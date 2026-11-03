---
name: grafica-datarecon
description: Use when creating or modifying any visual element of the DataRecon PySide6 desktop app (maschera.py, app.py styles, colors, layout, KPI cards, table colors, dialogs, buttons, light or dark theme), or when verifying visual readability across themes.
---

# Grafica DataRecon (PySide6)

App desktop multipiattaforma in `PySide6` (Qt6): solo widget Qt standard, nessuna dipendenza grafica extra.

## 1. Palette e Regole di Contrasto (Chiaro & Scuro)

| Elemento | Tema Chiaro | Tema Scuro | Scopo |
|---|---|---|---|
| **Colore Primario (Brand)** | `#2563EB` (Blu) | `#3B82F6` (Blu brillante) | Pulsante principale "Esegui Riconciliazione", intestazioni |
| **Testo su Primario** | `#FFFFFF` | `#FFFFFF` | Contrasto netto garantito |
| **Stato Match OK (Verde)** | Fondo `#DCFCE7` / Testo `#166534` | Fondo `#14532D` / Testo `#DCFCE7` | Righe e KPI senza anomalie |
| **Stato Discrepanza (Ambra)** | Fondo `#FEF3C7` / Testo `#92400E` | Fondo `#78350F` / Testo `#FEF3C7` | Righe con scostamento di importo/valore |
| **Stato Orfano/Errore (Rosso)**| Fondo `#FEE2E2` / Testo `#991B1B` | Fondo `#7F1D1D` / Testo `#FEE2E2` | Righe mancanti in A o B / Duplicati |
| **Pulsante Disattivato** | Fondo `#E5E7EB` / Testo `#6B7280` | Fondo `#374151` / Testo `#9CA3AF` | Pulsanti non ancora cliccabili (`:disabled`) |

### Regole auree anti-bug visivi
1. **Mai impostare lo sfondo senza impostare il colore del testo:** Il testo di default segue il tema di sistema (bianco in tema scuro, nero in tema chiaro) e diventa illeggibile su uno sfondo personalizzato. Nelle tabelle `QTableWidget`, impostare sempre sia `setBackground` sia `setForeground`.
2. **Stati `:disabled` espliciti nel QSS:** Specificare sempre sfondo e testo dei pulsanti disattivati sia in chiaro che in scuro.
3. **Gerarchia visiva e spaziatura:** Usare margini respirabili (`12px-16px`), card KPI per i conteggi sintetici in alto e tabella filtrabile in basso.

## 2. Verifica Visiva Obbligatoria
Dopo ogni modifica a `maschera.py` o `app.py`:
1. Eseguire `.venv/bin/python CODICE/SVILUPPO/screenshot_maschera.py` per generare i PNG in `.local/screenshot/` (tema chiaro e tema scuro, stato iniziale e stato con risultati).
2. Ispezionare ogni PNG con `read_file` per verificare che nessun testo sia tagliato o illeggibile.
3. Eseguire `pytest TEST/` per confermare che i test della GUI passino.
