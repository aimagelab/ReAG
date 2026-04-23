import glob
import os
import random
import tqdm
import ujson
import spacy

nlp = spacy.load("en_core_web_sm")

def find_visual_entity(question):
    """
    Trova l'entità visiva (quella nell'immagine) nella domanda.
    In KB-VQA, è tipicamente l'entità con riferimenti deittici o 
    l'oggetto di una preposizione nella parte finale della domanda.
    """
    doc = nlp(question)
    
    # Pattern 1: "this/that" + noun (massima priorità)
    for chunk in doc.noun_chunks:
        if chunk[0].text.lower() in ["this", "these"]:
            return {
                "entity": chunk.text,
                "root": chunk.root.text,
                "pattern": "demonstrative"
            }
    for chunk in doc.noun_chunks:
        if chunk[0].text.lower() in ["the"]:
            return {
                "entity": chunk.text,
                "root": chunk.root.text,
                "pattern": "demonstrative"
            }
    for chunk in doc.noun_chunks:
        if chunk[0].text.lower() in ["that", "those"]:
            return {
                "entity": chunk.text,
                "root": chunk.root.text,
                "pattern": "demonstrative"
            }
    
    # Pattern 2: Oggetto di preposizione (of, by, in, from)
    prep_objects = []
    for token in doc:
        if token.dep_ == "pobj" and token.head.text in ["of", "by", "in", "from", "about"]:
            for chunk in doc.noun_chunks:
                if token in chunk:
                    prep_objects.append({
                        "entity": chunk.text,
                        "root": token.text,
                        "prep": token.head.text,
                        "pattern": "prepositional_object"
                    })
    
    # Prendi l'ultimo (più vicino alla fine della domanda)
    if prep_objects:
        return prep_objects[-1]
    
    # Pattern 3: Ultimo sostantivo (fallback debole)
    noun_chunks = list(doc.noun_chunks)
    if noun_chunks:
        last_chunk = noun_chunks[-1]
        return {
            "entity": last_chunk.text,
            "root": last_chunk.root.text,
            "pattern": "last_noun"
        }
    
    return None
