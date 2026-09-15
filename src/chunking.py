"""
Chunking consapevole della struttura del documento.
Per i regolamenti FEI usiamo l'articolo (800, 801, 816.6...) come unità
di senso: ogni articolo diventa un chunk coerente. Testato sui marcatori
di articolo a 3 cifre del regolamento endurance.
"""
import re


def chunk_regolamento(testo: str) -> list[dict]:
    """Spezza un regolamento FEI per articolo.
    Cerca i marcatori tipo '805.' o '816.6' a inizio riga seguiti da un titolo
    in maiuscolo, e taglia il testo tra un marcatore e il successivo."""
    # Marcatori: 3 cifre, eventuale sotto-numero, seguiti da testo che inizia in maiuscolo
    pattern = re.compile(r'(?m)^(\d{3}(?:\.\d+)*)\.?\s+([A-Z][^\n]{3,})')
    matches = list(pattern.finditer(testo))
    chunks = []
    for i, m in enumerate(matches):
        inizio = m.start()
        fine = matches[i + 1].start() if i + 1 < len(matches) else len(testo)
        corpo = testo[inizio:fine].strip()
        # Scarta blocchi troppo corti (spesso sono voci dell'indice, non articoli veri)
        if len(corpo) > 80 and "...." not in corpo:
            chunks.append({
                "articolo": m.group(1),
                "titolo": m.group(2).strip(),
                "text": corpo,
            })
    return chunks

def chunk_finestra(testo: str, size: int = 900, overlap: int = 150) -> list[dict]:
    """Chunking a finestra scorrevole per documenti senza struttura ad articoli (i paper)."""
    chunks, start = [], 0
    testo = testo.strip()
    while start < len(testo):
        corpo = testo[start:start + size].strip()
        if len(corpo) > 50:
            chunks.append({"text": corpo})
        start += size - overlap
    return chunks


if __name__ == "__main__":
    # Test rapido sul regolamento estratto
    from pathlib import Path
    testo = Path("data/extracted/endurance_rules_2026.txt").read_text(encoding="utf-8")
    chunks = chunk_regolamento(testo)
    print(f"Trovati {len(chunks)} chunk-articolo")
    # Mostra i primi 5 per controllo
    for c in chunks[:5]:
        print(f"  Art. {c['articolo']}: {c['titolo'][:50]} ({len(c['text'])} char)")
    # Cerca l'articolo 816 (vet gate / frequenza cardiaca) per verificare
    for c in chunks:
        if c["articolo"].startswith("816.6"):
            print(f"\n--- Articolo {c['articolo']} trovato ---")
            print(c["text"][:200])
            break