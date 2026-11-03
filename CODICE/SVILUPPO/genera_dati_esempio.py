"""
Generatore di dati sintetici di esempio per DataRecon (Excel .xlsx e CSV .csv).

Crea:
1. Due file Excel (`fatture_emesse.xlsx` vs `incassi_bancari.xlsx`)
2. Due file CSV (`anagrafica_fatturato_A.csv` vs `flusso_distributore_B.csv`)
con anomalie realistiche (match perfetti, scostamenti d'importo, righe orfane A/B,
spazi accidentali, case disomogeneo e chiavi duplicate).
"""

from pathlib import Path
import random
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
        {"RIFERIMENTO": "FAT-2026-001", "ORDINANTE": "ACME CORPORATION", "IMPORTO_INCASSATO": 1250.00, "DATA_VALUTA": "2026-01-15", "CANALE": "BONIFICO"},
        {"RIFERIMENTO": "FAT-2026-002", "ORDINANTE": "BETA SERVIZI SRL", "IMPORTO_INCASSATO": 440.50, "DATA_VALUTA": "2026-01-16", "CANALE": "BONIFICO"},
        {"RIFERIMENTO": "FAT-2026-003", "ORDINANTE": "GAMMA LOGISTICA SAS", "IMPORTO_INCASSATO": 3200.00, "DATA_VALUTA": "2026-01-20", "CANALE": "BONIFICO"},
        {"RIFERIMENTO": "FAT-2026-004", "ORDINANTE": "DELTA CONSULTING", "IMPORTO_INCASSATO": 890.05, "DATA_VALUTA": "2026-01-22", "CANALE": "RIBA"},
        {"RIFERIMENTO": "FAT-2026-005", "ORDINANTE": "EPSILON RETAIL SPA", "IMPORTO_INCASSATO": 5400.20, "DATA_VALUTA": "2026-01-25", "CANALE": "BONIFICO"},
        {"RIFERIMENTO": "FAT-2026-006", "ORDINANTE": "ZETA IMPIANTI SRL", "IMPORTO_INCASSATO": 1780.00, "DATA_VALUTA": "2026-01-26", "CANALE": "BONIFICO"},
        {"RIFERIMENTO": "FAT-2026-007", "ORDINANTE": "OMEGA FOOD SAS", "IMPORTO_INCASSATO": 960.00, "DATA_VALUTA": "2026-01-28", "CANALE": "BONIFICO"},
        {"RIFERIMENTO": "BON-NON-CENSITO-99", "ORDINANTE": "CLIENTE SCONOSCIUTO", "IMPORTO_INCASSATO": 750.00, "DATA_VALUTA": "2026-01-29", "CANALE": "BONIFICO"},
        {"RIFERIMENTO": "FAT-2026-010", "ORDINANTE": "SOLARIS GREEN SRL", "IMPORTO_INCASSATO": 600.00, "DATA_VALUTA": "2026-02-01", "CANALE": "BONIFICO"},
    ]

    df_a = pd.DataFrame(dati_a)
    df_b = pd.DataFrame(dati_b)

    file_a = out_path / "fatture_emesse.xlsx"
    file_b = out_path / "incassi_bancari.xlsx"

    df_a.to_excel(file_a, index=False, engine="openpyxl")
    df_b.to_excel(file_b, index=False, engine="openpyxl")

    return file_a, file_b


