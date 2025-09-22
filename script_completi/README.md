# SCRIPT COMPLETI PIPELINE SEAEXPLORER

Questa cartella contiene tutti gli script Python per elaborare i dati del glider SeaExplorer in formato CSV. Gli script sono stati modificati per funzionare in sequenza automaticamente.

## 📁 CONTENUTO CARTELLA

### Script Principali (in ordine di esecuzione):
1. **`1_convert_raw_to_separate_csv.py`** - Converte file raw in CSV separati
2. **`2_merge_mission_data_csv.py`** - Unisce tutti i CSV in un file unico
3. **`3_convert_all_units_csv.py`** - Converte le unità di misura
4. **`4_rename_variables_csv.py`** - Rinomina le variabili con nomi standard

### Script di Supporto:
- **`pipeline_summary.py`** - Mostra stato attuale di tutti i file
- **`execute_pipeline.py`** - Esegue tutta la pipeline automaticamente

## 🚀 COME USARE

### Opzione 1: Eseguire Script Singoli
```bash
# Dalla directory principale
cd /Users/benedettatorelli/Desktop/Datos_brutos_1

# Script 1: Converte raw → CSV separati
python script_completi/1_convert_raw_to_separate_csv.py

# Script 2: Unisce CSV separati
python script_completi/2_merge_mission_data_csv.py

# Script 3: Converte unità
python script_completi/3_convert_all_units_csv.py

# Script 4: Rinomina variabili
python script_completi/4_rename_variables_csv.py
```

### Opzione 2: Eseguire Pipeline Completa
```bash
# Esegue tutti e 4 gli script in sequenza
python script_completi/execute_pipeline.py
```

### Opzione 3: Controllare Stato
```bash
# Mostra stato di tutti i file
python script_completi/pipeline_summary.py
```

## 🔧 COSA È STATO MODIFICATO

### Prima (Problemi):
- Ogni script lavorava su file diversi
- Nessun ordine sequenziale garantito
- Bisognava modificare manualmente i percorsi file

### Dopo (Soluzioni):
- **Selezione file automatica**: Ogni script cerca automaticamente il file giusto
- **Priorità file**: Script 3 cerca file "merged", Script 4 cerca file "units_converted"
- **Esclusioni intelligenti**: Evita file già processati (backup, sample, ecc.)
- **Sequenza garantita**: Ogni script lavora sull'output del precedente

## 📊 FLUSSO DATI

```
File Raw (.pld1.raw.1-183)
    ↓ Script 1
CSV Separati (mission_001.csv - mission_183.csv)
    ↓ Script 2  
CSV Unito (mission_complete_merged_YYYYMMDD_HHMMSS.csv)
    ↓ Script 3
CSV con Unità (mission_complete_merged_..._units_converted_YYYYMMDD_HHMMSS.csv)
    ↓ Script 4
CSV Finale (con variabili rinominate)
```

## ✅ CONVERSIONI APPLICATE

### Script 3 - Conversioni Unità:
- **Torbidità**: m⁻¹ sr⁻¹ → NTU
- **Clorofilla**: µg/L → mg/m³
- **Conduttività**: mS/cm → S/m
- **Ossigeno**: µmol/L → µmol/kg (TEOS-10)
- **Coordinate**: Mantenute in gradi decimali

### Script 4 - Rinomina Variabili:
- `PLD_REALTIMECLOCK` → `TIME`
- `LEGATO_CODA_DO` → `DOXY`
- `FLBBCD_BB_700_SCALED` → `TURB`
- `FLBBCD_CHL_SCALED` → `CHLA`
- `LEGATO_CONDUCTIVITY` → `CNDC`
- `LEGATO_TEMPERATURE` → `TEMP`
- `LEGATO_PRESSURE` → `PRES`
- `NAV_DEPTH` → `DEPTH`
- `NAV_LATITUDE` → `LATITUDE`
- `NAV_LONGITUDE` → `LONGITUDE`

## 🎯 VANTAGGI

1. **Automatico**: Non serve modificare percorsi file manualmente
2. **Sequenziale**: Garantisce ordine corretto di elaborazione
3. **Sicuro**: Crea backup automatici prima delle modifiche
4. **Tracciabile**: Metadati completi per ogni passaggio
5. **Flessibile**: Puoi eseguire script singoli o pipeline completa

## 📝 FILE GENERATI

Ogni script genera:
- **File elaborato principale**
- **File di esempio visualizzabile** (per controllo)
- **File metadati** (con dettagli elaborazione)
- **File backup** (prima delle modifiche)

## 🚨 IMPORTANTE

- Gli script funzionano dalla directory principale del progetto
- Ogni script trova automaticamente il file giusto da elaborare
- I file di output hanno timestamp per evitare sovrascritture
- Controlla sempre i file di esempio per verificare risultati

## 💡 SUGGERIMENTI

1. **Prima esecuzione**: Usa `pipeline_summary.py` per vedere stato attuale
2. **Controllo qualità**: Controlla sempre i file "_SAMPLE_" generati
3. **Backup**: I backup sono automatici, ma puoi farne di aggiuntivi
4. **Problemi**: Leggi i messaggi di errore, sono molto dettagliati

## 📞 SUPPORTO

Se uno script non funziona:
1. Controlla che sei nella directory corretta
2. Verifica che i file di input esistano
3. Leggi i messaggi di errore completi
4. Usa `pipeline_summary.py` per diagnosticare

---
**Creato il 22 Settembre 2025**  
**Pipeline SeaExplorer Data Processing - Versione Sequenziale**