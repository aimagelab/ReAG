#!/bin/bash
#SBATCH --job-name=compute_info_infoseek
#SBATCH --output=./logs/%A/%a.out
#SBATCH --error=./logs/%A/%a.err
#SBATCH --open-mode=truncate
#SBATCH --nodes=1
#SBATCH --gpus=0
#SBATCH --mem=20G
#SBATCH --partition=lrd_all_serial
#SBATCH --cpus-per-task=4
#SBATCH --account=your_account
#SBATCH --qos=boost_qos_dbg


cd ~/ReAG
source activate .venv

export PYTHONPATH=./src
input_path=$1

python src/retrieval_module/info_seek_eval/evaluation_infoseek.py \
    --adjust_score \
    --input_path $input_path


