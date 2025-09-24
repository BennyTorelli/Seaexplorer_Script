#!/usr/bin/env python3
"""
RIEPILOGO PIPELINE SEQUENZIALE
===============================

Questo script mostra lo stato attuale della pipeline di elaborazione dati SeaExplorer
e dimostra come i quattro script principali dovrebbero funzionare insieme sequenzialmente.

Ordine Pipeline:
1. convert_raw_to_separate_csv.py   → Crea file individuali mission_XXX.csv (1-183)
2. merge_mission_data_csv.py        → Unisce tutti i file in un singolo mission_complete_merged_XXX.csv
3. convert_all_units_csv.py         → Converte unità → mission_complete_merged_units_converted_XXX.csv
4. rename_variables_csv.py          → Rinomina variabili → mission_complete_merged_units_converted_renamed_XXX.csv

Ogni script dà priorità all'output dello script precedente per assicurare elaborazione sequenziale appropriata.
"""

import os
import glob
from datetime import datetime

def get_file_info(file_path):
    """Ottiene dimensione file e ora modifica"""
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
    return size_mb, mod_time

def analyze_pipeline_files():
    """Analizza stato attuale file pipeline"""
    
    print("=" * 80)
    print("🔍 PIPELINE ELABORAZIONE DATI SEAEXPLORER - STATO ATTUALE")
    print("=" * 80)
    
    # 1. Analisi file raw
    print("\n1️⃣ FILE RAW (.pld1.raw)")
    print("-" * 40)
    raw_files = glob.glob("*.pld1.raw")
    if raw_files:
        print(f"✅ Trovati {len(raw_files)} file raw")
        
        # Controlla gap nella numerazione
        numbers = []
        for file in raw_files:
            try:
                # Estrae numero dopo "raw."
                if '.raw.' in file:
                    num_str = file.split('.raw.')[1]
                    numbers.append(int(num_str))
            except:
                continue
        
        if numbers:
            numbers.sort()
            print(f"   📊 Range: {min(numbers)} - {max(numbers)}")
            
            # Controlla gap
            expected = set(range(1, 184))  # 1-183
            actual = set(numbers)
            missing = expected - actual
            extra = actual - expected
            
            if missing:
                print(f"   ❌ File mancanti: {sorted(list(missing))[:10]}{'...' if len(missing) > 10 else ''}")
            if extra:
                print(f"   ⚠️ File extra: {sorted(list(extra))[:10]}{'...' if len(extra) > 10 else ''}")
            if not missing and not extra:
                print(f"   ✅ Sequenza completa 1-183!")
    else:
        print("❌ Nessun file raw trovato")
    
    # 2. Analisi file CSV separati
    print("\n2️⃣ FILE CSV SEPARATI (mission_XXX.csv)")
    print("-" * 40)
    
    # Controlla directory csv_separati
    separate_dir = "csv_separati"
    if os.path.exists(separate_dir):
        separate_files = glob.glob(f"{separate_dir}/mission_*.csv")
        if separate_files:
            print(f"✅ Trovati {len(separate_files)} file CSV separati in {separate_dir}/")
            
            # Controlla numerazione
            numbers = []
            for file in separate_files:
                try:
                    filename = os.path.basename(file)
                    if filename.startswith('mission_') and filename.endswith('.csv'):
                        num_str = filename[8:-4]  # Estrae numero
                        numbers.append(int(num_str))
                except:
                    continue
            
            if numbers:
                numbers.sort()
                print(f"   📊 Range: {min(numbers)} - {max(numbers)}")
                if len(numbers) == 183 and min(numbers) == 1 and max(numbers) == 183:
                    print(f"   ✅ Sequenza completa 1-183!")
        else:
            print(f"❌ Nessun file CSV separato trovato in {separate_dir}/")
    else:
        print(f"❌ Directory {separate_dir}/ non trovata")
    
    # 3. Analisi file uniti
    print("\n3️⃣ FILE UNITI (mission_complete_merged_*.csv)")
    print("-" * 40)
    merged_files = glob.glob("*merged*.csv")
    merged_files = [f for f in merged_files if 'complete' in f and 'units_converted' not in f and 'renamed' not in f]
    
    if merged_files:
        merged_files.sort(key=os.path.getmtime, reverse=True)
        latest = merged_files[0]
        size_mb, mod_time = get_file_info(latest)
        print(f"✅ File unito più recente: {latest}")
        print(f"   📊 Dimensione: {size_mb:.1f} MB")
        print(f"   📅 Modificato: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if len(merged_files) > 1:
            print(f"   📁 File uniti totali: {len(merged_files)}")
    else:
        print("❌ Nessun file unito trovato")
    
    # 4. Analisi file unità convertite
    print("\n4️⃣ FILE UNITÀ CONVERTITE (*units_converted*.csv)")
    print("-" * 40)
    units_files = glob.glob("*units_converted*.csv")
    units_files = [f for f in units_files if 'renamed' not in f]
    
    if units_files:
        units_files.sort(key=os.path.getmtime, reverse=True)
        latest = units_files[0]
        size_mb, mod_time = get_file_info(latest)
        print(f"✅ File unità convertite più recente: {latest}")
        print(f"   📊 Dimensione: {size_mb:.1f} MB")
        print(f"   📅 Modificato: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if len(units_files) > 1:
            print(f"   📁 File unità convertite totali: {len(units_files)}")
    else:
        print("❌ Nessun file unità convertite trovato")
    
    # 5. Analisi file rinominati
    print("\n5️⃣ FILE RINOMINATI (*renamed*.csv)")
    print("-" * 40)
    renamed_files = glob.glob("*renamed*.csv")
    
    if renamed_files:
        renamed_files.sort(key=os.path.getmtime, reverse=True)
        latest = renamed_files[0]
        size_mb, mod_time = get_file_info(latest)
        print(f"✅ File rinominato più recente: {latest}")
        print(f"   📊 Dimensione: {size_mb:.1f} MB")
        print(f"   📅 Modificato: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if len(renamed_files) > 1:
            print(f"   📁 File rinominati totali: {len(renamed_files)}")
    else:
        print("❌ Nessun file rinominato trovato")
    
    # Raccomandazioni pipeline
    print("\n" + "=" * 80)
    print("🎯 RACCOMANDAZIONI PIPELINE")
    print("=" * 80)
    
    if not raw_files:
        print("❌ Inizia con file raw - assicurati che i file *.pld1.raw siano disponibili")
    elif not separate_files if 'separate_files' in locals() else True:
        print("🔄 Esegui: python convert_raw_to_separate_csv.py")
        print("   → Questo creerà file individuali mission_XXX.csv")
    elif not merged_files:
        print("🔄 Esegui: python merge_mission_data_csv.py")
        print("   → Questo unirà tutti i file separati in uno")
    elif not units_files:
        print("🔄 Esegui: python convert_all_units_csv.py")
        print("   → Questo convertirà le unità di misura")
    elif not renamed_files:
        print("🔄 Esegui: python rename_variables_csv.py")
        print("   → Questo rinominerà le variabili con nomi standard")
    else:
        print("✅ Pipeline sembra completa!")
        print("   Tutti i passi di elaborazione sono stati eseguiti")
    
    print("\n💡 NOTA: Ogni script seleziona automaticamente il file input corretto")
    print("   basato sulla logica di priorità implementata in ogni script.")

if __name__ == "__main__":
    analyze_pipeline_files()