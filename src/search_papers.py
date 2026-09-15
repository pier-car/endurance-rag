"""
Cerca automaticamente paper su PMC per uno o più termini, usando ESearch
(API ufficiale NCBI per liste di risultati — parte delle stesse E-utilities
del BioC che già usi in fetch_papers.py).

Fonte: https://www.ncbi.nlm.nih.gov/books/NBK25499/
"""
import time
import requests

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


def cerca_pmcid(termine: str, max_risultati: int = 10) -> list[str]:
    """Cerca su PMC, filtrando fin da subito al solo Open Access Subset —
    evita di trovare PMCID che poi il BioC non potrà servire."""
    query = f"{termine} AND open_access[filter]"
    params = {
        "db": "pmc",
        "term": query,
        "retmax": max_risultati,
        "retmode": "json",
        "tool": "EnduranceRAG-progetto-studio",
        "email": "il-tuo-indirizzo@email.com",
    }
    resp = requests.get(ESEARCH_URL, params=params, timeout=30)
    resp.raise_for_status()
    id_list = resp.json().get("esearchresult", {}).get("idlist", [])
    return [f"PMC{i}" for i in id_list]


if __name__ == "__main__":
    termini = [
        "endurance horse heart rate recovery",
        "endurance horse elimination lameness metabolic",
        "equine exercise physiology endurance racing",
        "horse vetgate cardiac recovery index",
    ]
    tutti_pmcid = []
    for t in termini:
        print(f"Cerco: '{t}'")
        trovati = cerca_pmcid(t, max_risultati=8)
        print(f"  Trovati {len(trovati)}: {trovati}")
        tutti_pmcid.extend(trovati)
        time.sleep(1)  # rispetto del limite NCBI: max 3 richieste/sec senza api key

    pmcid_unici = list(dict.fromkeys(tutti_pmcid))  # deduplica mantenendo l'ordine
    print(f"\nTotale PMCID unici trovati: {len(pmcid_unici)}")
    print(pmcid_unici)