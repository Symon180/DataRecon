# Specifiche Funzionali e Tecniche - DataRecon

**Stato:** Fase 0 completata (Impianto e Ambiente)
**Versione target MVP:** 0.1.0

## 1. Problema e Scopo
In ambito amministrativo, contabile e operativo è frequente dover confrontare due tabelle provenienti da sistemi diversi (es. *Gestionale Fatturazione* vs *Sistema Pagamenti / Estratto Conto*, oppure *Anagrafica Interna* vs *Flusso Distributore/Fornitore*).
DataRecon automatizza questa riconciliazione eliminando l'uso manuale di formule `CERCA.VERT`/`CERCA.X`.

## 2. Architettura Prevista (`CODICE/`)
1. `lettura.py`:
   - Caricamento file `.xlsx` e `.csv` tramite `pandas` / `openpyxl`.
   - Normalizzazione delle chiavi di incrocio (rimozione spazi superflui, uniformazione maiuscole/minuscole, gestione zeri iniziali).
2. `motore.py`:
   - Confronto tra Tabella A (es. Fonte Interna) e Tabella B (es. Fonte Esterna) sulla colonna chiave scelta:
     - **Corrispondenze esatte (Match OK):** presenti in entrambi i file con valori coerenti.
     - **Discrepanze di valore (Mismatch):** presenti in entrambi i file, ma con scostamento su importi (oltre una tolleranza configurabile, es. `0.01 €`) o su campi testuali/stato.
     - **Solo in A (Orfani A):** righe presenti nel primo file ma assenti nel secondo.
     - **Solo in B (Orfani B):** righe presenti nel secondo file ma assenti nel primo.
     - **Duplicati chiave:** righe con chiave ripetuta all'interno dello stesso file.
3. `scrittura.py`:
   - Esportazione di un file Excel `.xlsx` multi-foglio (`RIEPILOGO`, `DISCREPANZE`, `SOLO_IN_A`, `SOLO_IN_B`, `DUPLICATI`, `CONCORDI`) con intestazioni formattate e larghezza colonne automatica.
4. `maschera.py` & `app.py`:
   - Interfaccia grafica `PySide6` pulita, con supporto nativo al tema Chiaro e Scuro, selezione file, scelta colonne da menu a tendina, riepilogo KPI a schede e tabella di anteprima risultati.
