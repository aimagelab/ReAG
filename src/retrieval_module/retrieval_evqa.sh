#!/bin/bash
#SBATCH --job-name=ency-vqa_retrieval
#SBATCH --partition=your_partition
#SBATCH --account=your_account
#SBATCH --open-mode=truncate
#SBATCH --gpus=1
#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --array=0-3
#SBATCH --mem=100GB
#SBATCH --output=./logs/%A/%a.out
#SBATCH --error=./logs/%A/%a.err

module load cuda/12.6

# Use the current directory or a relative path instead of an absolute one
cd ~/ReAG/
source .venv/bin/activate

export PYTHONPATH="./src"

export PART=${SLURM_ARRAY_TASK_ID}
export TOTAL_PART=${SLURM_ARRAY_TASK_MAX}

export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1


srun --cpu_bind=none --exclusive -u python src/retrieval_module/retrieval.py \
    --query_path "path_to_queries" \
    --output_root ./results \
    --img_index_path "path_to_img_index" \
    --img_index_json_path "path_to_img_index_json" \
    --wiki_KB "path_to_evqa_wiki_kb" \
    --dataset_name "evqa" \
    \
    --model_name "aimagelab/ReAG-3B" \
    --all_filtered \
    --force_reasoning \
    --extract_reasoning \
    \
    --experiment_type "with_retrieval" \
    --top_k 20 \
    \
    \
    --crop_query_img \
    \
    --critic_model_name "aimagelab/ReAG-Critic" \
    --eval_passages \
    --yes_prob_thr 0.1 \
    --eval_passages_batch_size 1 \
    \
    
    # --use_google_lens \
    # --use_oracle \
    # --use_oracle_passage \
        
    # --few_shots \
    