def genera_csv_casuali(output_dir: Path | str = "DATI_ESEMPIO", seed: int = 42) -> tuple[Path, Path]:
    """
    Genera due file CSV realistici con dati casuali ma riproducibili (seed=42)
    per testare la riconciliazione di forniture/consumi e importi.
    """
    rng = random.Random(seed)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    clienti = [
        "Officine Meccaniche Rossi Srl", "Panificio San Marco Sas", "Hotel Belvedere SpA",
        "Supermercato Sigma", "Farmacia Centrale Dr. Bianchi", "Logistica Tirrena Srl",
        "Vetrerie Artigiane Romane", "Studio Legale Associato Verdi", "Palestra FitHouse",
        "Ristorante La Pergola", "Autocarrozzeria Moderna", "Tipografia GraficaSud",
        "Caseificio Valle Verde", "Lavanderia Industriale Lindo", "Elettroforniture Nord",
        "Centro Odontoiatrico Smile", "Maglificio Toscano Srl", "Trasporti Veloci SpA",
        "Agriturismo Il Poggio", "Bar Pasticceria Aurora", "Clinica Veterinaria Roma",
        "Ferramenta Industriale B&B", " Edilizia Integrata Srl", "Cantina Sociale Colli"
    ]

    righe_a = []
    righe_b = []

    # 1. Primi 15 POD: Match perfetti (con qualche chiave sporca da spazi o minuscole)
    for i in range(1, 16):
        pod = f"IT001E9000{i:04d}"
        importo = round(rng.uniform(120.0, 2800.0), 2)
        kwh = int(importo * 3.8)
        nome = clienti[i - 1]

        pod_a = f"  {pod} " if i == 5 else (pod.lower() if i == 9 else pod)
        righe_a.append({
            "CODICE_POD": pod_a,
            "CLIENTE": nome.strip(),
            "KWH_FATTURATI": kwh,
            "IMPORTO_EURO": f"{importo:.2f}",
            "MESE": "2026-10",
        })
        righe_b.append({
            "POD_DISTRIBUTORE": pod,
            "RAGIONE_SOCIALE": nome.strip().upper(),
            "KWH_MISURATI": kwh,
            "TOTALE_ADDEBITATO": f"{importo:.2f}",
            "TIPO_MISURA": "EFFETTIVA",
        })

    # 2. 4 POD con Discrepanza di Importo
    scostamenti = [15.50, -42.00, 128.40, -0.35]
    for idx, delta in enumerate(scostamenti, start=16):
        pod = f"IT001E9000{idx:04d}"
        importo_a = round(rng.uniform(300.0, 1500.0), 2)
        importo_b = round(importo_a + delta, 2)
        nome = clienti[idx - 1]
        righe_a.append({
            "CODICE_POD": pod,
            "CLIENTE": nome.strip(),
            "KWH_FATTURATI": int(importo_a * 3.8),
            "IMPORTO_EURO": f"{importo_a:.2f}",
            "MESE": "2026-10",
        })
        righe_b.append({
            "POD_DISTRIBUTORE": pod,
            "RAGIONE_SOCIALE": nome.strip().upper(),
            "KWH_MISURATI": int(importo_b * 3.8),
            "TOTALE_ADDEBITATO": f"{importo_b:.2f}",
            "TIPO_MISURA": "STIMATA",
        })

    # 3. 3 POD presenti SOLO nel File A (Fatturati ma assenti nel flusso distributore)
    for idx in range(20, 23):
        pod = f"IT001E9000{idx:04d}"
        importo_a = round(rng.uniform(200.0, 900.0), 2)
        righe_a.append({
            "CODICE_POD": pod,
            "CLIENTE": clienti[idx - 1].strip(),
            "KWH_FATTURATI": int(importo_a * 3.8),
            "IMPORTO_EURO": f"{importo_a:.2f}",
            "MESE": "2026-10",
        })

    # 4. 2 POD presenti SOLO nel File B (Presenti sul distributore ma non a gestionale)
    for idx in range(91, 93):
        pod = f"IT001E9000{idx:04d}"
        importo_b = round(rng.uniform(400.0, 1100.0), 2)
        righe_b.append({
            "POD_DISTRIBUTORE": pod,
            "RAGIONE_SOCIALE": f"NUOVA UTENZA NON CENSITA {idx}",
            "KWH_MISURATI": int(importo_b * 3.8),
            "TOTALE_ADDEBITATO": f"{importo_b:.2f}",
            "TIPO_MISURA": "EFFETTIVA",
        })

    # 5. 1 POD duplicato nel File A
    righe_a.append({
        "CODICE_POD": "IT001E90000001",
        "CLIENTE": "Officine Meccaniche Rossi Srl (Seconda emissione)",
        "KWH_FATTURATI": righe_a[0]["KWH_FATTURATI"],
        "IMPORTO_EURO": righe_a[0]["IMPORTO_EURO"],
        "MESE": "2026-10",
    })

    csv_a = out_path / "anagrafica_fatturato_A.csv"
    csv_b = out_path / "flusso_distributore_B.csv"

    pd.DataFrame(righe_a).to_csv(csv_a, index=False, sep=";", encoding="utf-8")
    pd.DataFrame(righe_b).to_csv(csv_b, index=False, sep=";", encoding="utf-8")

    return csv_a, csv_b


if __name__ == "__main__":
    fa, fb = genera_file_esempio()
    ca, cb = genera_csv_casuali()
    print(f"File generati con successo in:\n- {fa}\n- {fb}\n- {ca}\n- {cb}")
