import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st

# In locale la chiave arriva da .env (via load_dotenv sopra); su Streamlit
# Community Cloud arriva dai "Secrets" configurati nell'interfaccia, mai dal
# repository. Qui la rendiamo disponibile in os.environ in entrambi i casi,
# perché il client Anthropic la legge da lì.
api_key = os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")
if api_key:
    os.environ["ANTHROPIC_API_KEY"] = api_key

from agent import run_agent
from rag import retrieve

st.set_page_config(page_title="EnduranceRAG", page_icon="🐴")

st.title("🐴 EnduranceRAG")
st.caption("Assistente dimostrativo su regolamento FEI Endurance e letteratura scientifica.")

st.warning(
    "⚠️ Progetto dimostrativo/didattico, non un tool ufficiale. Le risposte non "
    "sostituiscono il parere di un veterinario o di un delegato tecnico FEI. "
    "Verifica sempre le fonti citate prima di basarci decisioni reali."
)

domanda = st.text_input("Fai una domanda sul regolamento o sulla fisiologia del cavallo da endurance:")

if st.button("Chiedi") and domanda:
    with st.spinner("Cerco nei documenti e genero la risposta..."):
        risposta = run_agent(domanda, verbose=False)
    st.markdown("### Risposta")
    st.write(risposta)

    with st.expander("Fonti consultate"):
        for c in retrieve(domanda, top_k=5):
            fonte = c["meta"].get("fonte", "?")
            articolo = c["meta"].get("articolo", "")
            st.text(f"{fonte}  {articolo}")

st.divider()
st.caption(
    "Hai trovato una risposta sbagliata o poco utile? Scrivimi direttamente "
    "(WhatsApp/messaggio) con la domanda esatta che hai fatto — mi aiuta a migliorarlo."
)