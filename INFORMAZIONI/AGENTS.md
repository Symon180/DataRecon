# Istruzioni di sviluppo - DataRecon

Regole per chi sviluppa: Simone, agente principale e subagent. Caricate in automatico tramite `AGENTS.md` nella radice.

## 1. Direttiva didattica prioritaria: "Spiega mentre fai"
- Simone usa questo progetto per consolidare la programmazione Python e la costruzione di un portfolio GitHub.
- Ogni modulo creato, funzione scritta, test aggiunto o comando eseguito deve essere accompagnato da una spiegazione chiara e concisa in italiano: **cosa fa**, **perché è stato progettato così** e **quali concetti Python sfrutta**.

## 2. Come si sviluppa
- Il codice applicativo vive in `CODICE/`, gli script di supporto/sviluppo in `CODICE/SVILUPPO/`, i test in `TEST/`, gli eseguibili generati in `DIST/` (mai modificati a mano).
- **Multipiattaforma (Linux & Windows):**
  - Usare sempre `pathlib.Path` per ogni percorso file (mai concatenare stringhe con `/` o `\`).
  - L'app usa `PySide6` (Qt6), nativo sia su Linux sia su Windows.
- **Verifica obbligatoria dopo ogni modifica:**
  1. Eseguire i test automatici (`pytest TEST/ -W error`): nessuna modifica si consegna con test rotti o senza il proprio test unitario.
  2. Quando si tocca l'interfaccia grafica (`maschera.py` / `app.py`), seguire la skill `grafica-datarecon`: generare gli screenshot in tema chiaro e scuro ed esaminarli visivamente.

## 3. Continuità e Handoff
- A inizio sessione: leggere `INFORMAZIONI/HANDOFF.md`, `SPEC.md` e `DEVELOP.md`, e verificare lo stato reale con `git status` e `pytest`.
- Ai milestone e a fine sessione: aggiornare `INFORMAZIONI/HANDOFF.md` e mantenerne una copia byte per byte identica in `/home/symon/Documents/Vault Personale/03 - Progetti/In Corso/DataRecon/HANDOFF - DataRecon.md`.

@SECURITY.md
