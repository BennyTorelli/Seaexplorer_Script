#!/usr/bin/env python3
"""
MERGE MISSION DATA - CSV VERSION
Unisce più file CSV di missione del glider SeaExplorer in un unico dataset completo
Ordinamento numerico corretto e gestione memoria ottimizzata
"""

import pandas as pd
import glob
import os
import re
from datetime import datetime
import numpy as np

def extract_file_number(filename):
    """
    Estrae il numero dal filename per ordinamento numerico corretto
    Supporta vari formati: mission_001.csv, sea074.67.xxx.csv, etc.
    """
    # Pattern per diversi formati (in ordine di priorità)
    patterns = [
        r'mission_(\d+)\.csv$',  # mission_001.csv, mission_123.csv
        r'_(\d+)\.csv$',         # qualsiasi_123.csv
        r'\.(\d+)\.csv$',        # sea074.67.123.csv
        r'(\d+)\.csv$',          # 123.csv
        r'\.sub\.(\d+)',         # .sub.123.
        r'\.raw\.(\d+)',         # .raw.123.
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            return int(match.group(1))
    
    return 0

def analyze_csv_files(file_paths):
    """
    Analizza i file CSV per verificare compatibilità e struttura
    """
    print(f"\n🔍 ANALISI FILE CSV...")
    
    sample_files = file_paths[:3]  # Analizza primi 3 file
    columns_info = {}
    
    for file_path in sample_files:
        try:
            # Leggi solo header per analisi veloce
            df_sample = pd.read_csv(file_path, nrows=5)
            file_num = extract_file_number(file_path)
            
            print(f"   📄 {os.path.basename(file_path)} (#{file_num})")
            print(f"      Colonne: {len(df_sample.columns)}")
            
            # Salva info colonne del primo file come riferimento
            if not columns_info:
                columns_info = {
                    'reference_file': file_path,
                    'columns': list(df_sample.columns),
                    'count': len(df_sample.columns)
                }
            else:
                # Verifica compatibilità
                if set(df_sample.columns) != set(columns_info['columns']):
                    print(f"      ⚠️ Colonne diverse dal file di riferimento")
                else:
                    print(f"      ✅ Colonne compatibili")
                    
        except Exception as e:
            print(f"      ❌ Errore lettura: {e}")
    
    return columns_info

def merge_csv_files():
    """
    Unisce più file CSV in un unico dataset di missione
    """
    
    print("🚀 MERGE MISSION DATA - CSV VERSION")
    print("=" * 60)
    print("Unisce più file CSV del glider in un unico dataset completo")
    print("=" * 60)
    
    # Pattern per trovare i file CSV di missione
    patterns = [
        "csv_separati/mission_*.csv",  # File mission separati (PRIORITÀ)
        "csv_separati/*.csv",          # Tutti i CSV nella cartella separati
        "mission_*.csv",               # File mission specifici
        "*.csv",                       # Tutti i CSV nella directory corrente
        "sea074*.csv",                 # File SeaExplorer specifici
        "netcdf_output/*.csv",         # CSV nella cartella output
        "pld/logs/*.csv"               # CSV nella cartella pld/logs
    ]
    
    print(f"\n🔍 RICERCA FILE CSV...")
    all_files = []
    
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            print(f"   Pattern '{pattern}': {len(files)} file")
            all_files.extend(files)
    
    # Rimuovi duplicati e ordina
    file_paths = list(set(all_files))
    
    if not file_paths:
        print(f"❌ Nessun file CSV trovato!")
        print(f"💡 Patterns cercati: {patterns}")
        print(f"💡 Directory corrente: {os.getcwd()}")
        return None
    
    # Filtra file validi (esclude file già mergiati, sample, etc.)
    valid_files = []
    excluded_keywords = ['merged', 'complete', 'sample', 'metadata', 'units_converted', 'backup']
    
    for file_path in file_paths:
        filename = os.path.basename(file_path).lower()
        
        # Salta file che contengono parole chiave di esclusione
        if any(keyword in filename for keyword in excluded_keywords):
            print(f"   ⏭️ Escluso: {os.path.basename(file_path)} (già processato)")
            continue
        
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        
        # Salta file troppo grandi (probabilmente già uniti) o troppo piccoli
        if 0.01 <= file_size <= 100:  # Tra 0.01MB e 100MB (adattato per file separati)
            valid_files.append(file_path)
        else:
            print(f"   ⏭️ Saltato {os.path.basename(file_path)} ({file_size:.1f} MB)")
    
    file_paths = valid_files
    
    if not file_paths:
        print(f"❌ Nessun file CSV valido trovato dopo il filtro!")
        return None
    
    print(f"✅ Trovati {len(file_paths)} file CSV validi")
    
    # ORDINAMENTO NUMERICO CORRETTO
    print(f"\n📋 ORDINAMENTO FILE...")
    file_paths.sort(key=extract_file_number)
    
    # Mostra ordine
    file_numbers = [extract_file_number(f) for f in file_paths]
    print(f"   Primo file: {os.path.basename(file_paths[0])} (#{file_numbers[0]})")
    print(f"   Ultimo file: {os.path.basename(file_paths[-1])} (#{file_numbers[-1]})")
    print(f"   Range numeri: {min(file_numbers)} → {max(file_numbers)}")
    
    if len(file_paths) <= 20:
        print(f"   Ordine completo: {file_numbers}")
    else:
        print(f"   Primi 10: {file_numbers[:10]}")
        print(f"   Ultimi 10: {file_numbers[-10:]}")
    
    # Verifica ordine
    if file_numbers != sorted(file_numbers):
        print("⚠️ ATTENZIONE: Ordine potrebbe non essere corretto")
    else:
        print("✅ Ordine numerico verificato")
    
    # Analizza struttura file
    columns_info = analyze_csv_files(file_paths)
    
    # Merge dei file
    print(f"\n🔗 MERGE FILE CSV...")
    
    all_dataframes = []
    total_rows = 0
    successful_files = 0
    
    for i, file_path in enumerate(file_paths, 1):
        try:
            file_num = extract_file_number(file_path)
            file_size = os.path.getsize(file_path) / 1024  # KB
            
            print(f"\n📂 File {i}/{len(file_paths)}: {os.path.basename(file_path)}")
            print(f"      Numero: #{file_num}, Dimensione: {file_size:.1f} KB")
            
            # Leggi CSV
            df = pd.read_csv(file_path)
            
            if len(df) == 0:
                print(f"      ⚠️ File vuoto, saltato")
                continue
            
            # Aggiungi colonne di tracciabilità
            df['source_file'] = os.path.basename(file_path)
            df['file_number'] = file_num
            df['merge_position'] = i
            
            all_dataframes.append(df)
            successful_files += 1
            total_rows += len(df)
            
            print(f"      ✅ Aggiunto: {len(df):,} righe (totale: {total_rows:,})")
            
            # Progress ogni 10 file
            if i % 10 == 0:
                print(f"\n📊 PROGRESS: {i}/{len(file_paths)} file, {total_rows:,} righe totali")
                
        except Exception as e:
            print(f"      ❌ Errore: {e}")
            continue
    
    if not all_dataframes:
        print(f"\n❌ Nessun file caricato con successo!")
        return None
    
    print(f"\n🔗 CONCATENAZIONE FINALE...")
    print(f"   File processati: {successful_files}/{len(file_paths)}")
    print(f"   Righe totali: {total_rows:,}")
    
    try:
        # Concatena tutti i dataframe
        merged_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
        
        print(f"✅ Dataset unito: {len(merged_df):,} righe × {len(merged_df.columns)} colonne")
        
        # Ordina per colonna temporale se presente
        time_columns = ['time', 'timestamp', 'PLD_REALTIMECLOCK', 'TIME']
        sort_column = None
        
        for col in time_columns:
            if col in merged_df.columns:
                sort_column = col
                break
        
        if sort_column:
            print(f"   📅 Ordinamento per colonna temporale: {sort_column}")
            merged_df = merged_df.sort_values(sort_column).reset_index(drop=True)
            print(f"   ✅ Dataset ordinato temporalmente")
        
    except Exception as e:
        print(f"❌ Errore concatenazione: {e}")
        return None
    
    # Salvataggio
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"mission_complete_merged_{timestamp}.csv"
    
    print(f"\n💾 SALVATAGGIO DATASET UNITO...")
    
    try:
        # Salva dataset completo
        merged_df.to_csv(output_file, index=False, encoding='utf-8')
        
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"✅ Dataset salvato: {output_file}")
        print(f"   Dimensione: {file_size:.1f} MB")
        print(f"   Righe: {len(merged_df):,}")
        print(f"   Colonne: {len(merged_df.columns)}")
        
    except Exception as e:
        print(f"❌ Errore salvataggio: {e}")
        return None
    
    # CREA FILE DI ESEMPIO VISUALIZZABILE
    print(f"\n📄 CREAZIONE FILE CSV DI ESEMPIO...")
    
    try:
        # Campione rappresentativo
        sample_size = 500
        
        if len(merged_df) > sample_size:
            # Prendi campioni da inizio, metà e fine
            third = len(merged_df) // 3
            start_sample = merged_df.head(150)
            mid_sample = merged_df.iloc[third:third+200]
            end_sample = merged_df.tail(150)
            
            sample_df = pd.concat([start_sample, mid_sample, end_sample], ignore_index=True)
        else:
            sample_df = merged_df.copy()
        
        # File di esempio
        sample_file = f"mission_complete_merged_SAMPLE_{timestamp}.csv"
        sample_df.to_csv(sample_file, index=False, encoding='utf-8')
        
        sample_size_kb = os.path.getsize(sample_file) / 1024
        print(f"✅ CSV di esempio: {sample_file}")
        print(f"   Righe: {len(sample_df)}")
        print(f"   Dimensione: {sample_size_kb:.1f} KB (visualizzabile)")
        
        # Anteprima dati
        print(f"\n📊 ANTEPRIMA DATASET UNITO (prime 5 righe):")
        print("-" * 80)
        
        # Colonne prioritarie per anteprima
        priority_cols = [
            'time', 'timestamp', 'PLD_REALTIMECLOCK', 'TIME',
            'NAV_LATITUDE', 'NAV_LONGITUDE', 'NAV_DEPTH',
            'LEGATO_TEMPERATURE', 'LEGATO_PRESSURE', 'source_file'
        ]
        
        display_cols = []
        for col in priority_cols:
            if col in sample_df.columns:
                display_cols.append(col)
                if len(display_cols) >= 6:
                    break
        
        if display_cols:
            preview_df = sample_df[display_cols].head(5)
            print(preview_df.to_string(index=False))
        else:
            # Fallback: prime colonne disponibili
            display_cols = list(sample_df.columns)[:6]
            preview_df = sample_df[display_cols].head(5)
            print(preview_df.to_string(index=False))
        
    except Exception as e:
        print(f"⚠️ Warning esempio: {e}")
    
    # Metadati
    print(f"\n📝 CREAZIONE METADATI...")
    
    try:
        metadata_file = f"mission_merge_metadata_{timestamp}.txt"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write("MERGE MISSION DATA - CSV\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Data merge: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"File processati: {successful_files}/{len(file_paths)}\n")
            f.write(f"Righe totali: {len(merged_df):,}\n")
            f.write(f"Colonne totali: {len(merged_df.columns)}\n")
            f.write(f"Range file numbers: {min(file_numbers)} → {max(file_numbers)}\n")
            f.write(f"Ordinamento: Numerico corretto\n\n")
            
            f.write("FILE GENERATI:\n")
            f.write(f"- Dataset completo: {output_file}\n")
            f.write(f"- Campione: {sample_file}\n")
            f.write(f"- Metadati: {metadata_file}\n\n")
            
            f.write("COLONNE NEL DATASET:\n")
            for i, col in enumerate(merged_df.columns, 1):
                valid_count = merged_df[col].notna().sum()
                percentage = (valid_count / len(merged_df)) * 100
                f.write(f"{i:2d}. {col:<25} : {valid_count:>8,} valori ({percentage:5.1f}%)\n")
            
            f.write("\nFILE SORGENTE PROCESSATI:\n")
            for i, file_path in enumerate(file_paths[:successful_files], 1):
                file_num = extract_file_number(file_path)
                f.write(f"{i:3d}. {os.path.basename(file_path):<30} (#{file_num})\n")
        
        print(f"✅ Metadati: {metadata_file}")
        
    except Exception as e:
        print(f"⚠️ Warning metadati: {e}")
    
    # RIEPILOGO FINALE
    print(f"\n🎯 MERGE MISSION DATA COMPLETATO!")
    print("=" * 60)
    print(f"📂 File uniti: {successful_files}")
    print(f"📊 Dataset finale: {len(merged_df):,} righe × {len(merged_df.columns)} colonne")
    print(f"💾 Dataset completo: {output_file} ({file_size:.1f} MB)")
    print(f"👁️ Anteprima: {sample_file} ({sample_size_kb:.1f} KB)")
    print(f"📝 Metadati: {metadata_file}")
    
    print(f"\n💡 PROSSIMI PASSI:")
    print(f"1. 👁️ Apri {sample_file} per vedere il risultato")
    print(f"2. 🏷️ Applica script rinomina variabili se necessario")
    print(f"3. 🔄 Applica conversioni unità se necessario")
    print(f"4. 📊 Usa {output_file} per analisi complete")
    
    print(f"\n🚀 MISSIONE UNITA CON SUCCESSO!")
    
    return merged_df

if __name__ == "__main__":
    merged_dataset = merge_csv_files()
    if merged_dataset is not None:
        print("\n🎉 MERGE COMPLETATO CON SUCCESSO!")
    else:
        print("\n💥 MERGE FALLITO - controllare errori sopra")