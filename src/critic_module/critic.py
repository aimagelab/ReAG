import tqdm
from typing import List
import pandas as pd
import torch
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

import retrieval_module.prompts as prompts

class CriticModel:
    def __init__(self, args = None):
        self.args = args
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("Loading critic model...")
        model_name = args.critic_model_name
        self.processor = AutoProcessor.from_pretrained(
            model_name,
            model_max_length=args.model_max_length,
            padding_side="left",
            use_fast=True,
            min_pixels=args.min_pixels,
            max_pixels=args.max_pixels
        )
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            attn_implementation="flash_attention_2",
            torch_dtype=torch.bfloat16,
            device_map=None,
        ).to(self.device)
        
        self.model.model.config.use_cache = True
        self.model.model.language_model.config.use_cache = True
        self.model.eval()
        
        print("Critic model loaded.")
        
    @torch.inference_mode()
    def critique(self, inputs):

        outputs = self.model(**inputs)
        output_logits = outputs[0][:, -1, :]
        output_logits = output_logits.to(dtype=torch.float32)

        T = 1
        output_logits = output_logits / T

        # Find 'yes' or 'no' token ids
        yes_token_id = self.processor.tokenizer.convert_tokens_to_ids('Yes')
        no_token_id = self.processor.tokenizer.convert_tokens_to_ids('No')
        
        results = []
        for out_logits in output_logits:
            probs = torch.softmax(out_logits, dim=-1)
            
            yes_prob = probs[yes_token_id].item()  # .item() per spostare su CPU
            no_prob = probs[no_token_id].item()
            
            answer = True if yes_prob > self.args.yes_prob_thr else False
            
            out = {
                'answer': answer,
                'probs': {
                    "yes": yes_prob, 
                    "no": no_prob
                },
            }
            results.append(out)
        
        return results
    

    def passages_relevance(self, passages: List[str], questions: List[str], images) -> bool:
        messages_list = [
            [
                {
                    'role': 'system',
                    'content': [
                        {'type': 'text', 'text': prompts.RELEVANCY_EVAL_SYSTEM_PROMPT}
                    ]
                },
                {
                    'role': 'user',
                    'content': [
                        {'type': 'image'},
                        {'type': 'text', 'text': prompts.SECTION_EVAL_USER_TEMPLATE.format(question=question, passage=passage)}
                    ]
                }
            ]
            for question, passage in zip(questions, passages)
        ]

        texts = self.processor.apply_chat_template(
            messages_list, tokenize=False, add_generation_prompt=True
        )

        inputs = self.processor(
            images=images, 
            text=texts, 
            return_tensors="pt", 
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        critiques = self.critique(inputs)
        
        return critiques
    
