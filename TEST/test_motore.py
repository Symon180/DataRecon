"""
Suite di test unitari completa per DataRecon.
Verifica:
- Normalizzazione chiavi e gestione valori sporchi
- Quadratura con e senza colonne importo
- Tolleranza e calcolo scostamenti
- Esportazione report Excel multi-foglio
"""

from pathlib import Path
import pytest
import pandas as pd

from CODICE.lettura import normalizza_chiave, prepara_dataframe, carica_file
from CODICE.motore import riconcilia_tabelle
from CODICE.scrittura import esporta_report_excel
from CODICE.SVILUPPO.genera_dati_esempio import genera_file_esempio


def test_normalizza_chiave_casi_limite():
    assert normalizza_chiave("  FAT-001  ") == "FAT-001"
    assert normalizza_chiave("1050.0") == "1050"
    assert normalizza_chiave(1050.0) == "1050"
    assert normalizza_chiave(None) == ""
    assert normalizza_chiave(pd.NA) == ""
    assert normalizza_chiave("") == ""


def test_riconciliazione_dati_sintetici(tmp_path: Path):
    file_a, file_b = genera_file_esempio(output_dir=tmp_path)

    df_a = carica_file(file_a)
    df_b = carica_file(file_b)

    assert len(df_a) == 11
    assert len(df_b) == 9

    risultato = riconcilia_tabelle(
        df_a=df_a,
        chiave_a="ID_FATTURA",
        df_b=df_b,
        chiave_b="RIFERIMENTO",
        colonna_valore_a="IMPORTO",
        colonna_valore_b="IMPORTO_INCASSATO",
        tolleranza=0.01,
    )

    kpi = risultato.kpi

    # Verifiche attese sui dati sintetici di prova:
    assert kpi["match_perfetti"] >= 5
    assert kpi["discrepanze_valori"] == 2
    assert kpi["solo_in_a"] == 2
    assert kpi["solo_in_b"] == 1
    assert kpi["duplicati_a"] == 2

    # Verifica esportazione Excel
    report_path = tmp_path / "report_test.xlsx"
    esporta_report_excel(risultato, report_path)
    assert report_path.exists()
    assert report_path.stat().st_size > 0


def test_riconciliazione_pura_solo_chiavi():
    df_a = pd.DataFrame({"CODICE": ["A1", "A2", "A3"], "DESC": ["Uno", "Due", "Tre"]})
    df_b = pd.DataFrame({"ID": ["A2", "A3", "A4"], "NOTE": ["Esiste", "Esiste", "Nuovo"]})

    risultato = riconcilia_tabelle(
        df_a=df_a,
        chiave_a="CODICE",
        df_b=df_b,
        chiave_b="ID",
    )

    assert risultato.kpi["match_perfetti"] == 2
    assert risultato.kpi["solo_in_a"] == 1
    assert risultato.kpi["solo_in_b"] == 1
    assert risultato.kpi["discrepanze_valori"] == 0


def test_tolleranza_centesimi():
    df_a = pd.DataFrame({"ID": ["X1", "X2"], "VALORE": [100.00, 200.00]})
    df_b = pd.DataFrame({"ID": ["X1", "X2"], "VALORE": [100.01, 200.03]})

    # Con tolleranza 0.01, X1 è match e X2 è discrepanza
    risultato = riconcilia_tabelle(
        df_a=df_a,
        chiave_a="ID",
        df_b=df_b,
        chiave_b="ID",
        colonna_valore_a="VALORE",
        colonna_valore_b="VALORE",
        tolleranza=0.01,
    )

    assert risultato.kpi["match_perfetti"] == 1
    assert risultato.kpi["discrepanze_valori"] == 1
