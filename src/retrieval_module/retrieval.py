import subprocess
import time
import webdataset as wds
import re
import ujson
import tqdm
import os
import pandas as pd
from PIL import Image
import torch
import argparse

from transformers import AutoProcessor, AutoModelForImageTextToText

import retrieval_module.prompts as prompts
from retrieval_module.retriever import Retriever, uniform_passages_of_sentences
from retrieval_module.data import *
from critic_module.critic import CriticModel


def get_args():
    parser = argparse.ArgumentParser(description="RAG inference")

    parser.add_argument("--img_index_path", type=str, required=False)
    parser.add_argument("--img_index_json_path", type=str, required=False)
    parser.add_argument("--wiki_KB", type=str, required=False)
    parser.add_argument("--query_path", type=str, required=True)
    parser.add_argument("--model_name", type=str, default="aimagelab/ReAG-3B")
    parser.add_argument("--dataset_name", type=str, choices=["evqa", "infoseek", "viquae"], required=True)
    parser.add_argument("--output_root", type=str, default="./results")

    parser.add_argument("--experiment_type", type=str, choices=["with_retrieval", "no_retrieval"], default="with_retrieval")

    parser.add_argument("--top_k", type=int, default=1, help="Number of top documents to retrieve")

    parser.add_argument('--use_google_lens', action='store_true')
    parser.add_argument('--use_oracle', action='store_true')
    parser.add_argument('--use_oracle_passage', action='store_true')

    parser.add_argument('--only_question', action='store_true') # For no retrieval setting, if true, use only question without any prompt
    parser.add_argument("--all_filtered", action='store_true') # If true, when no filtered retrieval, use only question without any prompt

    # Passages Evaluation args
    parser.add_argument("--critic_model_name", type=str, default="aimagelab/ReAG-Critic", help="Model name or path for the critic model")
    parser.add_argument('--eval_passages', action='store_true')
    parser.add_argument('--eval_passages_batch_size', type=int, default=5, help="Batch size for passages evaluation")
    parser.add_argument("--yes_prob_thr", type=float, default=0.5, help="Threshold for yes probability in passage relevance evaluation")

    # Reasoning
    parser.add_argument("--extract_reasoning", action='store_true')
    parser.add_argument("--force_reasoning", action='store_true')
    parser.add_argument("--strict_parsing", action='store_true')

    parser.add_argument("--short_prompt", action='store_true')
    parser.add_argument("--max_new_tokens", type=int, default=4096)
    parser.add_argument('--model_max_length', type=int, default=16384)
    parser.add_argument('--min_pixels', type=int, default=3136)
    parser.add_argument('--max_pixels', type=int, default=301056)
    parser.add_argument('--temperature', type=float, default=None)
    parser.add_argument('--repetition_penalty', type=float, default=None)
    parser.add_argument('--top_p', type=float, default=None)
    parser.add_argument('--top_k_sampling', type=int, default=None)
    parser.add_argument('--min_p', type=float, default=None)

    parser.add_argument('--cropper_model_name', type=str, default="IDEA-Research/grounding-dino-base",)
    parser.add_argument('--crop_query_img', action='store_true')

    parser.add_argument('--few_shots', action='store_true', help="Use few-shot prompting for infoseek dataset")    

    args = parser.parse_args()

    
    return args

