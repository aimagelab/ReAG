import webdataset as wds
from braceexpand import braceexpand
import re
import ast
import urllib
import ujson
import tqdm
import retrieval_module.prompts as prompts
import os
import pandas as pd
from PIL import Image
import torch

import json
import csv

class DatasetEVQA(torch.utils.data.Dataset):
    def __init__(self, args):
        super().__init__()
        self.args = args
        print(f'Loading from {args.query_path}...')
        with open(args.query_path, 'r') as f:
            self.data = ujson.load(f)
        
        print(f'Loading completed...')
        self.start_idx = 0

    def split(self, start_idx, end_idx):
        self.start_idx = start_idx
        
        self.data = self.data[start_idx:end_idx]

    def __getitem__(self, idx):
        sample = self.data[idx]

        image_path = ... # Set the image path based on your dataset structure
        sample['image_path'] = image_path

        if os.path.isabs(image_path):
            image_query = Image.open(image_path).convert('RGB')
        else:
            # Black Image
            image_query = Image.new('RGB', (224, 224), color=(0, 0, 0))
            print(f"[!] Warning: image path {image_path} not found. Using black image as placeholder.")

        sample['image_query'] = image_query

        return sample
    
    def __len__(self):
        return len(self.data)

class DatasetInfoseek(torch.utils.data.Dataset):
    def __init__(self, args):
        super().__init__()

        self.args = args
        print(f'Loading from {args.query_path}...')
        with open(args.query_path, 'r') as f:
            self.data = [json.loads(line) for line in f]
        print(f'Loading completed...')

    
    def split(self, start_idx, end_idx):
        self.data = self.data[start_idx:end_idx]

    def __getitem__(self, idx):
        sample = self.data[idx]
            
        image_path = ... # Set the image path based on your dataset structure
        image = Image.open(image_path)

        sample['image_query'] = image
    
        return sample
    
    def __len__(self):
        return len(self.data)

class ViquaeDataset(torch.utils.data.Dataset):
    def __init__(self, args):
        super().__init__()
        self.args = args

        print(f'Loading from {args.query_path}...')
        with open(args.query_path, 'r') as f:
            self.data = [json.loads(line) for line in f]
        print('Loading completed')

    def split(self, start_idx, end_idx):
        self.data = self.data[start_idx:end_idx]

    def __getitem__(self, idx):
        sample = self.data[idx]
        image_path = ... # Set the image path based on your dataset structure
        sample['image_path'] = image_path
        if os.path.exists(image_path):
            image_query = Image.open(image_path).convert('RGB')
        else:
            # Black Image
            image_query = Image.new('RGB', (224, 224), color=(0, 0, 0))
            print(f"[!] Warning: image path {image_path} not found. Using black image as placeholder.")

        sample['image_query'] = image_query
        sample['question'] = sample['original_question']
        sample['wikipedia_url'] = sample['url']
        sample['data_id'] = sample['id']
        sample['reference'] = sample['output']['answer']

        return sample
    
    def __len__(self):
        return len(self.data)

def calculate_splits(dataset_len):
    """
    Calculate the start and end indices for splitting the dataset with job arrays.
    """
    part = int(os.environ.get('PART', '0'))
    total_part_env = os.environ.get('TOTAL_PART', None)
    total_part = (int(total_part_env) + 1) if total_part_env is not None else 1
    print(f'Computing split {part} of the dataset... (total_part={total_part})')
    slicing = dataset_len // total_part
    if (part+1) == total_part:
        start_idx = slicing * part
        end_idx = dataset_len
    else:
        start_idx = slicing * part
        end_idx = slicing * part + slicing
    print(f'Processing Element from {start_idx} to {end_idx}...')

    return start_idx, end_idx

def get_query_dataset(args):
    if args.dataset_name == 'evqa':
        dataset = DatasetEVQA(args)
    elif args.dataset_name == 'viquae':
        dataset = ViquaeDataset(args)
    elif args.dataset_name == 'infoseek':
        dataset = DatasetInfoseek(args)
        
    start_idx, end_idx = calculate_splits(len(dataset))
    dataset.split(start_idx, end_idx)
        
    return dataset, start_idx, end_idx

def load_csv_to_dict(csv_path):
    mapping = {}
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            key = row[0].strip()
            value = row[1].strip() if len(row) > 1 else ''
            mapping[key] = value
    return mapping


