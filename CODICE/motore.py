"""
Motore di riconciliazione e quadratura dati per DataRecon.

Esegue il confronto logico e deterministico tra due tabelle:
1. Individua record duplicati
2. Calcola corrispondenze su chiave primaria normalizzata
3. Identifica righe presenti solo nel primo file (Orfani A)
4. Identifica righe presenti solo nel secondo file (Orfani B)
5. Confronta colonne numeriche (es. importi) con soglia di tolleranza
6. Calcola KPI sintetici di quadratura economica e volumetrica
"""

from dataclasses import dataclass, field
from typing import Any
import numpy as np
import pandas as pd

from CODICE.lettura import prepara_dataframe


@dataclass
class RisultatoRiconciliazione:
    """Contenitore strutturato di tutti gli output della riconciliazione."""
    kpi: dict[str, Any]
    df_match: pd.DataFrame
    df_discrepanze: pd.DataFrame
    df_solo_a: pd.DataFrame
    df_solo_b: pd.DataFrame
    df_duplicati_a: pd.DataFrame
    df_duplicati_b: pd.DataFrame


def riconcilia_tabelle(
    df_a: pd.DataFrame,
    chiave_a: str,
    df_b: pd.DataFrame,
    chiave_b: str,
    colonna_valore_a: str | None = None,
    colonna_valore_b: str | None = None,
    tolleranza: float = 0.01,
) -> RisultatoRiconciliazione:
    """
    Esegue la riconciliazione completa tra Tabella A e Tabella B.
    """
    # 1. Normalizzazione chiavi
    t_a = prepara_dataframe(df_a, chiave_a)
    t_b = prepara_dataframe(df_b, chiave_b)

    # 2. Controllo duplicati sulla chiave
    duplicati_mask_a = t_a["_CHIAVE_NORM"].duplicated(keep=False) & (t_a["_CHIAVE_NORM"] != "")
    duplicati_mask_b = t_b["_CHIAVE_NORM"].duplicated(keep=False) & (t_b["_CHIAVE_NORM"] != "")

    df_duplicati_a = t_a[duplicati_mask_a].drop(columns=["_CHIAVE_NORM"])
    df_duplicati_b = t_b[duplicati_mask_b].drop(columns=["_CHIAVE_NORM"])

    # 3. Identificazione presenze su chiave
    set_a = set(t_a["_CHIAVE_NORM"].dropna()) - {""}
    set_b = set(t_b["_CHIAVE_NORM"].dropna()) - {""}

    chiavi_comuni = set_a.intersection(set_b)
    chiavi_solo_a = set_a - set_b
    chiavi_solo_b = set_b - set_a

    # Righe orfane
    df_solo_a = t_a[t_a["_CHIAVE_NORM"].isin(chiavi_solo_a)].drop(columns=["_CHIAVE_NORM"])
    df_solo_b = t_b[t_b["_CHIAVE_NORM"].isin(chiavi_solo_b)].drop(columns=["_CHIAVE_NORM"])

    # 4. Confronto valori per le chiavi comuni
    righe_match: list[dict[str, Any]] = []
    righe_discrepanze: list[dict[str, Any]] = []

    # Selezioniamo le righe non duplicate con chiavi in comune
    comuni_a = t_a[t_a["_CHIAVE_NORM"].isin(chiavi_comuni)]
    comuni_b = t_b[t_b["_CHIAVE_NORM"].isin(chiavi_comuni)]

    # Merge sulle chiavi comuni normalizzate
    merged = pd.merge(
        comuni_a,
        comuni_b,
        on="_CHIAVE_NORM",
        how="inner",
        suffixes=("_A", "_B")
    )

    ha_valori = bool(
        colonna_valore_a
        and colonna_valore_b
        and colonna_valore_a in df_a.columns
        and colonna_valore_b in df_b.columns
    )

    totale_scostamento = 0.0
    valore_quadrato = 0.0

    if ha_valori:
        col_val_a = f"{colonna_valore_a}_A" if colonna_valore_a in comuni_a.columns and colonna_valore_a in comuni_b.columns else colonna_valore_a
        col_val_b = f"{colonna_valore_b}_B" if colonna_valore_b in comuni_a.columns and colonna_valore_b in comuni_b.columns else colonna_valore_b

        # Convertiamo a numerico
        val_a = pd.to_numeric(merged[col_val_a], errors="coerce").fillna(0.0)
        val_b = pd.to_numeric(merged[col_val_b], errors="coerce").fillna(0.0)
        diff = (val_b - val_a).round(4)
        scostamento_assoluto = diff.abs()

        maschera_match = scostamento_assoluto <= tolleranza
        maschera_disc = ~maschera_match

        merged["VALORE_A"] = val_a
        merged["VALORE_B"] = val_b
        merged["SCOSTAMENTO"] = diff
        merged["SCOSTAMENTO_ASS"] = scostamento_assoluto

        df_match = merged[maschera_match].drop(columns=["_CHIAVE_NORM", "SCOSTAMENTO_ASS"])
        df_discrepanze = merged[maschera_disc].drop(columns=["_CHIAVE_NORM", "SCOSTAMENTO_ASS"])

        totale_scostamento = float(diff[maschera_disc].sum())
        valore_quadrato = float(val_a[maschera_match].sum())
    else:
        df_match = merged.drop(columns=["_CHIAVE_NORM"])
        df_discrepanze = pd.DataFrame()

    # 5. Calcolo KPI sintetici
    tot_val_a = float(pd.to_numeric(df_a[colonna_valore_a], errors="coerce").fillna(0).sum()) if colonna_valore_a and colonna_valore_a in df_a.columns else 0.0
    tot_val_b = float(pd.to_numeric(df_b[colonna_valore_b], errors="coerce").fillna(0).sum()) if colonna_valore_b and colonna_valore_b in df_b.columns else 0.0

    totale_righe = len(df_a)
    percentuale_quadratura = round((len(df_match) / totale_righe * 100), 2) if totale_righe > 0 else 0.0

    kpi = {
        "righe_file_a": len(df_a),
        "righe_file_b": len(df_b),
        "chiavi_distinte_a": len(set_a),
        "chiavi_distinte_b": len(set_b),
        "match_perfetti": len(df_match),
        "discrepanze_valori": len(df_discrepanze),
        "solo_in_a": len(df_solo_a),
        "solo_in_b": len(df_solo_b),
        "duplicati_a": len(df_duplicati_a),
        "duplicati_b": len(df_duplicati_b),
        "percentuale_quadratura": percentuale_quadratura,
        "totale_importo_a": round(tot_val_a, 2),
        "totale_importo_b": round(tot_val_b, 2),
        "totale_importo_quadrato": round(valore_quadrato, 2),
        "totale_scostamento_anomalie": round(totale_scostamento, 2),
    }

    return RisultatoRiconciliazione(
        kpi=kpi,
        df_match=df_match,
        df_discrepanze=df_discrepanze,
        df_solo_a=df_solo_a,
        df_solo_b=df_solo_b,
        df_duplicati_a=df_duplicati_a,
        df_duplicati_b=df_duplicati_b,
    )
