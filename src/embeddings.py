"""
Embedding semantico via sentence-transformers. Gira su CPU senza problemi:
il modello scelto (~470MB) è pensato per essere leggero.
"""
from sentence_transformers import SentenceTransformer
from chromadb.api.types import EmbeddingFunction


class SentenceTransformerEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self.model.encode(
            input, convert_to_numpy=True, show_progress_bar=False
        ).tolist()

    def name(self) -> str:
        return "st-multilingual-minilm-l12-v2"