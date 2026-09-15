"""
Ingestion: legge i testi estratti, li spezza per articolo (o a finestra per
documenti senza struttura ad articoli), e indicizza tutto in ChromaDB con
embedding semantici.
"""
from pathlib import Path
import chromadb

from chunking import chunk_regolamento, chunk_finestra
from embeddings import SentenceTransformerEmbeddingFunction

import config
EXTRACTED_DIR = config.EXTRACTED_DIR
CHROMA_DIR = str(config.CHROMA_DIR)
COLLECTION_NAME = "endurance"


def carica_chunks() -> list[dict]:
    records = []
    id_visti = {}

    for txt_path in sorted(config.EXTRACTED_DIR.glob("*.txt")):
        testo = txt_path.read_text(encoding="utf-8")
        nome = txt_path.stem.lower()

        if "rule" in nome or "regulation" in nome:
            chunks_raw = chunk_regolamento(testo)
            tipo = "regolamento"
            chiavi = [c["articolo"] for c in chunks_raw]
        else:
            chunks_raw = chunk_finestra(testo)
            tipo = "paper"
            chiavi = [str(i) for i in range(len(chunks_raw))]

        for c, chiave in zip(chunks_raw, chiavi):
            id_base = f"{txt_path.stem}_{chiave}"

            if id_base in id_visti:
                id_visti[id_base] += 1
                id_finale = f"{id_base}_dup{id_visti[id_base]}"
            else:
                id_visti[id_base] = 0
                id_finale = id_base

            meta = {"fonte": txt_path.name, "tipo": tipo}
            if tipo == "regolamento":
                meta["articolo"] = chiave

            records.append({"id": id_finale, "text": c["text"], "meta": meta})

    return records


if __name__ == "__main__":
    print("Carico e chunk-izzo i documenti...")
    records = carica_chunks()
    print(f"{len(records)} chunk pronti per l'indicizzazione.")

    print("Inizializzo il modello di embedding (primo avvio: scarica ~470MB)...")
    embedding_fn = SentenceTransformerEmbeddingFunction()

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)
    collection = client.create_collection(COLLECTION_NAME, embedding_function=embedding_fn)

    print("Indicizzo (può richiedere qualche decina di secondi su CPU)...")
    collection.add(
        ids=[r["id"] for r in records],
        documents=[r["text"] for r in records],
        metadatas=[r["meta"] for r in records],
    )
    print(f"Fatto. Collection '{COLLECTION_NAME}' pronta con {collection.count()} chunk.")
    
    