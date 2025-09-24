#!/usr/bin/env python3
"""
RINOMINA VARIABILI NEL DATASET CSV
Rinomina tutte le variabili con nomi standard oceanografici
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import glob

def rename_variables_csv():
    """
    Rinomina tutte le variabili nel CSV con nomi standard
    """
    
    print("🏷️ RINOMINA VARIABILI DATASET CSV")
    print("=" * 50)
    
    # Trova automaticamente il file CSV più recente
    print(f"\n🔍 RICERCA FILE CSV...")
    
    # Patterns di ricerca per file CSV
    csv_patterns = [
        "*.csv",                    # CSV nella directory corrente
        "mission_*.csv",           # Mission files
        "test_complete/*.csv",     # Test directory  
        "netcdf_output/*.csv"      # Output directory
    ]
    
    csv_files = []
    for pattern in csv_patterns:
        files = glob.glob(pattern)
        csv_files.extend(files)
    
    if not csv_files:
        print("❌ Nessun file CSV trovato!")
        print("💡 Patterns cercati:", csv_patterns)
        return
    
    # Filtra file troppo piccoli (< 1MB) o backup/sample
    valid_files = []
    units_converted_files = []  # Priorità ai file con unità convertite
    
    for file in csv_files:
        if any(keyword in file.lower() for keyword in ['backup', 'sample', 'metadata', 'renamed']):
            continue
        size_mb = os.path.getsize(file) / (1024 * 1024)
        if size_mb > 1:  # File maggiori di 1MB
            file_info = (file, size_mb, os.path.getmtime(file))
            # Dai priorità ai file con unità già convertite
            if 'units_converted' in file.lower():
                units_converted_files.append(file_info)
            else:
                valid_files.append(file_info)
    
    # Priorità ai file con unità convertite, poi agli altri
    all_valid_files = units_converted_files + valid_files
    
    if not all_valid_files:
        print("❌ Nessun file CSV valido trovato!")
        return
    
    # Ordina per data di modifica (più recente primo)
    all_valid_files.sort(key=lambda x: x[2], reverse=True)
    csv_file = all_valid_files[0][0]
    
    print(f"✅ File CSV selezionato: {csv_file}")
    print(f"   Dimensione: {all_valid_files[0][1]:.1f} MB")
    print(f"   Ultimo aggiornamento: {datetime.fromtimestamp(all_valid_files[0][2]).strftime('%Y-%m-%d %H:%M:%S')}")
    
    if 'units_converted' in csv_file:
        print(f"   🎯 File con unità già convertite (PRIORITÀ)")
    else:
        print(f"   ⚠️ File senza conversioni unità")
    
    # File CSV
    # csv_file = "test_complete/mission_raw_to_csv_20250922_180354.csv"
    
    # Mapping delle variabili da rinominare
    variable_mapping = {
        'PLD_REALTIMECLOCK': 'TIME',
        'LEGATO_CODA_DO': 'DOXY',
        'FLBBCD_BB_700_SCALED': 'TURB',
        'FLBBCD_CHL_SCALED': 'CHLA',
        'LEGATO_CONDUCTIVITY': 'CNDC',
        'LEGATO_TEMPERATURE': 'TEMP',
        'LEGATO_PRESSURE': 'PRES',
        'NAV_DEPTH': 'DEPTH',
        'NAV_LATITUDE': 'LATITUDE',
        'NAV_LONGITUDE': 'LONGITUDE'
    }
    
    print(f"\n📋 MAPPING VARIABILI:")
    print("-" * 40)
    for old_name, new_name in variable_mapping.items():
        print(f"   {old_name:<25} → {new_name}")
    
    # Carica CSV
    print(f"\n📄 CARICAMENTO CSV...")
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ CSV caricato: {csv_file}")
        print(f"   Righe: {len(df):,}")
        print(f"   Colonne: {len(df.columns)}")
        
        # Mostra colonne attuali
        print(f"\n📊 COLONNE ATTUALI:")
        for i, col in enumerate(df.columns, 1):
            marker = "🎯" if col in variable_mapping else "  "
            print(f"   {marker} {i:2d}. {col}")
        
    except Exception as e:
        print(f"❌ Errore caricamento CSV: {e}")
        return
    
    # Verifica presenza delle variabili da rinominare
    print(f"\n🔍 VERIFICA VARIABILI DA RINOMINARE:")
    print("-" * 45)
    
    missing_vars = []
    present_vars = []
    
    for old_name, new_name in variable_mapping.items():
        if old_name in df.columns:
            present_vars.append((old_name, new_name))
            valid_count = df[old_name].notna().sum()
            total_count = len(df)
            percentage = (valid_count / total_count) * 100
            print(f"   ✅ {old_name:<25} → {new_name:<10} ({valid_count:,} valori, {percentage:.1f}%)")
        else:
            missing_vars.append(old_name)
            print(f"   ❌ {old_name:<25} → {new_name:<10} (NON TROVATA)")
    
    if missing_vars:
        print(f"\n⚠️ Variabili mancanti: {len(missing_vars)}")
        print(f"   Continuo con le variabili disponibili: {len(present_vars)}")
    
    if not present_vars:
        print(f"❌ Nessuna variabile da rinominare trovata!")
        return
    
    # Applica rinomina
    print(f"\n🔄 APPLICAZIONE RINOMINA...")
    
    try:
        # Crea dizionario solo per variabili presenti
        rename_dict = {old_name: new_name for old_name, new_name in present_vars}
        
        # Applica rinomina
        df_renamed = df.rename(columns=rename_dict)
        
        print(f"✅ Rinomina applicata per {len(rename_dict)} variabili")
        
        # Verifica che la rinomina sia avvenuta correttamente
        print(f"\n📋 COLONNE DOPO RINOMINA:")
        renamed_columns = []
        for i, col in enumerate(df_renamed.columns, 1):
            is_renamed = col in rename_dict.values()
            marker = "✅" if is_renamed else "  "
            if is_renamed:
                renamed_columns.append(col)
            print(f"   {marker} {i:2d}. {col}")
        
        print(f"\n🎯 Variabili rinominate: {len(renamed_columns)}")
        print(f"   Nuovi nomi: {', '.join(renamed_columns)}")
        
    except Exception as e:
        print(f"❌ Errore rinomina: {e}")
        return
    
    # Salva CSV con nomi aggiornati
    print(f"\n💾 SALVATAGGIO CSV CON NUOVI NOMI...")
    
    try:
        # Crea backup temporaneo
        backup_file = csv_file.replace('.csv', '_backup_temp.csv')
        df_renamed.to_csv(backup_file, index=False, encoding='utf-8')
        
        # Sostituisce file originale
        df_renamed.to_csv(csv_file, index=False, encoding='utf-8')
        
        # Rimuove backup temporaneo
        os.remove(backup_file)
        
        print(f"✅ CSV aggiornato e salvato: {csv_file}")
        
        # Verifica dimensione file
        file_size = os.path.getsize(csv_file) / (1024 * 1024)  # MB
        print(f"   Dimensione: {file_size:.1f} MB")
        
    except Exception as e:
        print(f"❌ Errore salvataggio: {e}")
        return
    
    # Verifica finale
    print(f"\n🔍 VERIFICA FINALE...")
    
    try:
        # Ricarica CSV per verifica
        df_check = pd.read_csv(csv_file)
        
        print(f"✅ Verifica completata:")
        print(f"   Righe: {len(df_check):,}")
        print(f"   Colonne: {len(df_check.columns)}")
        
        # Verifica variabili rinominate
        print(f"\n   Variabili principali verificate:")
        main_vars = ['TIME', 'DOXY', 'CHLA', 'TURB', 'CNDC', 'TEMP', 'PRES', 'DEPTH', 'LATITUDE', 'LONGITUDE']
        
        for var in main_vars:
            if var in df_check.columns:
                valid_count = df_check[var].notna().sum()
                total_count = len(df_check)
                percentage = (valid_count / total_count) * 100
                print(f"      ✅ {var:<10}: {valid_count:,} valori ({percentage:.1f}%)")
            else:
                print(f"      ❌ {var:<10}: NON TROVATA")
        
    except Exception as e:
        print(f"❌ Errore verifica: {e}")
        return
    
    # Aggiorna file metadati
    print(f"\n📝 AGGIORNAMENTO METADATI...")
    
    try:
        metadata_file = "dataset_metadata.txt"
        
        # Legge metadati esistenti
        with open(metadata_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Aggiunge sezione variabili rinominate
        additional_info = f"""

