"""
Percorsi centralizzati, ancorati alla posizione di questo file — non alla
cartella da cui lanci lo script. Così funziona sia con 'python src/rag.py'
dalla radice, sia con 'uvicorn api:app' da dentro src/, senza sorprese.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # la cartella endurance_rag
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdf"
EXTRACTED_DIR = DATA_DIR / "extracted"
XML_DIR = DATA_DIR / "xml"
CHROMA_DIR = BASE_DIR / "chroma_db"