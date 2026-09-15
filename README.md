# EnduranceRAG — Sistema RAG + Agente per il regolamento FEI Endurance

Sistema di question-answering costruito su dati pubblici reali (regolamento
FEI Endurance 2026 e letteratura scientifica veterinaria) con retrieval
semantico multilingue e un agente con accesso a dati strutturati sui
risultati di gara.

## Architettura

- **Estrazione** (`extract_pdf.py`): pdfplumber per testo e tabelle da PDF
  reali, con filtro per scartare tabelle multi-colonna frammentate
  dall'estrazione automatica e ricongiungimento delle parole spezzate da
  sillabazione a fine riga.
- **Chunking** (`chunking.py`): per articolo normativo (marcatori tipo
  "805.", "816.6") per il regolamento, preservando l'unità di senso del
  testo; a finestra scorrevole (900 caratteri, overlap 150) per i paper
  scientifici, che non hanno una struttura ad articoli.
- **Embedding** (`embeddings.py`): sentence-transformers, modello
  multilingue (`paraphrase-multilingual-MiniLM-L12-v2`), CPU-only.
- **Vector store** (`ingest.py`): ChromaDB, persistente su disco.
- **RAG** (`rag.py`): retrieval dei chunk più rilevanti + generazione della
  risposta con Claude, ancorata esclusivamente al contesto recuperato.
- **Agente** (`agent.py` + `tools.py`): estende il RAG con un tool XML
  (`statistiche_gara`) che l'agente può invocare per interrogare i
  risultati di una gara specifica (partenti, finisher, eliminati e cause,
  velocità media) quando la domanda riguarda dati di gara e non il
  regolamento.
- **API** (`api.py`): endpoint FastAPI (`POST /ask`) che espone l'agente.
- **Interfaccia** (`app_streamlit.py`): UI Streamlit per interrogare il
  sistema e ispezionare le fonti citate.
- **Valutazione** (`eval.py`): calcolo di Recall@k su un eval set di
  dominio.

## Fonti dati

- **Regolamento FEI Endurance 2026** (PDF ufficiale pubblico) — fonte
  normativa principale, chunk-izzata per articolo.
- **Paper scientifici da PMC Open Access** (`fetch_papers.py`,
  `search_papers.py`), scaricati via BioC API e ESearch (NCBI E-utilities)
  — letteratura su fisiologia dell'esercizio, recupero cardiaco e cause di
  eliminazione nel cavallo da endurance.
- **Dati gara di esempio** (`data/xml/example_race.xml`) — XML fittizio con
  la struttura tipica di un risultato di gara FEI, usato dal tool
  `statistiche_gara`. Non sono risultati FEI reali collegati.

## Risultati di valutazione

Recall@1 = 0.75, Recall@3 = 1.00, Recall@5 = 1.00, su un eval set di 8
domande di dominio costruito a mano (nessun ground-truth pubblico
disponibile per questo caso d'uso). Vedi `src/eval.py` per il dettaglio
delle domande e degli articoli attesi.

## Come eseguirlo in locale

```bash
# 1. Ambiente virtuale e dipendenze
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS
pip install -r requirements.txt

# 2. Chiave API
cp .env.example .env
# apri .env e inserisci la tua ANTHROPIC_API_KEY

# 3. Estrazione testo dai PDF (regolamento)
python src/extract_pdf.py

# 4. (opzionale) Scaricare i paper scientifici da PMC
python src/fetch_papers.py

# 5. Indicizzazione in ChromaDB
python src/ingest.py

# 6. Interrogare il sistema
python src/rag.py "Qual è la frequenza cardiaca massima al vet gate?"
python src/agent.py "Quanti finisher ha avuto la gara di Monterosso?"

# 7. Interfaccia web
streamlit run src/app_streamlit.py

# 8. API
uvicorn api:app --reload --app-dir src
```

I testi già estratti (`data/extracted/`) sono inclusi nel repository, quindi
i passi 3-4 sono necessari solo per rigenerarli da zero o aggiungere nuovi
documenti.

## Disclaimer

Progetto dimostrativo e didattico, realizzato per esplorare tecniche di
RAG e agenti su dati di dominio reali. **Non è un tool ufficiale FEI** e
non è stato validato per uso professionale. Le risposte generate non
sostituiscono il parere di un veterinario o di un delegato tecnico FEI:
verifica sempre le fonti citate prima di basarci decisioni reali.