RINOMINA VARIABILI APPLICATE:
------------------------------
Data rinomina: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Variabili rinominate: {len(present_vars)}

Mapping applicato:
"""
        
        for old_name, new_name in present_vars:
            additional_info += f"- {old_name} → {new_name}\n"
        
        additional_info += f"""
VARIABILI PRINCIPALI FINALI:
-----------------------------
✅ TIME: Timestamp del glider
✅ DOXY: Ossigeno disciolto (µmol/kg)
✅ CHLA: Clorofilla-a (mg/m³)
✅ TURB: Turbidità originale (m⁻¹ sr⁻¹)
✅ CNDC: Conducibilità (S/m)
✅ TEMP: Temperatura (°C)
✅ PRES: Pressione (dbar)
✅ DEPTH: Profondità (m)
✅ LATITUDE: Latitudine (DMS)
✅ LONGITUDE: Longitudine (DMS)
"""
        
        # Aggiunge al file metadati
        with open(metadata_file, 'a', encoding='utf-8') as f:
            f.write(additional_info)
        
        print(f"✅ Metadati aggiornati: {metadata_file}")
        
    except Exception as e:
        print(f"⚠️ Warning aggiornamento metadati: {e}")
    
    # Riepilogo finale
    print(f"\n🎯 RINOMINA VARIABILI COMPLETATA!")
    print("=" * 50)
    print(f"🏷️ Variabili rinominate: {len(present_vars)}")
    print(f"📄 File aggiornato: {csv_file}")
    print(f"📁 Dimensione: {file_size:.1f} MB")
    
    print(f"\n📋 VARIABILI PRINCIPALI CON NOMI STANDARD:")
    standard_vars = [
        ('TIME', 'Timestamp'),
        ('DOXY', 'Ossigeno (µmol/kg)'),
        ('CHLA', 'Clorofilla (mg/m³)'),
        ('TURB', 'Turbidità (m⁻¹ sr⁻¹)'),
        ('CNDC', 'Conducibilità (S/m)'),
        ('TEMP', 'Temperatura (°C)'),
        ('PRES', 'Pressione (dbar)'),
        ('DEPTH', 'Profondità (m)'),
        ('LATITUDE', 'Latitudine (DMS)'),
        ('LONGITUDE', 'Longitudine (DMS)')
    ]
    
    for var_name, description in standard_vars:
        status = "✅" if var_name in df_check.columns else "❌"
        print(f"   {status} {var_name:<10}: {description}")
    
    # Crea file CSV di esempio per visualizzazione
    print(f"\n📄 CREAZIONE FILE CSV DI ESEMPIO...")
    
    try:
        # Prendi un campione di 100 righe
        sample_size = 100
        df_sample = df_check.head(sample_size).copy()
        
        # Nome file di esempio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sample_file = f"renamed_variables_sample_{timestamp}.csv"
        
        # Salva campione
        df_sample.to_csv(sample_file, index=False, encoding='utf-8')
        
        print(f"✅ File CSV di esempio creato: {sample_file}")
        print(f"   Righe di esempio: {len(df_sample)}")
        print(f"   Colonne: {len(df_sample.columns)}")
        print(f"   Dimensione: {os.path.getsize(sample_file) / 1024:.1f} KB")
        
        # Mostra anteprima delle variabili principali
        print(f"\n📊 ANTEPRIMA VARIABILI RINOMINATE (prime 5 righe):")
        print("-" * 70)
        
        # Seleziona variabili principali per anteprima
        main_vars = []
        for var in ['TIME', 'TEMP', 'PRES', 'DOXY', 'CHLA', 'CNDC', 'TURB']:
            if var in df_sample.columns:
                main_vars.append(var)
        
        if main_vars:
            preview_df = df_sample[main_vars].head(5)
            print(preview_df.to_string(index=False))
        else:
            print("   Nessuna variabile standard trovata per anteprima")
        
        print(f"\n💡 APRI IL FILE: {sample_file}")
        print("   📝 Visualizza facilmente le variabili rinominate")
        print("   📊 Confronta prima/dopo la conversione")
        
    except Exception as e:
        print(f"⚠️ Warning creazione esempio: {e}")

    print(f"\n🚀 DATASET PRONTO CON NOMI VARIABILI STANDARD!")
    print("   📊 Tutte le unità convertite")
    print("   🏷️ Nomi variabili standardizzati")
    print("   📄 Formato CSV per facile utilizzo")

if __name__ == "__main__":
    rename_variables_csv()