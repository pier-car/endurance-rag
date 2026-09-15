"""Agente: combina RAG (regolamento) e tool use (risultati gara)."""
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
from rag import retrieve, format_context, SYSTEM as RAG_SYSTEM, CLAUDE_MODEL
from tools import STATS_TOOL_SCHEMA, TOOL_REGISTRY

AGENT_SYSTEM = RAG_SYSTEM + """

Hai anche accesso a un tool per consultare i risultati di gare specifiche.
Usalo solo quando la domanda riguarda risultati/statistiche di una gara,
non per domande sul regolamento."""


def run_agent(query: str, verbose: bool = True, max_turns: int = 5) -> str:
    chunks = retrieve(query)
    context = format_context(chunks)
    if verbose:
        print("--- Chunk recuperati ---")
        for c in chunks:
            print(f"  Articolo {c['meta'].get('articolo')}")
        print()

    client = Anthropic()
    messages = [{"role": "user", "content": f"CONTESTO:\n{context}\n\nDOMANDA: {query}"}]

    for _ in range(max_turns):
        resp = client.messages.create(
            model=CLAUDE_MODEL, max_tokens=800, system=AGENT_SYSTEM,
            tools=[STATS_TOOL_SCHEMA], messages=messages,
        )
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")

        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            if verbose:
                print(f"--- Chiamata tool: {block.name}({block.input}) ---")
            risultato = TOOL_REGISTRY[block.name](**block.input)
            tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(risultato)})
        messages.append({"role": "user", "content": tool_results})

    return "Numero massimo di turni raggiunto."


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print('Uso: python src/agent.py "la tua domanda"')
        sys.exit(1)
    print("--- Risposta finale ---")
    print(run_agent(" ".join(sys.argv[1:])))