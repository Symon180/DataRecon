"""
Interfaccia Grafica Desktop per DataRecon (PySide6 / Qt6).

Permette di:
- Selezionare due file Excel/CSV e le relative colonne di quadratura
- Caricare con un click i dati di esempio sintetici
- Eseguire la riconciliazione con visualizzazione immediata dei KPI
- Esportare il report Excel multi-foglio formattato
- Supportare nativamente tema chiaro e tema scuro ad alto contrasto
"""

import sys
from pathlib import Path
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QColor, QBrush
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QComboBox, QDoubleSpinBox,
    QGroupBox, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QFrame, QTabWidget
)

from CODICE.lettura import carica_file
from CODICE.motore import riconcilia_tabelle, RisultatoRiconciliazione
from CODICE.scrittura import esporta_report_excel
from CODICE.SVILUPPO.genera_dati_esempio import genera_file_esempio, genera_csv_casuali

RADICE_PROGETTO = Path(__file__).resolve().parent.parent
CARTELLA_DATI_ESEMPIO = RADICE_PROGETTO / "DATI_ESEMPIO"


STILE_CHIARO = """
QMainWindow, QWidget {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 18px;
    background-color: #FFFFFF;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #1E293B;
}
QPushButton {
    background-color: #E2E8F0;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #CBD5E1;
}
QPushButton#btn_primario {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    font-weight: bold;
    font-size: 14px;
    padding: 10px 20px;
    border-radius: 6px;
}
QPushButton#btn_primario:hover {
    background-color: #1D4ED8;
}
QPushButton#btn_primario:disabled {
    background-color: #94A3B8;
    color: #E2E8F0;
}
QComboBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    padding: 5px 8px;
    min-height: 24px;
}
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    gridline-color: #E2E8F0;
}
QHeaderView::section {
    background-color: #F1F5F9;
    color: #1E293B;
    font-weight: bold;
    border: 1px solid #CBD5E1;
    padding: 6px;
}
"""

STILE_SCURO = """
QMainWindow, QWidget {
    background-color: #0F172A;
    color: #F8FAFC;
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 13px;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 18px;
    background-color: #1E293B;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #93C5FD;
}
QPushButton {
    background-color: #334155;
    color: #F8FAFC;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #475569;
}
QPushButton#btn_primario {
    background-color: #3B82F6;
    color: #FFFFFF;
    border: none;
    font-weight: bold;
    font-size: 14px;
    padding: 10px 20px;
    border-radius: 6px;
}
QPushButton#btn_primario:hover {
    background-color: #2563EB;
}
QPushButton#btn_primario:disabled {
    background-color: #1E293B;
    color: #64748B;
}
QComboBox, QDoubleSpinBox {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 5px;
    padding: 5px 8px;
    min-height: 24px;
}
QTableWidget {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    gridline-color: #334155;
}
QHeaderView::section {
    background-color: #0F172A;
    color: #93C5FD;
    font-weight: bold;
    border: 1px solid #334155;
    padding: 6px;
}
"""


