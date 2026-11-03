"""
Generatore di dati sintetici di esempio per DataRecon.

Crea due file Excel realistici (Fatture Emesse vs Flusso Incassi Bancari)
con anomalie tipiche del mondo contabile e di fatturazione:
- Corrispondenze perfette
- Scostamenti di importo (es. differenze decimali, commissioni non scorporate)
- Righe orfane (fatture non ancora incassate presenti solo in A)
- Righe orfane (bonifici non censiti presenti solo in B)
- Chiavi con spazi accidentali o formattazione disomogenea
- Chiavi duplicate
"""

from pathlib import Path
import pandas as pd


def genera_file_esempio(output_dir: Path | str = "DATI_ESEMPIO") -> tuple[Path, Path]:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Dataset A: Fatture Emesse (es. Gestionale Vendite)
    dati_a = [
        {"ID_FATTURA": "FAT-2026-001", "CLIENTE": "Acme Corporation SpA", "IMPORTO": 1250.00, "DATA": "2026-01-10", "STATO": "EMESSA"},
        {"ID_FATTURA": "FAT-2026-002", "CLIENTE": "Beta Servizi Srl", "IMPORTO": 450.50, "DATA": "2026-01-12", "STATO": "EMESSA"},
        {"ID_FATTURA": "FAT-2026-003", "CLIENTE": "Gamma Logistica Sas", "IMPORTO": 3200.00, "DATA": "2026-01-15", "STATO": "EMESSA"},
        {"ID_FATTURA": "FAT-2026-004", "CLIENTE": "Delta Consulting Srl", "IMPORTO": 890.00, "DATA": "2026-01-18", "STATO": "EMESSA"},
        {"ID_FATTURA": "FAT-2026-005", "CLIENTE": "Epsilon Retail SpA", "IMPORTO": 5400.20, "DATA": "2026-01-20", "STATO": "EMESSA"},
        {"ID_FATTURA": "FAT-2026-006", "CLIENTE": "Zeta Impianti Srl", "IMPORTO": 1780.00, "DATA": "2026-01-22", "STATO": "EMESSA"},
        # Anomalia: Spazio accidentale all'inizio o fine
        {"ID_FATTURA": " FAT-2026-007 ", "CLIENTE": "Omega Food Sas", "IMPORTO": 960.00, "DATA": "2026-01-25", "STATO": "EMESSA"},
        # Anomalia: Orfana in A (fattura emessa ma non presente nel flusso bancario)
        {"ID_FATTURA": "FAT-2026-008", "CLIENTE": "K-Tech Solutions", "IMPORTO": 2100.00, "DATA": "2026-01-28", "STATO": "EMESSA"},
        {"ID_FATTURA": "FAT-2026-009", "CLIENTE": "Nova Energie Srl", "IMPORTO": 1540.00, "DATA": "2026-01-29", "STATO": "EMESSA"},
        # Anomalia: Duplicato su A
        {"ID_FATTURA": "FAT-2026-010", "CLIENTE": "Solaris Green Srl", "IMPORTO": 600.00, "DATA": "2026-01-30", "STATO": "EMESSA"},
        {"ID_FATTURA": "FAT-2026-010", "CLIENTE": "Solaris Green Srl (Duplicata)", "IMPORTO": 600.00, "DATA": "2026-01-30", "STATO": "EMESSA"},
    ]

    # 2. Dataset B: Incassi Ricevuti (es. Estratto Conto Bancario o Flusso CBI)
    dati_b = [
        # Match perfetto
        {"RIFERIMENTO": "FAT-2026-001", "ORDINANTE": "ACME CORPORATION", "IMPORTO_INCASSATO": 1250.00, "DATA_VALUTA": "2026-01-15", "CANALE": "BONIFICO"},
        # Discrepanza importo (es. commissione o decurtazione di 10.00 €)
        {"RIFERIMENTO": "FAT-2026-002", "ORDINANTE": "BETA SERVIZI SRL", "IMPORTO_INCASSATO": 440.50, "DATA_VALUTA": "2026-01-16", "CANALE": "BONIFICO"},
        # Match perfetto
        {"RIFERIMENTO": "FAT-2026-003", "ORDINANTE": "GAMMA LOGISTICA SAS", "IMPORTO_INCASSATO": 3200.00, "DATA_VALUTA": "2026-01-20", "CANALE": "BONIFICO"},
        # Discrepanza centesimi (arrotondamento errato 890.00 vs 890.05)
        {"RIFERIMENTO": "FAT-2026-004", "ORDINANTE": "DELTA CONSULTING", "IMPORTO_INCASSATO": 890.05, "DATA_VALUTA": "2026-01-22", "CANALE": "RIBA"},
        # Match perfetto
        {"RIFERIMENTO": "FAT-2026-005", "ORDINANTE": "EPSILON RETAIL SPA", "IMPORTO_INCASSATO": 5400.20, "DATA_VALUTA": "2026-01-25", "CANALE": "BONIFICO"},
        # Match perfetto
        {"RIFERIMENTO": "FAT-2026-006", "ORDINANTE": "ZETA IMPIANTI SRL", "IMPORTO_INCASSATO": 1780.00, "DATA_VALUTA": "2026-01-26", "CANALE": "BONIFICO"},
        # Corrispondenza con chiave senza spazi (il software deve normalizzare ed effettuare il match!)
        {"RIFERIMENTO": "FAT-2026-007", "ORDINANTE": "OMEGA FOOD SAS", "IMPORTO_INCASSATO": 960.00, "DATA_VALUTA": "2026-01-28", "CANALE": "BONIFICO"},
        # Anomalia: Orfana in B (bonifico incassato senza fattura di riscontro)
        {"RIFERIMENTO": "BON-NON-CENSITO-99", "ORDINANTE": "CLIENTE SCONOSCIUTO", "IMPORTO_INCASSATO": 750.00, "DATA_VALUTA": "2026-01-29", "CANALE": "BONIFICO"},
        # Match per il duplicato
        {"RIFERIMENTO": "FAT-2026-010", "ORDINANTE": "SOLARIS GREEN SRL", "IMPORTO_INCASSATO": 600.00, "DATA_VALUTA": "2026-02-01", "CANALE": "BONIFICO"},
    ]

    df_a = pd.DataFrame(dati_a)
    df_b = pd.DataFrame(dati_b)

    file_a = out_path / "fatture_emesse.xlsx"
    file_b = out_path / "incassi_bancari.xlsx"

    df_a.to_excel(file_a, index=False, engine="openpyxl")
    df_b.to_excel(file_b, index=False, engine="openpyxl")

    return file_a, file_b


if __name__ == "__main__":
    fa, fb = genera_file_esempio()
    print(f"File generati con successo in:\n- {fa}\n- {fb}")
