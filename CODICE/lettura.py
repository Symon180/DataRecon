"""
Modulo di caricamento e normalizzazione dati per DataRecon.

Gestisce la lettura di file Excel (.xlsx, .xls) e CSV,
applicando pulizia automatica delle intestazioni e normalizzazione
delle colonne chiave per evitare falsi scostamenti dovuti a spazi o caratteri sporchi.
"""

from pathlib import Path
import pandas as pd


def carica_file(percorso: Path | str, nome_foglio: str | int | None = 0) -> pd.DataFrame:
    """
    Carica un file tabellare (.xlsx, .xls o .csv) in un DataFrame pandas.
    Pulisce automaticamente gli spazi dalle intestazioni di colonna.
    """
    path = Path(percorso)
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

    estensione = path.suffix.lower()

    if estensione in [".xlsx", ".xls"]:
        df = pd.read_excel(path, sheet_name=nome_foglio, engine="openpyxl" if estensione == ".xlsx" else None)
    elif estensione == ".csv":
        # Prova prima con separatore virgola/punto e virgola e codifica utf-8 / latin-1
        try:
            df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(path, sep=None, engine="python", encoding="latin-1")
    else:
        raise ValueError(f"Formato non supportato ({estensione}). Utilizzare file .xlsx, .xls o .csv")

    # Pulizia nomi colonne: rimuove spazi bianchi iniziali e finali
    df.columns = [str(col).strip() for col in df.columns]
    return df


def normalizza_chiave(valore: object) -> str:
    """
    Normalizza un valore chiave di quadratura:
    - Rimuove spazi bianchi prima e dopo
    - Gestisce float esportati come 123.0 convertendoli coerentemente
    - Converte valori nulli/NaN in stringa vuota
    """
    if pd.isna(valore) or valore is None:
        return ""
    
    testo = str(valore).strip()
    # Se è un float senza decimali (es. 1001.0 derivante da lettura Excel di un codice numerico)
    if testo.endswith(".0"):
        testo = testo[:-2]
    return testo


def prepara_dataframe(df: pd.DataFrame, colonna_chiave: str) -> pd.DataFrame:
    """
    Copia il DataFrame e aggiunge una colonna normalizzata '_CHIAVE_NORM'
    utilizzata internamente per il join e il confronto deterministico.
    """
    if colonna_chiave not in df.columns:
        raise KeyError(f"La colonna chiave '{colonna_chiave}' non è presente nel file.")

    df_lavorazione = df.copy()
    df_lavorazione["_CHIAVE_NORM"] = df_lavorazione[colonna_chiave].apply(normalizza_chiave)
    return df_lavorazione
