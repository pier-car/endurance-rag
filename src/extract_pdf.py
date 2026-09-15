"""
Estrazione testo + tabelle da PDF reali (regolamenti FEI, paper scientifici).
I PDF reali sono 'sporchi': intestazioni ripetute, sillabazione a fine riga,
tabelle. Qui gestiamo i casi principali.
"""
import re
import pdfplumber

import config
PDF_DIR = config.PDF_DIR
OUT_DIR = config.EXTRACTED_DIR
OUT_DIR.mkdir(parents=True, exist_ok=True)


def pulisci_testo(text: str) -> str:
    # Ricongiunge le parole spezzate da sillabazione a fine riga: "compe-\ntition" -> "competition"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # Normalizza gli a-capo multipli
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tabella_in_testo(tabella: list) -> str:
    """Converte una tabella estratta in testo leggibile dal modello.
    Scarta le tabelle che l'estrazione ha frammentato (tipico degli
    allegati multi-colonna complessi): meglio nessuna tabella che
    una tabella-spazzatura che inquina il retrieval."""
    if not tabella or len(tabella) < 2:
        return ""  # una tabella con meno di 2 righe è quasi sempre un frammento
    intestazioni = [c or "" for c in tabella[0]]
    # Se le "intestazioni" sono vuote o iniziano con ':' è un frammento mal estratto
    intestazioni_valide = [h for h in intestazioni if h.strip() and not h.strip().startswith(":")]
    if len(intestazioni_valide) < 2:
        return ""  # senza almeno 2 colonne con intestazione sensata, scarta
    righe_testo = []
    for riga in tabella[1:]:
        celle = [c or "" for c in riga]
        coppie = [f"{h}: {v}" for h, v in zip(intestazioni, celle)
                  if v and v.strip() and not v.strip().startswith(":")]
        if len(coppie) >= 2:  # tieni solo righe con almeno 2 campi validi
            righe_testo.append(" | ".join(coppie))
    return "\n".join(righe_testo)


def estrai_pdf(percorso: Path) -> str:
    parti = []
    with pdfplumber.open(percorso) as pdf:
        for page in pdf.pages:
            testo = page.extract_text() or ""
            parti.append(testo)
            for tabella in page.extract_tables():
                t = tabella_in_testo(tabella)
                if t:
                    parti.append("\n[TABELLA]\n" + t + "\n[/TABELLA]\n")
    return pulisci_testo("\n".join(parti))


if __name__ == "__main__":
    pdf_trovati = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_trovati:
        print("Nessun PDF trovato in data/pdf/ — controlla che il file sia lì.")
    for pdf_path in pdf_trovati:
        testo = estrai_pdf(pdf_path)
        out_path = OUT_DIR / (pdf_path.stem + ".txt")
        out_path.write_text(testo, encoding="utf-8")
        print(f"{pdf_path.name}: {len(testo)} caratteri estratti -> {out_path.name}")