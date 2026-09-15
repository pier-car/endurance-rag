"""Valutazione del retrieval con un eval set di dominio costruito a mano."""
from rag import retrieve

# (domanda, prefisso dell'articolo atteso — basta che l'id inizi con questo)
EVAL_SET = [
    ("Qual è la frequenza cardiaca massima al vet gate?", "816.6"),
    ("Quanti punti penalità per disqualificazione per presentazione tardiva?", "864"),
    ("Qual è il peso minimo per un atleta senior in CEI 3*?", "805"),
    ("Qual è l'età minima del cavallo per CEI 2*?", "827"),
    ("Quanti loop minimi servono per un percorso di 100-119 km?", "814.4"),
    ("Dopo quanti punti penalità un atleta viene sospeso?", "866"),
    ("Quanto dura il periodo obbligatorio fuori competizione dopo una gara fino a 54 km?", "839.1"),
    ("Quante persone possono accompagnare il cavallo nella vetting area?", "816.4"),
]


def recall_at_k(k: int = 5) -> float:
    hits = 0
    for domanda, atteso in EVAL_SET:
        chunks = retrieve(domanda, top_k=k)
        articoli = [c["meta"].get("articolo", "") for c in chunks]
        if any(a.startswith(atteso) for a in articoli):
            hits += 1
        else:
            print(f"MISS: '{domanda}' -> atteso {atteso}, trovato {articoli}")
    return hits / len(EVAL_SET)


if __name__ == "__main__":
    for k in [1, 3, 5]:
        print(f"Recall@{k} = {recall_at_k(k):.2f}")