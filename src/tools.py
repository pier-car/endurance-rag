"""Tool dell'agente: interroga i risultati gara in XML."""
import xml.etree.ElementTree as ET
from pathlib import Path

import config
XML_DIR = config.XML_DIR

STATS_TOOL_SCHEMA = {
    "name": "statistiche_gara",
    "description": (
        "Restituisce statistiche su una gara di endurance dai risultati: numero "
        "di partenti, finisher, eliminati e relative cause, velocità media dei "
        "finisher. Usa questo tool per domande sui RISULTATI di gare specifiche."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"nome_gara": {"type": "string", "description": "Nome (anche parziale) della gara"}},
        "required": ["nome_gara"],
    },
}


def statistiche_gara(nome_gara: str) -> dict:
    nome_gara = nome_gara.lower()
    for xml_file in XML_DIR.glob("*.xml"):
        root = ET.parse(xml_file).getroot()
        for event in root.iter("Event"):
            if nome_gara in event.get("name", "").lower():
                risultati = event.findall("Result")
                finisher = [r for r in risultati if r.get("status") == "Completed"]
                eliminati = [r for r in risultati if r.get("status") == "Eliminated"]
                cause = {}
                for r in eliminati:
                    motivo = r.get("reason", "sconosciuto")
                    cause[motivo] = cause.get(motivo, 0) + 1
                velocita = [float(r.find("AvgSpeed").text) for r in finisher if r.find("AvgSpeed") is not None]
                return {
                    "gara": event.get("name"),
                    "partenti": len(risultati),
                    "finisher": len(finisher),
                    "eliminati": len(eliminati),
                    "cause_eliminazione": cause,
                    "velocita_media_finisher": round(sum(velocita) / len(velocita), 2) if velocita else None,
                }
    return {"errore": f"Nessuna gara trovata con nome '{nome_gara}'"}


TOOL_REGISTRY = {"statistiche_gara": statistiche_gara}