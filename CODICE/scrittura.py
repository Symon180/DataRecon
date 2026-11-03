"""
Modulo di esportazione report di quadratura per DataRecon.

Genera una cartella di lavoro Excel (.xlsx) professionale e multi-foglio
con colori leggibili, stili curati, formattazione valute e riepilogo KPI.
"""

from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd

from CODICE.motore import RisultatoRiconciliazione


def applica_stile_tabella(ws, start_row: int = 1, colore_header: str = "1F4E79"):
    """Formatta una tabella Excel con intestazione scura e bordi leggeri."""
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color=colore_header, end_color=colore_header, fill_type="solid")
    border_sottile = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    for cell in ws[start_row]:
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for row in ws.iter_rows(min_row=start_row + 1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            cell.border = border_sottile
            if isinstance(cell.value, (int, float)):
                cell.number_format = "#,##0.00"

    # Auto-adattamento larghezza colonne
    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)


def esporta_report_excel(risultato: RisultatoRiconciliazione, percorso_output: Path | str) -> Path:
    """
    Crea il file Excel di quadratura completo di tutti i fogli.
    """
    out_file = Path(percorso_output)
    wb = openpyxl.Workbook()

    # --- Foglio 1: RIEPILOGO KPI ---
    ws_kpi = wb.active
    ws_kpi.title = "RIEPILOGO_KPI"
    ws_kpi.views.sheetView[0].showGridLines = True

    # Titolo
    ws_kpi["A1"] = "REPORT RICONCILIAZIONE E QUADRATURA DATI"
    ws_kpi["A1"].font = Font(name="Calibri", size=16, bold=True, color="1F4E79")
    ws_kpi["A2"] = f"Generato con DataRecon • Tool di Audit e Automazione"
    ws_kpi["A2"].font = Font(name="Calibri", size=10, italic=True, color="595959")

    # Tabella KPI
    kpi_dati = [
        ("METRICA", "VALORE"),
        ("Righe File A", risultato.kpi["righe_file_a"]),
        ("Righe File B", risultato.kpi["righe_file_b"]),
        ("Tasso di Quadratura (%)", f"{risultato.kpi['percentuale_quadratura']}%"),
        ("Match Perfetti (Conteggio)", risultato.kpi["match_perfetti"]),
        ("Discrepanze di Valore (Conteggio)", risultato.kpi["discrepanze_valori"]),
        ("Record presenti SOLO nel File A", risultato.kpi["solo_in_a"]),
        ("Record presenti SOLO nel File B", risultato.kpi["solo_in_b"]),
        ("Chiavi Duplicate nel File A", risultato.kpi["duplicati_a"]),
        ("Chiavi Duplicate nel File B", risultato.kpi["duplicati_b"]),
        ("Totale Importo File A (€)", risultato.kpi["totale_importo_a"]),
        ("Totale Importo File B (€)", risultato.kpi["totale_importo_b"]),
        ("Totale Importo Quadrato (€)", risultato.kpi["totale_importo_quadrato"]),
        ("Totale Scostamento Anomalie (€)", risultato.kpi["totale_scostamento_anomalie"]),
    ]

    for r_idx, (chiave, val) in enumerate(kpi_dati, start=4):
        ws_kpi.cell(row=r_idx, column=1, value=chiave)
        ws_kpi.cell(row=r_idx, column=2, value=val)

    applica_stile_tabella(ws_kpi, start_row=4, colore_header="1F4E79")

    # --- Fogli Dati con pandas ExcelWriter engine aperto su workbook esistente ---
    fogli = [
        ("DISCREPANZE", risultato.df_discrepanze, "C00000"),     # Rosso/bordeaux per anomalie
        ("SOLO_IN_A", risultato.df_solo_a, "ED7D31"),            # Arancione
        ("SOLO_IN_B", risultato.df_solo_b, "70AD47"),            # Verde oliva
        ("DUPLICATI_A", risultato.df_duplicati_a, "7030A0"),      # Viola
        ("DUPLICATI_B", risultato.df_duplicati_b, "7030A0"),      # Viola
        ("MATCH_PERFETTI", risultato.df_match, "385723"),        # Verde scuro
    ]

    for nome_foglio, df, colore in fogli:
        ws = wb.create_sheet(title=nome_foglio)
        ws.views.sheetView[0].showGridLines = True

        if df.empty:
            ws.cell(row=1, column=1, value="Nessun record in questa categoria.")
            ws.cell(row=1, column=1).font = Font(italic=True, color="595959")
            continue

        # Scrive intestazioni
        for c_idx, col_name in enumerate(df.columns, start=1):
            ws.cell(row=1, column=c_idx, value=str(col_name))

        # Scrive righe
        for r_idx, row_values in enumerate(df.itertuples(index=False), start=2):
            for c_idx, val in enumerate(row_values, start=1):
                ws.cell(row=r_idx, column=c_idx, value=val)

        applica_stile_tabella(ws, start_row=1, colore_header=colore)

    wb.save(out_file)
    return out_file