class FinestraPrincipale(QMainWindow):
    def __init__(self, tema_scuro: bool = False):
        super().__init__()
        self.setWindowTitle("DataRecon — Riconciliazione e Quadratura Dati")
        self.resize(1000, 720)
        self.setMinimumSize(850, 600)

        self.df_a: pd.DataFrame | None = None
        self.df_b: pd.DataFrame | None = None
        self.risultato: RisultatoRiconciliazione | None = None
        self.is_dark = tema_scuro

        self._costruisci_interfaccia()
        self.applica_tema(self.is_dark)

    def _costruisci_interfaccia(self):
        widget_centrale = QWidget()
        layout_principale = QVBoxLayout(widget_centrale)
        layout_principale.setSpacing(12)
        layout_principale.setContentsMargins(18, 16, 18, 16)

        # 1. Header con Titolo e Toggle Tema
        layout_header = QHBoxLayout()
        box_titolo = QVBoxLayout()
        lbl_titolo = QLabel("📊 DataRecon")
        lbl_titolo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        lbl_sottotitolo = QLabel("Strumento desktop per la quadratura e riconciliazione tra flussi contabili ed elenchi Excel/CSV")
        lbl_sottotitolo.setStyleSheet("color: #64748B;")
        box_titolo.addWidget(lbl_titolo)
        box_titolo.addWidget(lbl_sottotitolo)
        layout_header.addLayout(box_titolo)

        layout_header.addStretch()

        self.btn_tema = QPushButton("🌙 Tema Scuro" if not self.is_dark else "☀️ Tema Chiaro")
        self.btn_tema.clicked.connect(self.inverti_tema)
        layout_header.addWidget(self.btn_tema)

        self.btn_dati_esempio = QPushButton("⚡ Prova Excel")
        self.btn_dati_esempio.setToolTip("Genera e carica i due file Excel di prova (Fatture vs Incassi)")
        self.btn_dati_esempio.clicked.connect(self.carica_scenario_esempio)
        layout_header.addWidget(self.btn_dati_esempio)

        self.btn_csv_esempio = QPushButton("📄 Prova CSV Casuali")
        self.btn_csv_esempio.setToolTip("Genera e carica i due file CSV casuali (Fatturato POD vs Distributore)")
        self.btn_csv_esempio.clicked.connect(self.carica_scenario_csv)
        layout_header.addWidget(self.btn_csv_esempio)

        layout_principale.addLayout(layout_header)

        # 2. Selezione File
        box_file = QGroupBox("1. Selezione File Tabellari")
        layout_grid_file = QVBoxLayout(box_file)

        # Riga File A
        riga_a = QHBoxLayout()
        self.lbl_path_a = QLabel("File A (Es. Gestionale / Fatture): Nessun file selezionato")
        self.lbl_path_a.setStyleSheet("font-style: italic;")
        btn_sfoglia_a = QPushButton("Sfoglia File A...")
        btn_sfoglia_a.clicked.connect(lambda: self.apri_selettore_file("A"))
        riga_a.addWidget(self.lbl_path_a, stretch=4)
        riga_a.addWidget(btn_sfoglia_a, stretch=1)
        layout_grid_file.addLayout(riga_a)

        # Riga File B
        riga_b = QHBoxLayout()
        self.lbl_path_b = QLabel("File B (Es. Estratto Conto / Incassi): Nessun file selezionato")
        self.lbl_path_b.setStyleSheet("font-style: italic;")
        btn_sfoglia_b = QPushButton("Sfoglia File B...")
        btn_sfoglia_b.clicked.connect(lambda: self.apri_selettore_file("B"))
        riga_b.addWidget(self.lbl_path_b, stretch=4)
        riga_b.addWidget(btn_sfoglia_b, stretch=1)
        layout_grid_file.addLayout(riga_b)

        layout_principale.addWidget(box_file)

        # 3. Parametri di Confronto
        box_parametri = QGroupBox("2. Mappatura Colonne e Tolleranza")
        layout_param = QHBoxLayout(box_parametri)

        # Colonna Chiave A & B
        v_chiave_a = QVBoxLayout()
        v_chiave_a.addWidget(QLabel("Chiave Primaria (File A):"))
        self.combo_chiave_a = QComboBox()
        v_chiave_a.addWidget(self.combo_chiave_a)
        layout_param.addLayout(v_chiave_a)

        v_chiave_b = QVBoxLayout()
        v_chiave_b.addWidget(QLabel("Chiave Primaria (File B):"))
        self.combo_chiave_b = QComboBox()
        v_chiave_b.addWidget(self.combo_chiave_b)
        layout_param.addLayout(v_chiave_b)

        # Colonna Importo A & B
        v_val_a = QVBoxLayout()
        v_val_a.addWidget(QLabel("Colonna Importo A (Opzionale):"))
        self.combo_val_a = QComboBox()
        v_val_a.addWidget(self.combo_val_a)
        layout_param.addLayout(v_val_a)

        v_val_b = QVBoxLayout()
        v_val_b.addWidget(QLabel("Colonna Importo B (Opzionale):"))
        self.combo_val_b = QComboBox()
        v_val_b.addWidget(self.combo_val_b)
        layout_param.addLayout(v_val_b)

        # Tolleranza
        v_tol = QVBoxLayout()
        v_tol.addWidget(QLabel("Tolleranza Scostamento (€):"))
        self.spin_tolleranza = QDoubleSpinBox()
        self.spin_tolleranza.setRange(0.00, 1000.00)
        self.spin_tolleranza.setValue(0.01)
        self.spin_tolleranza.setSingleStep(0.01)
        v_tol.addWidget(self.spin_tolleranza)
        layout_param.addLayout(v_tol)

        layout_principale.addWidget(box_parametri)

        # 4. Pulsante Esegui Riconciliazione
        self.btn_elabora = QPushButton("⚡ Esegui Riconciliazione Dati")
        self.btn_elabora.setObjectName("btn_primario")
        self.btn_elabora.clicked.connect(self.esegui_riconciliazione)
        layout_principale.addWidget(self.btn_elabora)

        # 5. Dashboard Risultati con Schede di Dettaglio Righe
        box_risultati = QGroupBox("3. Risultato Quadratura e Dettaglio Righe Confrontate")
        layout_risultati = QVBoxLayout(box_risultati)

        self.tabs_risultati = QTabWidget()

        self.tabella_kpi = QTableWidget(6, 3)
        self.tabella_kpi.setHorizontalHeaderLabels(["Indicatore", "Valore", "Cosa significa"])
        self.tabella_kpi.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabella_kpi.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabella_kpi.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.tab_discrepanze = QTableWidget()
        self.tab_solo_a = QTableWidget()
        self.tab_solo_b = QTableWidget()
        self.tab_duplicati = QTableWidget()
        self.tab_match = QTableWidget()

        self.tabs_risultati.addTab(self.tabella_kpi, "📊 Riepilogo KPI")
        self.tabs_risultati.addTab(self.tab_discrepanze, "⚠️ Discrepanze Importo")
        self.tabs_risultati.addTab(self.tab_solo_a, "🟠 Solo in File A")
        self.tabs_risultati.addTab(self.tab_solo_b, "🔵 Solo in File B")
        self.tabs_risultati.addTab(self.tab_duplicati, "🔁 Duplicati")
        self.tabs_risultati.addTab(self.tab_match, "✅ Match Perfetti")

        layout_risultati.addWidget(self.tabs_risultati)

        # Azione Esporta Excel
        self.btn_esporta = QPushButton("📥 Esporta Report Excel Completo (.xlsx)")
        self.btn_esporta.setEnabled(False)
        self.btn_esporta.clicked.connect(self.esporta_report)
        layout_risultati.addWidget(self.btn_esporta)

        layout_principale.addWidget(box_risultati)

        self.setCentralWidget(widget_centrale)

    def applica_tema(self, scuro: bool):
        self.is_dark = scuro
        self.setStyleSheet(STILE_SCURO if scuro else STILE_CHIARO)
        self.btn_tema.setText("☀️ Tema Chiaro" if scuro else "🌙 Tema Scuro")
        if self.risultato:
            self._aggiorna_tabella_kpi()

    def inverti_tema(self):
        self.applica_tema(not self.is_dark)

    def apri_selettore_file(self, target: str):
        CARTELLA_DATI_ESEMPIO.mkdir(parents=True, exist_ok=True)
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Seleziona File {target}",
            str(CARTELLA_DATI_ESEMPIO),
            "File Tabellari (*.xlsx *.xls *.csv);;Tutti i File (*.*)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if file_path:
            self.carica_dataframe(Path(file_path), target)

    def carica_dataframe(self, path: Path, target: str):
        try:
            df = carica_file(path)
            colonne = ["(Nessuna)"] + list(df.columns)

            if target == "A":
                self.df_a = df
                self.lbl_path_a.setText(f"File A: {path.name} ({len(df)} righe)")
                self.combo_chiave_a.clear()
                self.combo_chiave_a.addItems(list(df.columns))
                self.combo_val_a.clear()
                self.combo_val_a.addItems(colonne)
                for c in df.columns:
                    if any(k in c.lower() for k in ("id", "cod", "pod", "pdr", "rif", "fattur", "chiav")):
                        self.combo_chiave_a.setCurrentText(c)
                        break
                for kw in ("import", "tot", "prezz", "valore", "euro", "consum", "kwh", "smc"):
                    trovato = next((c for c in df.columns if kw in c.lower()), None)
                    if trovato:
                        self.combo_val_a.setCurrentText(trovato)
                        break
            else:
                self.df_b = df
                self.lbl_path_b.setText(f"File B: {path.name} ({len(df)} righe)")
                self.combo_chiave_b.clear()
                self.combo_chiave_b.addItems(list(df.columns))
                self.combo_val_b.clear()
                self.combo_val_b.addItems(colonne)
                for c in df.columns:
                    if any(k in c.lower() for k in ("id", "cod", "pod", "pdr", "rif", "fattur", "chiav")):
                        self.combo_chiave_b.setCurrentText(c)
                        break
                for kw in ("import", "tot", "prezz", "valore", "euro", "consum", "kwh", "smc"):
                    trovato = next((c for c in df.columns if kw in c.lower()), None)
                    if trovato:
                        self.combo_val_b.setCurrentText(trovato)
                        break

        except Exception as e:
            QMessageBox.critical(self, "Errore Caricamento", f"Impossibile leggere il file:\n{e}")

    def carica_scenario_esempio(self):
        file_a, file_b = genera_file_esempio(output_dir=CARTELLA_DATI_ESEMPIO)
        self.carica_dataframe(file_a, "A")
        self.carica_dataframe(file_b, "B")
        self.combo_chiave_a.setCurrentText("ID_FATTURA")
        self.combo_chiave_b.setCurrentText("RIFERIMENTO")
        self.combo_val_a.setCurrentText("IMPORTO")
        self.combo_val_b.setCurrentText("IMPORTO_INCASSATO")
        self.esegui_riconciliazione()

    def carica_scenario_csv(self):
        csv_a, csv_b = genera_csv_casuali(output_dir=CARTELLA_DATI_ESEMPIO)
        self.carica_dataframe(csv_a, "A")
        self.carica_dataframe(csv_b, "B")
        self.combo_chiave_a.setCurrentText("CODICE_POD")
        self.combo_chiave_b.setCurrentText("POD_DISTRIBUTORE")
        self.combo_val_a.setCurrentText("IMPORTO_EURO")
        self.combo_val_b.setCurrentText("TOTALE_ADDEBITATO")
        self.esegui_riconciliazione()

    def esegui_riconciliazione(self):
        if self.df_a is None or self.df_b is None:
            QMessageBox.warning(self, "Attenzione", "Selezionare entrambi i file prima di procedere.")
            return

        chiave_a = self.combo_chiave_a.currentText()
        chiave_b = self.combo_chiave_b.currentText()
        val_a = self.combo_val_a.currentText() if self.combo_val_a.currentText() != "(Nessuna)" else None
        val_b = self.combo_val_b.currentText() if self.combo_val_b.currentText() != "(Nessuna)" else None

        try:
            self.risultato = riconcilia_tabelle(
                df_a=self.df_a,
                chiave_a=chiave_a,
                df_b=self.df_b,
                chiave_b=chiave_b,
                colonna_valore_a=val_a,
                colonna_valore_b=val_b,
                tolleranza=self.spin_tolleranza.value(),
            )
            self._aggiorna_tabella_kpi()
            self.btn_esporta.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Errore durante la Quadratura", f"Si è verificato un errore:\n{e}")

    def _popola_tabella_df(self, tabella: QTableWidget, df: pd.DataFrame):
        tabella.clear()
        if df is None or df.empty:
            tabella.setRowCount(1)
            tabella.setColumnCount(1)
            tabella.setHorizontalHeaderLabels(["Risultato"])
            tabella.setItem(0, 0, QTableWidgetItem("Nessun record presente in questa categoria."))
            tabella.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            return

        tabella.setRowCount(len(df))
        tabella.setColumnCount(len(df.columns))
        tabella.setHorizontalHeaderLabels([str(c) for c in df.columns])

        for r_idx, row in enumerate(df.itertuples(index=False)):
            for c_idx, val in enumerate(row):
                testo = f"{val:.2f}" if isinstance(val, float) else str(val if pd.notna(val) else "")
                item = QTableWidgetItem(testo)
                tabella.setItem(r_idx, c_idx, item)

        tabella.resizeColumnsToContents()

    def _aggiorna_tabella_kpi(self):
        if not self.risultato:
            return

        kpi = self.risultato.kpi
        dati = [
            (
                "Tasso di Quadratura Globale",
                f"{kpi['percentuale_quadratura']}%",
                "VERDE" if kpi['percentuale_quadratura'] > 70 else "AMBRA",
                f"Percentuale di codici del File A ({kpi['match_perfetti']} su {kpi['chiavi_distinte_a']}) che quadrano al 100% col File B"
            ),
            (
                "Match Perfetti (Chiave + Importo)",
                str(kpi["match_perfetti"]),
                "VERDE",
                "Codici trovati in entrambi i file con lo stesso identico importo (vedi scheda '✅ Match Perfetti')"
            ),
            (
                "Discrepanze di Valore Rilevate",
                str(kpi["discrepanze_valori"]),
                "AMBRA" if kpi["discrepanze_valori"] > 0 else "VERDE",
                "Codici trovati in entrambi i file, ma con importo diverso tra File A e File B (vedi scheda '⚠️ Discrepanze')"
            ),
            (
                "Record presenti SOLO nel File A",
                str(kpi["solo_in_a"]),
                "ROSSO" if kpi["solo_in_a"] > 0 else "VERDE",
                "Codici presenti nel File A che NON esistono affatto nel File B (vedi scheda '🟠 Solo in File A')"
            ),
            (
                "Record presenti SOLO nel File B",
                str(kpi["solo_in_b"]),
                "ROSSO" if kpi["solo_in_b"] > 0 else "VERDE",
                "Codici presenti nel File B che NON esistono affatto nel File A (vedi scheda '🔵 Solo in File B')"
            ),
            (
                "Totale Scostamento Economico Anomalie",
                f"€ {kpi['totale_scostamento_anomalie']:.2f}",
                "ROSSO" if kpi['totale_scostamento_anomalie'] != 0 else "VERDE",
                "Somma algebrica delle differenze (Importo B meno Importo A) sulle righe con discrepanza"
            ),
        ]

        # Colori secondo skill grafica (con contrasto garantito sfondo + testo)
        colori = {
            "VERDE": {
                "light": (QColor("#DCFCE7"), QColor("#166534")),
                "dark": (QColor("#14532D"), QColor("#DCFCE7")),
            },
            "AMBRA": {
                "light": (QColor("#FEF3C7"), QColor("#92400E")),
                "dark": (QColor("#78350F"), QColor("#FEF3C7")),
            },
            "ROSSO": {
                "light": (QColor("#FEE2E2"), QColor("#991B1B")),
                "dark": (QColor("#7F1D1D"), QColor("#FEE2E2")),
            },
        }

        mode = "dark" if self.is_dark else "light"

        for row_idx, (nome, valore, stato, spiegazione) in enumerate(dati):
            item_nome = QTableWidgetItem(nome)
            item_val = QTableWidgetItem(valore)
            item_val.setTextAlignment(Qt.AlignCenter)
            item_val.setFont(QFont("Segoe UI", 11, QFont.Bold))

            bg, fg = colori[stato][mode]
            item_val.setBackground(QBrush(bg))
            item_val.setForeground(QBrush(fg))

            item_spieg = QTableWidgetItem(spiegazione)

            self.tabella_kpi.setItem(row_idx, 0, item_nome)
            self.tabella_kpi.setItem(row_idx, 1, item_val)
            self.tabella_kpi.setItem(row_idx, 2, item_spieg)

        # Popola le schede di dettaglio righe
        self._popola_tabella_df(self.tab_discrepanze, self.risultato.df_discrepanze)
        self._popola_tabella_df(self.tab_solo_a, self.risultato.df_solo_a)
        self._popola_tabella_df(self.tab_solo_b, self.risultato.df_solo_b)
        df_dup = pd.concat([self.risultato.df_duplicati_a, self.risultato.df_duplicati_b], ignore_index=True)
        self._popola_tabella_df(self.tab_duplicati, df_dup)
        self._popola_tabella_df(self.tab_match, self.risultato.df_match)

        self.tabs_risultati.setTabText(1, f"⚠️ Discrepanze ({len(self.risultato.df_discrepanze)})")
        self.tabs_risultati.setTabText(2, f"🟠 Solo in File A ({len(self.risultato.df_solo_a)})")
        self.tabs_risultati.setTabText(3, f"🔵 Solo in File B ({len(self.risultato.df_solo_b)})")
        self.tabs_risultati.setTabText(4, f"🔁 Duplicati ({len(df_dup)})")
        self.tabs_risultati.setTabText(5, f"✅ Match Perfetti ({len(self.risultato.df_match)})")

    def esporta_report(self):
        if not self.risultato:
            return

        CARTELLA_DATI_ESEMPIO.mkdir(parents=True, exist_ok=True)
        percorso_default = str(CARTELLA_DATI_ESEMPIO / "Report_Quadratura_DataRecon.xlsx")
        percorso_salvataggio, _ = QFileDialog.getSaveFileName(
            self,
            "Salva Report Riconciliazione",
            percorso_default,
            "File Excel (*.xlsx)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if percorso_salvataggio:
            try:
                esporta_report_excel(self.risultato, percorso_salvataggio)
                QMessageBox.information(
                    self,
                    "Esportazione Completata",
                    f"Report salvato con successo:\n{percorso_salvataggio}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Errore di Salvataggio", f"Errore:\n{e}")


def main():
    app = QApplication(sys.argv)
    finestra = FinestraPrincipale()
    finestra.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
