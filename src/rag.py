"""RAG: retrieval + generazione con Claude, ancorata ai regolamenti indicizzati."""
from dotenv import load_dotenv
load_dotenv()

import chromadb
from anthropic import Anthropic
from embeddings import SentenceTransformerEmbeddingFunction

import config
CHROMA_DIR = str(config.CHROMA_DIR)

COLLECTION_NAME = "endurance"
CLAUDE_MODEL = "claude-sonnet-5"

SYSTEM = """Sei un assistente tecnico esperto di endurance equestre FEI.
Rispondi basandoti ESCLUSIVAMENTE sugli estratti forniti.

Quando citi risultati di studi scientifici:
- Distingui sempre correlazione da causazione. Se lo studio osserva
  un'associazione, non affermare un rapporto causale.
- Segnala i limiti metodologici quando rilevanti: dimensione del
  campione, se è una singola sessione o uno studio longitudinale,
  se i risultati sono generalizzabili o specifici al contesto studiato.
- Non trasformare un risultato specifico in una raccomandazione pratica
  generale (es. "quindi allena il cavallo su X") a meno che lo studio
  stesso lo suggerisca esplicitamente.

Cita sempre l'articolo di regolamento o il paper di riferimento. Se
l'informazione non è nel contesto, dillo invece di inventare."""


_embedding_fn = None  # cache del modello, caricato una sola volta

def get_embedding_fn():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = SentenceTransformerEmbeddingFunction()
    return _embedding_fn


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    coll = client.get_collection(COLLECTION_NAME, embedding_function=get_embedding_fn())
    res = coll.query(query_texts=[query], n_results=top_k)
    return [{"text": d, "meta": m} for d, m in zip(res["documents"][0], res["metadatas"][0])]


def format_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[Articolo {c['meta'].get('articolo', '?')}]\n{c['text']}" for c in chunks
    )


def answer(query: str, verbose: bool = True) -> str:
    chunks = retrieve(query)
    if verbose:
        print("--- Chunk recuperati ---")
        for c in chunks:
            meta = c["meta"]
            if meta.get("tipo") == "regolamento":
                print(f"  [Regolamento] Articolo {meta.get('articolo')}")
            else:
                print(f"  [Paper] {meta.get('fonte')}")
        print()

    context = format_context(chunks)
    client = Anthropic()
    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=800, system=SYSTEM,
        messages=[{"role": "user", "content": f"CONTESTO:\n{context}\n\nDOMANDA: {query}"}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print('Uso: python src/rag.py "la tua domanda"')
        sys.exit(1)
    print("--- Risposta ---")
    print(answer(" ".join(sys.argv[1:])))