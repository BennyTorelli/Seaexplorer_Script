# COMPLETE SEAEXPLORER PIPELINE SCRIPTS

This folder contains all Python scripts to process SeaExplorer glider data in CSV format. The scripts have been modified to work automatically in sequence.

## 📁 FOLDER CONTENTS

### Main Scripts (in execution order):
1. **`1_convert_raw_to_separate_csv.py`** - Converts raw files to separate CSV files
2. **`2_merge_mission_data_csv.py`** - Merges all CSV files into a single file
3. **`3_convert_all_units_csv.py`** - Converts measurement units
4. **`4_rename_variables_csv.py`** - Renames variables with standard names

### Support Scripts:
- **`summarize_pipeline.py`** - Shows current status of all files
- **`execute_pipeline.py`** - Runs the entire pipeline automatically

## 🚀 HOW TO USE

### Option 1: Run Individual Scripts
```bash
# From the main directory
cd /Users/benedettatorelli/Desktop/Datos_brutos_1

# Script 1: Convert raw → separate CSV
python script_completi/1_convert_raw_to_separate_csv.py

# Script 2: Merge separate CSV files
python script_completi/2_merge_mission_data_csv.py

# Script 3: Convert units
python script_completi/3_convert_all_units_csv.py

# Script 4: Rename variables
python script_completi/4_rename_variables_csv.py
```

### Option 2: Run Complete Pipeline
```bash
# Runs all 4 scripts in sequence
python script_completi/execute_pipeline.py
```

### Option 3: Check Status
```bash
# Shows status of all files
python script_completi/summarize_pipeline.py
```

## 🔧 WHAT HAS BEEN MODIFIED

### Before (Problems):
- Each script worked on different files
- No guaranteed sequential order
- Had to manually modify file paths

### After (Solutions):
- **Automatic file selection**: Each script automatically finds the right file
- **File priority**: Script 3 looks for "merged" files, Script 4 looks for "units_converted" files
- **Smart exclusions**: Avoids already processed files (backup, sample, etc.)
- **Guaranteed sequence**: Each script works on the output of the previous one

## 📊 DATA FLOW

```
Raw Files (.pld1.raw.1-183)
    ↓ Script 1
Separate CSV (mission_001.csv - mission_183.csv)
    ↓ Script 2  
Merged CSV (mission_complete_merged_YYYYMMDD_HHMMSS.csv)
    ↓ Script 3
Units CSV (mission_complete_merged_..._units_converted_YYYYMMDD_HHMMSS.csv)
    ↓ Script 4
Final CSV (with renamed variables)
```

## ✅ APPLIED CONVERSIONS

### Script 3 - Unit Conversions:
- **Turbidity**: m⁻¹ sr⁻¹ → NTU
- **Chlorophyll**: µg/L → mg/m³
- **Conductivity**: mS/cm → S/m
- **Oxygen**: µmol/L → µmol/kg (TEOS-10)
- **Coordinates**: Kept in decimal degrees

### Script 4 - Variable Renaming:
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

## 🎯 ADVANTAGES

1. **Automatic**: No need to manually modify file paths
2. **Sequential**: Guarantees correct processing order
3. **Safe**: Creates automatic backups before modifications
4. **Traceable**: Complete metadata for each step
5. **Flexible**: You can run individual scripts or complete pipeline

## 📝 GENERATED FILES

Each script generates:
- **Main processed file**
- **Viewable sample file** (for checking)
- **Metadata file** (with processing details)
- **Backup file** (before modifications)

## 🚨 IMPORTANT

- Scripts work from the main project directory
- Each script automatically finds the right file to process
- Output files have timestamps to avoid overwrites
- Always check sample files to verify results

## 💡 TIPS

1. **First run**: Use `summarize_pipeline.py` to see current status
2. **Quality control**: Always check the generated "_SAMPLE_" files
3. **Backup**: Backups are automatic, but you can make additional ones
4. **Problems**: Read error messages, they are very detailed

## 📞 SUPPORT

If a script doesn't work:
1. Check that you are in the correct directory
2. Verify that input files exist
3. Read complete error messages
4. Use `summarize_pipeline.py` to diagnose

---
**Created September 22, 2025**  
**SeaExplorer Data Processing Pipeline - Sequential Version**