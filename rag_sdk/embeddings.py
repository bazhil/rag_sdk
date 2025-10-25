from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from .config import settings


class EmbeddingModel:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self.model = None
        
    def load(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
            
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        self.load()
        
        if isinstance(texts, str):
            embedding = self.model.encode(texts, convert_to_numpy=True)
            return embedding.tolist()
        else:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
            
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        self.load()
        embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True)
        return embeddings.tolist()

