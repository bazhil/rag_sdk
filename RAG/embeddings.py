from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from .config import settings


class EmbeddingModel:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self.model = None
        print(f"[EMBEDDINGS] EmbeddingModel initialized: {self.model_name}")
        
    def load(self):
        if self.model is None:
            print(f"[EMBEDDINGS] Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(f"[EMBEDDINGS] Model loaded successfully")
            
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        self.load()
        
        if isinstance(texts, str):
            print(f"[EMBEDDINGS] Encoding single text: {len(texts)} chars")
            embedding = self.model.encode(texts, convert_to_numpy=True)
            result = embedding.tolist()
            print(f"[EMBEDDINGS] Generated embedding: {len(result)} dimensions")
            return result
        else:
            print(f"[EMBEDDINGS] Encoding {len(texts)} texts")
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            result = embeddings.tolist()
            print(f"[EMBEDDINGS] Generated {len(result)} embeddings")
            return result
            
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        self.load()
        print(f"[EMBEDDINGS] Batch encoding {len(texts)} texts (batch_size={batch_size})")
        embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
        result = embeddings.tolist()
        print(f"[EMBEDDINGS] Generated {len(result)} embeddings")
        return result

