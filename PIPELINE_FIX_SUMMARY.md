# Pipeline Elaborazione Dati SeaExplorer - Riassunto Correzioni Sequenziali

## Problema Identificato
L'utente aveva 4 script Python per elaborare i dati del glider SeaExplorer, ma non funzionavano in sequenza - ogni script selezionava file diversi invece di elaborare l'output dello script precedente nella pipeline.

## Panoramica Pipeline
**Ordine Sequenziale Corretto:**
1. `convert_raw_to_separate_csv.py` → Crea 183 file individuali `mission_XXX.csv`
2. `merge_mission_data_csv.py` → Unisce in un singolo `mission_complete_merged_XXX.csv` 
3. `convert_all_units_csv.py` → Converte unità → `mission_complete_merged_units_converted_XXX.csv`
4. `rename_variables_csv.py` → Rinomina variabili → `mission_complete_merged_units_converted_renamed_XXX.csv`

## Problemi Risolti

### 1. Logica Selezione File
**Problema:** Gli script non davano priorità all'output dello script precedente
**Soluzione:** Implementata logica di priorità file in ogni script:

- `convert_all_units_csv.py`: Ora dà priorità ai file con parole chiave "merged" e "complete"
- `rename_variables_csv.py`: Ora dà priorità ai file con parola chiave "units_converted"
- Entrambi gli script escludono file già elaborati ("backup", "sample", "renamed", ecc.)

### 2. Estrazione Numeri File
**Problema:** Le funzioni `extract_number()` avevano parsing incorretto per diversi pattern di nomi file
**Soluzione:** Corretta logica di estrazione per analizzare correttamente:
- Formato `mission_XXX.csv` (per script merge)
- Numerazione file raw dopo "raw." (per script conversione)

### 3. Problemi Formato Coordinate
**Problema:** Gli script convertivano coordinate decimali in formato DMS quando era richiesto decimale
**Soluzione:** Rimossa completamente funzione `decimal_to_dms()` per mantenere coordinate decimali

### 4. Sequenziamento Pipeline
**Problema:** Nessun modo chiaro per eseguire la pipeline completa in ordine
**Soluzione:** Creato script `execute_pipeline.py` che esegue tutti e 4 gli script sequenzialmente con gestione errori appropriata

## Stato Attuale

### ✅ Stato Pipeline (Tutto Completato)
- **Passo 1:** 183 file CSV separati creati nella directory `csv_separati/`
- **Passo 2:** File unito creato: `mission_complete_merged_20250922_194638.csv` (374.5 MB)
- **Passo 3:** Unità convertite: `mission_complete_merged_*_units_converted_*.csv` (374.5 MB)
- **Passo 4:** Variabili rinominate: esistono file `renamed_variables_*.csv`

### 🔧 Modifiche Codice Effettuate

#### convert_all_units_csv.py
```python
# Aggiunta priorità file
merged_files = []
for file in csv_files:
    if any(keyword in file.lower() for keyword in ['merged', 'complete']) and \
       not any(skip in file.lower() for skip in ['units_converted', 'renamed', 'backup', 'sample']):
        # ... priorità ai file merged

# Logica selezione aggiornata
all_valid_files = merged_files + valid_files  # File merged prima
```

#### rename_variables_csv.py
```python
# Aggiunta esclusione per file già rinominati
if any(keyword in file.lower() for keyword in ['backup', 'sample', 'metadata', 'renamed']):
    continue

# Priorità ai file units_converted
if 'units_converted' in file.lower():
    units_converted_files.append(file_info)
```

## Strumenti Creati

### 1. `pipeline_summary.py`
- Analizza stato attuale di tutti i file pipeline
- Mostra conteggi file, dimensioni e date modifica
- Fornisce raccomandazioni per passi successivi
- Valida sequenze numerazione file

### 2. `execute_pipeline.py`  
- Esegue pipeline completa sequenzialmente
- Include gestione errori e protezione timeout
- Fornisce report progresso dettagliato
- Conferma ogni passo prima di procedere

## Istruzioni Utilizzo

### Eseguire Analisi Pipeline
```bash
cd /Users/benedettatorelli/Desktop/Datos_brutos_1
python pld/logs/pipeline_summary.py
```

### Eseguire Pipeline Completa
```bash
cd /Users/benedettatorelli/Desktop/Datos_brutos_1
python execute_pipeline.py
```

### Eseguire Script Individuali (Ordine Sequenziale)
```bash
cd /Users/benedettatorelli/Desktop/Datos_brutos_1/pld/logs
python convert_raw_to_separate_csv.py    # Passo 1
python merge_mission_data_csv.py          # Passo 2  
python convert_all_units_csv.py           # Passo 3
python rename_variables_csv.py            # Passo 4
```

## Vantaggi Principali

1. **Selezione File Automatica:** Ogni script ora seleziona automaticamente il file input corretto basato su priorità
2. **Nessuna Specifica File Manuale:** Non serve modificare script per cambiare percorsi file
3. **Elaborazione Sequenziale:** Assicura che i dati fluiscano correttamente attraverso tutti i passi di elaborazione
4. **Prevenzione Duplicati:** Esclude file già elaborati per prevenire rielaborazione
5. **Tracciamento Progresso:** Report stato chiaro ad ogni passo

## Logica Priorità File

| Script | Priorità | Esclude |
|--------|----------|---------|
| `convert_all_units_csv.py` | "merged", "complete" | "units_converted", "renamed", "backup", "sample" |
| `rename_variables_csv.py` | "units_converted" | "renamed", "backup", "sample", "metadata" |

Questo assicura che ogni script elabori l'output dello script precedente nella pipeline, creando un flusso di lavoro di elaborazione dati sequenziale appropriato.