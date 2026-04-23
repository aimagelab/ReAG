import os
import json
import urllib
import ujson
import faiss
import ast
import pandas as pd
from transformers import AutoModel, CLIPTokenizer, CLIPImageProcessor
import torch
from spacy.lang.en import English

from cropper_module.cropper import Cropper


def uniform_passages_of_sentences(paragraphs, n=100):
    spacy_model = English()
    spacy_model.add_pipe("sentencizer")
    text = paragraphs

    sentences = spacy_model(text).sents

    passages = []
    passage = []
    tokens_in_passage = 0
    for sent in sentences:
        if tokens_in_passage + len(sent) > n:
            if len(passage) > 0:
                passages.append(' '.join(passage))
                passage = [sent.text]
                tokens_in_passage = len(sent)
            else:
                passages.append(sent.text)
        else:
            passage.append(sent.text)
            tokens_in_passage += len(sent)

    if len(passage) > 0:
        passages.append(' '.join(passage))

    return passages


class Retriever:
    def __init__(self, args):
        self.args = args
        self.top_k = args.top_k

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.load_wiki_KB()

        if hasattr(args, "use_oracle") and args.use_oracle:
            return
        elif args.use_google_lens:
            google_lens_path = ... # Set the path to your Google Lens data CSV file (available at https://storage.googleapis.com/encyclopedic-vqa/lens_entities.csv)
            self.google_lens_data = pd.read_csv(google_lens_path)
        else:
            self.load_index()
            self.load_embedding_model()
            if args.crop_query_img:
                self.load_cropper()

    def load_cropper(self):
        if self.args.cropper_model_name and self.args.crop_query_img:
            self.cropper = Cropper(self.args)

    def load_index(self):
        print("Loading FAISS indices...")
        if self.args.img_index_path and self.args.img_index_json_path:
            self.img_index = faiss.read_index(self.args.img_index_path)
            with open(self.args.img_index_json_path, "r") as f:
                self.img_values = json.load(f)
        
        if not (hasattr(self, 'img_index') and hasattr(self, 'img_values')) and not (hasattr(self, 'text_index') and hasattr(self, 'text_values')):
            raise ValueError("You must provide either img_index_path and img_index_json_path or text_index_path and text_index_json_path")
        print("FAISS indices loaded.")
        
    def load_wiki_KB(self):
        print("Loading KB...")
        if self.args.dataset_name == "evqa" or self.args.dataset_name == "viquae":
            with open(self.args.wiki_KB, "r") as f:
                self.wikipedia = json.load(f)
        elif self.args.dataset_name == "infoseek":
            #self.wikipedia = load_wiki_documents(self.args.wiki_KB)
            with open(self.args.wiki_KB, "r") as f:
                self.wikipedia = ujson.load(f)
        print("KB loaded.")

    def load_embedding_model(self):
        print("Loading embedding model...")
        self.processor = CLIPImageProcessor.from_pretrained("openai/clip-vit-large-patch14")
        self.embedding_model = AutoModel.from_pretrained("BAAI/EVA-CLIP-8B", torch_dtype=torch.float16, trust_remote_code=True).to(self.device).eval()
        
        if hasattr(self.embedding_model, 'text_model'):
            del self.embedding_model.text_model
        if hasattr(self.embedding_model, 'text_projection'):
            del self.embedding_model.text_projection
        torch.cuda.empty_cache()
        print("Embedding model loaded.")

    def _retrieve_wiki_urls(self, query_embeds, top_k: int = 10, dataset_image_id=None, return_scores: bool = False):
        if self.args.use_google_lens:
            entity_urls = ast.literal_eval(self.google_lens_data[self.google_lens_data['dataset_image_id'] == dataset_image_id].lens_wiki_urls.iloc[0])
            entity_urls = [urllib.parse.quote(url, safe=":/") for url in entity_urls if url != ''][:top_k]
            if return_scores:
                return entity_urls, [None] * len(entity_urls)
            return entity_urls

        index = self.img_index
        values = self.img_values
        query_embeds = query_embeds.cpu().numpy().astype('float32')
        
        D, I = index.search(query_embeds, k=top_k)
        ids = I[0]
        raw_scores = D[0].tolist()

        if self.args.dataset_name == "evqa":
            results = [values[id][0] for id in ids]
        elif self.args.dataset_name == "infoseek":
            results = [values[id][0] for id in ids]
        elif self.args.dataset_name == "viquae":
            results = [values[id][0] for id in ids]

        if return_scores:
            return results, [float(s) for s in raw_scores]
        return results
    
    def retrieve(self, image_query, dataset_image_id=None, query=None):
        if self.args.use_google_lens and dataset_image_id:
            wiki_urls = self._retrieve_wiki_urls(None, top_k=self.args.top_k, dataset_image_id=dataset_image_id)
            section_texts = []
            for url in wiki_urls:
                if url in self.wikipedia:
                    section_texts.extend(self.wikipedia[url]['section_texts'])
            return section_texts, wiki_urls
        
        if self.args.crop_query_img:
            wiki_urls, scores = self._retrieve_passages(image_query, return_scores=True)

            image_query_cropped, _ = self.cropper.detect_and_crop(image_query, query)
            wiki_urls_cropped, scores_cropped = self._retrieve_passages(image_query_cropped, return_scores=True)

            combined_urls = wiki_urls + wiki_urls_cropped
            combined_scores = scores + scores_cropped
            url_score_dict = {}
            for url, score in zip(combined_urls, combined_scores):
                if url not in url_score_dict or score > url_score_dict[url]:
                    url_score_dict[url] = score
            sorted_urls = sorted(url_score_dict.items(), key=lambda item: item[1], reverse=True)
            wiki_urls = [url for url, score in sorted_urls[:self.args.top_k]]            
        else:
            wiki_urls = self._retrieve_passages(image_query)


        section_texts = []       
        docs_images = []
        if self.args.dataset_name == "evqa" or self.args.dataset_name == "viquae":
            for url in wiki_urls:
                section_texts.extend(self.wikipedia[url]['section_texts'])
                
        elif self.args.dataset_name == "infoseek":
            for url in wiki_urls:
                section_texts.extend(uniform_passages_of_sentences(self.wikipedia[url]['wikipedia_content'], n=300))

        return section_texts, docs_images, wiki_urls
            
    def _retrieve_passages(self, image_query, return_scores: bool = False):
        input_pixels = torch.from_numpy(self.processor(images=image_query).pixel_values[0])[None].to(dtype=torch.float16, device=self.embedding_model.device)
        with torch.no_grad():
            image_embeds = self.embedding_model.encode_image(input_pixels)
            image_embeds = image_embeds / image_embeds.norm(p=2, dim=-1, keepdim=True)

        if return_scores:
            return self._retrieve_wiki_urls(image_embeds, top_k=self.args.top_k, return_scores=True)
        else:
            return self._retrieve_wiki_urls(image_embeds, top_k=self.args.top_k)
   
    def get_wiki_page_passages(self, wiki_url):
        if self.args.dataset_name == "evqa":
            return self.wikipedia[wiki_url]['section_texts']
        elif self.args.dataset_name == "infoseek":
            return uniform_passages_of_sentences(self.wikipedia[wiki_url]['wikipedia_content'], n=300)

