"""
Scarica il testo completo di paper scientifici da PMC Open Access via BioC.
Versione con pausa piu' ampia e retry automatico sul rate limit (429).
"""
import time
import requests
import config

PMCIDS = [
    "PMC13542711", "PMC13531787", "PMC13532979", "PMC13532992", "PMC13395041",
    "PMC13506835", "PMC13517099", "PMC13516385", "PMC13565396", "PMC13508917",
    "PMC13447936", "PMC13402110", "PMC13364340", "PMC13244195", "PMC12984839",
    "PMC12866905", "PMC13499858", "PMC13495423", "PMC13489413", "PMC13465511",
    "PMC13467334", "PMC13447870", "PMC13447954", "PMC13447926", "PMC8160124",
]

BIOC_URL = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmcid}/unicode"


def estrai_testo_bioc(data: list) -> str:
    testi = []
    for collection in data:
        for doc in collection.get("documents", []):
            for passage in doc.get("passages", []):
                if passage.get("infons", {}).get("section_type") == "REF":
                    continue
                t = passage.get("text", "").strip()
                if t:
                    testi.append(t)
    return "\n\n".join(testi)


def scarica_paper(pmcid: str, tentativi: int = 3) -> str | None:
    url = BIOC_URL.format(pmcid=pmcid)
    headers = {"User-Agent": "EnduranceRAG-progetto-personale-studio (non commerciale)"}

    for tentativo in range(tentativi):
        resp = requests.get(url, headers=headers, timeout=30)

        if resp.status_code == 429:
            attesa = 15 * (tentativo + 1)  # backoff crescente: 15s, 30s, 45s
            print(f"  Rate limit (429), aspetto {attesa}s e riprovo...")
            time.sleep(attesa)
            continue

        resp.raise_for_status()
        try:
            data = resp.json()
        except ValueError:
            # Risposta non-JSON: l'articolo non e' nel subset Open Access.
            return None
        return estrai_testo_bioc(data)

    return None  # tentativi esauriti


if __name__ == "__main__":
    config.EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    riusciti = 0

    for i, pmcid in enumerate(PMCIDS, start=1):
        print(f"Scarico {pmcid}...")
        try:
            testo = scarica_paper(pmcid)
        except Exception as e:
            print(f"  Errore imprevisto su {pmcid}: {e}")
            time.sleep(3)
            continue

        if not testo:
            print(f"  Non disponibile (non open access): {pmcid}")
            time.sleep(3)
            continue

        out_path = config.EXTRACTED_DIR / f"paper_{i:02d}_{pmcid}.txt"
        out_path.write_text(testo, encoding="utf-8")
        print(f"  Salvato: {out_path.name} ({len(testo)} caratteri)")
        riusciti += 1
        time.sleep(3)  # pausa piu' ampia: rispetta il rate limit del servizio

    print(f"\nCompletato: {riusciti}/{len(PMCIDS)} paper scaricati con successo.")