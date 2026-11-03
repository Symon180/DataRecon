# Handoff unico - DataRecon

**Stato:** Documento unico di continuità del progetto
**Ultimo aggiornamento:** 01-11-2026 (Fase 0: Impianto, Vault, Ambiente Python e Skill)
**Versione sorgente:** 0.1.0-dev
**Branch:** `main`

---

## 1. Obiettivo del Progetto
Realizzare **DataRecon**, uno strumento desktop (`PySide6`) e CLI in Python per la riconciliazione e quadratura tra due file tabellari (Excel `.xlsx` / `.csv`), pensato come primo progetto completo per il portfolio GitHub personale di Simone.

---

## 2. Cosa è stato fatto finora (Fase 0)
- [x] Creata la struttura di progetto nella Vault Personale (`03 - Progetti/In Corso/DataRecon/`) con:
  - `DataRecon.md` (scheda principale)
  - `DataRecon - Requisiti confermati.md`
  - `DataRecon - Piano di sviluppo.md`
  - `HANDOFF - DataRecon.md` (copia identica di questo file)
- [x] Creata la directory del codice in `/home/symon/Documents/Progetti Personali/DataRecon/` con `CODICE/`, `CODICE/SVILUPPO/`, `TEST/`, `INFORMAZIONI/`, `DIST/`, `.local/`.
- [x] Installato `uv` (`~/.local/bin/uv`), creato l'ambiente virtuale `.venv` con Python 3.12.3 e installate le dipendenze (`pandas`, `openpyxl`, `PySide6`, `pytest`, `pyinstaller`).
- [x] Creata la skill grafica `.agents/skills/grafica-datarecon/SKILL.md` per lo sviluppo dell'interfaccia Qt6 con verifica obbligatoria del contrasto in tema chiaro e scuro tramite screenshot automatici.

---

## 3. Cosa abbiamo imparato in questa sessione
- **Separazione Codice vs Vault:** La vault contiene il coordinamento, i requisiti e gli handoff; il codice vive in una repository Git autonoma (`Progetti Personali/DataRecon`).
- **Gestione Ambienti Virtuali con `uv`:** Su Linux, quando mancano i pacchetti di sistema `python3-pip` o `python3-venv` (che richiederebbero permessi di amministratore `sudo`), `uv` permette di creare ambienti `.venv` isolati e installare librerie nello spazio utente in pochi secondi.
- **Architettura Multipiattaforma:** Usando `pathlib.Path` per i percorsi e `PySide6` per l'interfaccia grafica, lo stesso codice scritto su Linux gira nativamente anche su Windows.

---

## 4. Architettura Prevista (`CODICE/`)
- `CODICE/SVILUPPO/genera_dati_esempio.py`: Script che genera due file Excel realistici di prova con anomalie note.
- `CODICE/lettura.py`: Caricamento Excel/CSV e pulizia delle chiavi di confronto.
- `CODICE/motore.py`: Algoritmo di riconciliazione (Match, Discrepanze importi/testo, Orfani A, Orfani B, Duplicati).
- `CODICE/scrittura.py`: Esportazione del report Excel multi-foglio formattato.
- `CODICE/maschera.py` & `CODICE/app.py`: Interfaccia grafica `PySide6`.
- `CODICE/SVILUPPO/screenshot_maschera.py`: Cattura automatica PNG della finestra in tema chiaro e scuro.

---

## 5. Azioni Aperte per la Prossima Sessione (Fase 1)
- [ ] Decidere insieme lo scenario dei dati sintetici di prova (es. *Fatture Emesse vs Pagamenti/Incassi*).
- [ ] Scrivere e spiegare `CODICE/SVILUPPO/genera_dati_esempio.py`.
- [ ] Scrivere e spiegare `CODICE/lettura.py` con i relativi test in `TEST/test_lettura.py`.

---

## 6. Comandi Utili per Riprendere
```bash
cd "/home/symon/Documents/Progetti Personali/DataRecon"
source .venv/bin/activate
pytest TEST/
```