class InferenceModel:
    def __init__(self, args):
        self.args = args

        print("Loading qwen model...")
        self.processor = AutoProcessor.from_pretrained(
            args.model_name,
            model_max_length=args.model_max_length,
            padding_side="left",
            use_fast=True,
            min_pixels=args.min_pixels,
            max_pixels=args.max_pixels
        )
        self.qwen_model = AutoModelForImageTextToText.from_pretrained(
            args.model_name,
            attn_implementation="flash_attention_2",
            torch_dtype=torch.bfloat16,
            device_map="balanced",
        )
        
        self.qwen_model.model.config.use_cache = True
        self.qwen_model.model.language_model.config.use_cache = True
        self.qwen_model.eval()

        print("Qwen model loaded.")

    @torch.inference_mode() 
    def generate(self, question, image_query):
        messages = []
        if self.args.extract_reasoning:
            messages.append(
                {
                    'role': 'system',
                    'content': [
                        {'type': 'text', 'text': prompts.SYSTEM_PROMPT_REASONING}
                    ]
                }
            )
        
        if self.args.short_prompt:
            question += '\nGive a short answer.\nShort answer: '
        
        messages.append(
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type":"text", "text": question}
                ]
            }
        )

        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        if self.args.force_reasoning:
            text = text + "<think>"

        inputs = self.processor(
            text = [text],
            images=[image_query],
            videos=None,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(self.qwen_model.device)

        gen_kwargs = {}
        if self.args.temperature is not None:
            gen_kwargs['temperature'] = self.args.temperature
        if self.args.top_p is not None:
            gen_kwargs['top_p'] = self.args.top_p
        if self.args.top_k_sampling is not None:
            gen_kwargs['top_k'] = self.args.top_k_sampling
        if self.args.repetition_penalty is not None:
            gen_kwargs['repetition_penalty'] = self.args.repetition_penalty
        if self.args.min_p is not None:
            gen_kwargs['min_p'] = self.args.min_p

        generated_ids = self.qwen_model.generate(
            **inputs, 
            max_new_tokens=self.args.max_new_tokens, 
            stop_strings=["</answer>"] if self.args.extract_reasoning else None,
            tokenizer=self.processor.tokenizer,
            use_cache=True,
            **gen_kwargs
        )
        # Subtract the len of <think> if reasoning is extracted, use tokenizer to be sure of how manuy tokens it is (should be 3)
        in_ids_lengths = [len(in_ids) - (len(self.processor.tokenizer("<think>").input_ids) if self.args.force_reasoning else 0) for in_ids in inputs.input_ids]

        generated_ids_trimmed = [
            out_ids[in_ids_len :] for in_ids, out_ids, in_ids_len in zip(inputs.input_ids, generated_ids, in_ids_lengths)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        return output_text

def get_output_root(args):
    root = args.output_root
    os.makedirs(root, exist_ok=True)

    model_name = args.model_name.split("/")[-1]
    
    if args.temperature is not None:
        model_name += f"_temp{str(args.temperature).replace('.', '')}"

    answer_root = f"{args.dataset_name}__{model_name}__{args.experiment_type}"

    if args.experiment_type == "with_retrieval":
        if args.use_google_lens:
            answer_root += f"__google_lens"
        elif args.use_oracle:
            if args.use_oracle_passage:
                answer_root += f"__oracle_page"    
            else:
                answer_root += f"__oracle"

        answer_root += f"_top{args.top_k}"

    if args.eval_passages:
        answer_root += f"__passages_eval_thr_{str(args.yes_prob_thr).replace('.', '')}"

    if args.extract_reasoning:
        answer_root += "__reasoning"
        if args.force_reasoning:
            answer_root += "_forced"
        if args.strict_parsing:
            answer_root += "_strict_parse"

    if args.short_prompt:
        answer_root += '__short'

    if args.only_question:
        answer_root += '__only_question'
    
    if args.all_filtered:
        answer_root += '__all_filtered'

    if args.crop_query_img:
        answer_root += f"__cropfixed"

    if args.few_shots:
        answer_root += f"__fewshots"

    answer_root = os.path.join(root, answer_root)
    os.makedirs(answer_root, exist_ok=True)

    print(f"Outputs will be saved to: {answer_root}")

    return answer_root

def sbatch_eval(args, answer_root):
    if os.environ.get("DEBUG", "0") == "1":
        print("DEBUG env var not set to 1; skipping sbatch submission.")
        return

    # Submit evaluation job via sbatch, pass answer_root as first argument to the submit script
    try:
        # Decide whether to submit: only submit when running as a single Slurm job
        # or when running as array task 0. If not running under Slurm, submit as well.
        slurm_job_id = os.environ.get("SLURM_JOB_ID")
        slurm_array_job_id = os.environ.get("SLURM_ARRAY_JOB_ID")
        slurm_array_task_id = os.environ.get("SLURM_ARRAY_TASK_ID")
        should_submit = False

        if slurm_job_id:
            # Under Slurm: submit only for single job or array task 0
            if slurm_array_task_id is None or str(slurm_array_task_id) == "0":
                should_submit = True
                print(f"Will submit evaluation job (SLURM_JOB_ID={slurm_job_id}, SLURM_ARRAY_JOB_ID={slurm_array_job_id}, SLURM_ARRAY_TASK_ID={slurm_array_task_id})")
            else:
                print(f"Skipping evaluation submission for array task {slurm_array_task_id} (only task 0 should submit).")
        else:
            # Not running under Slurm: submit by default
            should_submit = True
            print("Not running under Slurm; submitting evaluation job without dependency.")

        if should_submit:
            cmd = ["sbatch"]
            if args.dataset_name == "evqa":
                job_name = "evqa_eval_" + os.path.basename(answer_root)
                cmd.extend(["--job-name", job_name])
                script_path = "./src/retrieval_module/evqa_eval/submit_job.sh"
            elif args.dataset_name == "infoseek":
                job_name = "infoseek_eval_" + os.path.basename(answer_root)
                cmd.extend(["--job-name", job_name])
                script_path = "./src/retrieval_module/info_seek_eval/eval.sh"
            if slurm_job_id and (slurm_array_task_id is None or str(slurm_array_task_id) == "0"):
                # Use SLURM_ARRAY_JOB_ID for array jobs, SLURM_JOB_ID for single jobs
                job_id_for_dependency = slurm_array_job_id if slurm_array_job_id else slurm_job_id
                dependency = f"--dependency=afterok:{job_id_for_dependency}_*"
                cmd.append(dependency)
                print(f"Adding dependency on job id: {job_id_for_dependency}_*")
            
            cmd.extend([script_path, answer_root])
            print(f"Submitting evaluation job: {' '.join(cmd)}")
            sbatch = subprocess.run(cmd, capture_output=True, text=True)
            if sbatch.returncode == 0:
                out = sbatch.stdout.strip()
                print(f"sbatch output: {out}")
                m = re.search(r"Submitted batch job (\d+)", out)
                if m:
                    print(f"Submitted job id: {m.group(1)}")
            else:
                print(f"sbatch failed (code {sbatch.returncode}). stderr: {sbatch.stderr}")
        else:
            print("Evaluation submission skipped.")
    except Exception as e:
        print(f"Error submitting sbatch job: {e}")

def main():
    args = get_args()

    answer_root = get_output_root(args)

    try:
        sbatch_eval(args, answer_root)
    except Exception as e:
        print(f"Error during sbatch evaluation submission: {e}")

    # Print args
    print("Arguments:")
    for arg in vars(args):
        print(f"{arg}: {getattr(args, arg)}")
    print("\n\n")
    
    dataset, start_idx, end_idx = get_query_dataset(args)
    len_dataset = end_idx - start_idx
    
    model = InferenceModel(args)
    retriever = Retriever(args)
    if args.eval_passages:
        critic_model = CriticModel(args=args)

    saved_filtered_sections = {}
    responses = []
    reasoning_trace_list = []
    FORMAT_RESPECTED = 0
    retrieval_latencys = []
    filtering_latencys = []
    generation_latencys = []
    for i, sample in tqdm.tqdm(enumerate(dataset), desc=f"{args.dataset_name} Retrieval", total=len_dataset):
        filtered_sections = []
        docs_images = []
        wiki_urls = []
        query = sample['question']
        image_query = sample['image_query']

        # Get evidence_section
        evidence_section = None
        if 'retrieval' in sample and 'evidence_section_id' in sample: # evqa data_loader
            try:
                evidence_section = sample['retrieval'][0]['section_texts'][int(sample['evidence_section_id'])]
            except (KeyError, IndexError, ValueError):
                evidence_section = None

        evidence_in_context = False
        
        try:
            if args.experiment_type == "no_retrieval":
                if args.only_question:
                    question = query
                else:
                    question = prompts.VQA_PROMPT.format(question=query, answer="")
            else:
                start = time.time()
                if args.use_google_lens:
                    dataset_image_id = sample['dataset_image_ids']
                    sections, wiki_urls = retriever.retrieve(image_query, dataset_image_id=dataset_image_id)
                    docs_images = []
                elif args.use_oracle:
                    if args.dataset_name == 'evqa':
                        if args.use_oracle_passage and evidence_section is not None:
                            sections = [evidence_section]
                        else:
                            evidence_wiki_url = sample['wikipedia_url']
                            wiki_urls = evidence_wiki_url.split('|')
                            sections = []
                            for wiki_url in wiki_urls:
                                sections.extend(retriever.get_wiki_page_passages(wiki_url))
                        
                    else:
                        sections = retriever.get_wiki_page_passages(sample['passage_id'])
                else:
                    sections, docs_images, _ = retriever.retrieve(image_query, query=query)
                end = time.time()
                retrieval_latency = end - start
                retrieval_latencys.append(retrieval_latency)

                start = time.time()
                if args.eval_passages:
                    filtered_sections = []
                    yes_probs = []
                    # Batch evaluation
                    for j in range(0, len(sections), args.eval_passages_batch_size):
                        passages = sections[j:j+args.eval_passages_batch_size]
                        questions = [query] * len(passages)
                        images = [image_query] * len(passages)
                        results = critic_model.passages_relevance(passages, questions, images)
                        for k, result in enumerate(results):
                            if result['answer']: # Filtered opver the yes_prob threshold
                                filtered_sections.append(passages[k])
                                yes_probs.append(result['probs']['yes'])

                else:
                    filtered_sections = sections

                end = time.time()
                filtering_latency = end - start
                filtering_latencys.append(filtering_latency)

                saved_filtered_sections[sample['unique_id'] if args.dataset_name == "evqa" else sample['data_id']] = {
                    "filtered_sections": filtered_sections.copy(),
                    "sections": sections.copy(),
                }

                if evidence_section is not None:
                    if evidence_section in filtered_sections:
                        evidence_in_context = True # Checks if the evidence section was retrieved and included in the filtered sections

                for j, section in enumerate(filtered_sections):
                    filtered_sections[j] = '<paragraph>' + section + "</paragraph>"


                if len(filtered_sections) == 0 and args.all_filtered:
                        question = query
                        context = ""
                else:
                    context = "\n\n\n".join(filtered_sections) + '.'
                    question = prompts.CONTEXT_VQA_PROMPT_training.format(question=query, context=context)


            if args.dataset_name == "infoseek" and args.few_shots: # add few-shots
                question = prompts.INFOSEEK_FEW_SHOTS + '\n\n\n' + question
            elif args.dataset_name == "evqa" and args.few_shots:
                question = prompts.EVQA_FEW_SHOTS + '\n\n' + question
            
            start = time.time()
            output = model.generate(question, image_query)[0]     
            end = time.time()
            generation_latency = end - start
            generation_latencys.append(generation_latency)

            if args.extract_reasoning:
                pred_match = re.search(r'<answer>(.*?)</answer>', output) # lowercase
                thinking_match = re.search(r'<think>(.*?)</think>', output)
                reasoning_trace = thinking_match.group(1).strip() if thinking_match else ""
                reasoning_trace_list.append({
                    "data_id": sample['unique_id'] if args.dataset_name == "evqa" else sample['data_id'],
                    "question": query,
                    "reasoning_trace": reasoning_trace,
                    "output": output,
                    "evidence_in_context": evidence_in_context
                })
            
                if pred_match:
                    output = pred_match.group(1)
                    FORMAT_RESPECTED += 1
                elif args.strict_parsing:
                    output = "Error: parsing"
                elif "<answer>" in output:
                    output = output[output.index("<answer>") + len("<answer>"): ]
                elif "</think>" in output:
                    output = output[output.index("</think>") + len("</think>"): ]

                output = output.replace('<answer>', '').replace('</answer>', '').replace("<think>", '').replace("</think>", '').strip()

        except Exception as e:
            data_id = sample['unique_id'] if args.dataset_name == "evqa" else sample['data_id']
            print(f"Error processing sample {i} with data_id: {data_id}{e}")
            output = "Error"
        if args.dataset_name == "evqa":
            reference_list = sample['answer']
            if isinstance(reference_list, str):
                reference_list = reference_list.split('|')
            responses.append({
                "data_id": sample['unique_id'],
                "unique_id": sample['unique_id'],
                "question": sample['question'],
                "image_path": sample['image_path'] if 'image_path' in sample else "",
                "answers": output,
                "prediction": output,
                "reference": reference_list,
                "question_type": sample['question_type'],
                "evidence_in_context": evidence_in_context,
                "num_passages": len(filtered_sections) if args.experiment_type == "with_retrieval" else 0,
            })
        elif args.dataset_name == "infoseek":
            responses.append({
                "data_id": sample['data_id'] if 'data_id' in sample else sample['unique_id'],
                "unique_id": sample['data_id'] if 'data_id' in sample else sample['unique_id'],
                "question": sample['question'],
                "image_path": sample['image_path'] if 'image_path' in sample else "",
                "answers": output,
                "prediction": output,
                "reference": sample['answer'] if 'answer' in sample else [],
                "question_type": sample.get('question_type', 'N/A'),
                "evidence_in_context": evidence_in_context,
                "num_passages": len(filtered_sections) if args.experiment_type == "with_retrieval" else 0,
            })
        elif args.dataset_name == "viquae":
            responses.append({
                "data_id": sample['data_id'],
                "unique_id": sample['data_id'],
                "question": sample['question'],
                "image_path": sample['image_path'] if 'image_path' in sample else "",
                "answers": output,
                "prediction": output,
                "reference": sample['reference'],
                "evidence_in_context": evidence_in_context,
                "num_passages": len(filtered_sections) if args.experiment_type == "with_retrieval" else 0,
            })

    os.makedirs(answer_root, exist_ok=True)
    part = int(os.environ.get('PART', '0'))
    answers_file = os.path.join(answer_root, f'split_{part}.json')
    print("Answer file:", answers_file)

    with open(answers_file, "w") as f:
        f.write(ujson.dumps(responses))
    
    if args.extract_reasoning:
        reasoning_file = os.path.join(answer_root, f'reasoning_traces__split_{part}.json')
        with open(reasoning_file, "w") as f:
            f.write(ujson.dumps(reasoning_trace_list))

        print(f"Reasoning traces saved to {reasoning_file}. FORMAT_RESPECTED: {FORMAT_RESPECTED}/{len_dataset}")

    latency_dict = {
        "retrieval_latency_avg": sum(retrieval_latencys) / len(retrieval_latencys) if len(retrieval_latencys) > 0 else 0,
        "filtering_latency_avg": sum(filtering_latencys) / len(filtering_latencys) if len(filtering_latencys) > 0 else 0,
        "generation_latency_avg": sum(generation_latencys) / len(generation_latencys) if len(generation_latencys) > 0 else 0,
    }
    latency_stats_file = os.path.join(answer_root, f'latency_stats__split_{part}.json')
    with open(latency_stats_file, "w") as f:
        f.write(ujson.dumps(latency_dict))
    print(f"Latency stats saved to {latency_stats_file}.")

    filtered_sections_file = os.path.join(answer_root, f'filtered_sections__split_{part}.json')
    with open(filtered_sections_file, "w") as f:
        f.write(ujson.dumps(saved_filtered_sections))
    print(f"Filtered sections saved to {filtered_sections_file}.")

    

if __name__ == "__main__":
    main()
