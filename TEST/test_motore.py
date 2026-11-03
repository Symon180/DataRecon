"""
Suite di test unitari e di integrazione per DataRecon.
Verifica:
- Normalizzazione chiavi (spazi, case-insensitivity, numeri interi da Excel)
- Parsing importi in formato standard e formato italiano ('€ 1.250,50')
- Quadratura su file Excel e su file CSV con separatore ';'
- Prevenzione prodotto cartesiano su chiavi duplicate
- Esportazione report Excel multi-foglio
- Integrazione interfaccia grafica PySide6
"""

import os
from pathlib import Path
import pytest
import pandas as pd

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from CODICE.lettura import normalizza_chiave, converti_serie_numerica, carica_file
from CODICE.motore import riconcilia_tabelle
from CODICE.scrittura import esporta_report_excel
from CODICE.SVILUPPO.genera_dati_esempio import genera_file_esempio, genera_csv_casuali


def test_normalizza_chiave_casi_limite():
    assert normalizza_chiave("  fat-001  ") == "FAT-001"
    assert normalizza_chiave("it001e90000008") == "IT001E90000008"
    assert normalizza_chiave("1050.0") == "1050"
    assert normalizza_chiave(1050.0) == "1050"
    assert normalizza_chiave(None) == ""
    assert normalizza_chiave(pd.NA) == ""
    assert normalizza_chiave("") == ""


def test_converti_serie_numerica_formati_misti():
    s = pd.Series(["1250.50", "€ 1.250,50", "450,25", "", None, 100])
    ris = converti_serie_numerica(s).tolist()
    assert ris == [1250.50, 1250.50, 450.25, 0.0, 0.0, 100.0]


def test_riconciliazione_dati_excel(tmp_path: Path):
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

    # 6 chiavi con match perfetto (001, 003, 005, 006, 007, 010 deduplicata)
    assert kpi["match_perfetti"] == 6
    # 2 discrepanze (002 e 004)
    assert kpi["discrepanze_valori"] == 2
    # 2 solo in A (008 e 009)
    assert kpi["solo_in_a"] == 2
    # 1 solo in B (BON-NON-CENSITO-99)
    assert kpi["solo_in_b"] == 1
    # 2 righe duplicate in A per FAT-2026-010
    assert kpi["duplicati_a"] == 2

    # Verifica esportazione Excel
    report_path = tmp_path / "report_test.xlsx"
    esporta_report_excel(risultato, report_path)
    assert report_path.exists()
    assert report_path.stat().st_size > 0


def test_riconciliazione_csv_casuali(tmp_path: Path):
    csv_a, csv_b = genera_csv_casuali(output_dir=tmp_path)

    df_a = carica_file(csv_a)
    df_b = carica_file(csv_b)

    # 15 match + 4 discrepanze + 3 solo_a + 1 riga extra duplicata = 23 righe in A
    assert len(df_a) == 23
    # 15 match + 4 discrepanze + 2 solo_b = 21 righe in B
    assert len(df_b) == 21

    risultato = riconcilia_tabelle(
        df_a=df_a,
        chiave_a="CODICE_POD",
        df_b=df_b,
        chiave_b="POD_DISTRIBUTORE",
        colonna_valore_a="IMPORTO_EURO",
        colonna_valore_b="TOTALE_ADDEBITATO",
        tolleranza=0.01,
    )

    kpi = risultato.kpi
    assert kpi["match_perfetti"] == 15
    assert kpi["discrepanze_valori"] == 4
    assert kpi["solo_in_a"] == 3
    assert kpi["solo_in_b"] == 2
    assert kpi["duplicati_a"] == 2
    assert kpi["duplicati_b"] == 0


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


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_maschera_gui_caricamento_csv(tmp_path: Path, qapp):
    from CODICE.maschera import FinestraPrincipale

    csv_a, csv_b = genera_csv_casuali(output_dir=tmp_path)

    finestra = FinestraPrincipale(tema_scuro=False)
    finestra.carica_dataframe(csv_a, "A")
    finestra.carica_dataframe(csv_b, "B")

    # Verifica auto-detect delle colonne chiave e valore
    assert finestra.combo_chiave_a.currentText() == "CODICE_POD"
    assert finestra.combo_chiave_b.currentText() == "POD_DISTRIBUTORE"
    assert finestra.combo_val_a.currentText() == "IMPORTO_EURO"
    assert finestra.combo_val_b.currentText() == "TOTALE_ADDEBITATO"

    finestra.esegui_riconciliazione()
    assert finestra.risultato is not None
    assert finestra.risultato.kpi["match_perfetti"] == 15
    assert finestra.btn_esporta.isEnabled()
    finestra.close()
