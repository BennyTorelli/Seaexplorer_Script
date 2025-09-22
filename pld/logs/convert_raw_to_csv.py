#!/usr/bin/env python3
"""
CONVERSIONE RAW TO CSV - SEAEXPLORER
Converte i file raw (.pld1.raw.*) del glider SeaExplorer direttamente in formato CSV
consolidato, ordinato temporalmente
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import glob

def read_glider_raw_file(file_path):
    """
    Legge un file raw del glider SeaExplorer
    """
    try:
        print(f"  📄 Lettura file: {os.path.basename(file_path)}")
        
        # Leggi il file usando punto e virgola come separatore
        data = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
        
        print(f"      Righe: {len(data):,}, Colonne: {len(data.columns)}")
        
        # Rimuovi righe completamente vuote
        data = data.dropna(how='all')
        
        # Converti il timestamp se presente
        if 'PLD_REALTIMECLOCK' in data.columns:
            try:
                data['PLD_REALTIMECLOCK'] = pd.to_datetime(data['PLD_REALTIMECLOCK'], 
                                                         format='%d/%m/%Y %H:%M:%S.%f', 
                                                         errors='coerce')
                print(f"      ✅ Timestamp convertito")
            except:
                print(f"      ⚠️ Warning: Impossibile convertire timestamp")
        
        return data
        
    except Exception as e:
        print(f"      ❌ Errore: {str(e)}")
        return None

def convert_raw_to_csv():
    """
    Converte tutti i file raw in un unico CSV
    """
    
    print("🚀 CONVERSIONE RAW → CSV - SEAEXPLORER")
    print("=" * 60)
    
    # Pattern per trovare i file raw del glider
    raw_pattern = "pld/logs/*.pld1.raw.*"
    
    # Trova tutti i file .pld1.raw.*
    print(f"\n🔍 RICERCA FILE RAW...")
    print(f"Pattern: {raw_pattern}")
    
    raw_files = glob.glob(raw_pattern)
    
    if not raw_files:
        print(f"❌ Nessun file .pld1.raw.* trovato in {raw_pattern}")
        print("💡 Verifica che i file siano nella directory pld/logs/")
        return
    
    print(f"✅ Trovati {len(raw_files)} file .pld1.raw.*")
    
    # Ordina i file numericamente (evita il problema 1,10,100,2,20...)
    def extract_number(filename):
        try:
            # Estrae il numero dal nome del file (es: sea074.67.gli.sub.123.pld1.raw.* → 123)
            parts = os.path.basename(filename).split('.')
            for part in parts:
                if part.isdigit():
                    return int(part)
            return 0
        except:
            return 0
    
    raw_files.sort(key=extract_number)
    
    print(f"📋 ORDINE FILE (primi 10):")
    for i, file in enumerate(raw_files[:10], 1):
        file_num = extract_number(file)
        print(f"   {i:2d}. {os.path.basename(file)} (num: {file_num})")
    if len(raw_files) > 10:
        print(f"   ... e altri {len(raw_files)-10} file")
    
    # Lista per raccogliere tutti i dataframe
    all_dataframes = []
    successful_files = 0
    total_rows = 0
    
    print(f"\n🔄 PROCESSAMENTO FILE...")
    
    for i, file_path in enumerate(raw_files, 1):
        print(f"\n📂 File {i}/{len(raw_files)}: {os.path.basename(file_path)}")
        
        # Leggi il file
        data = read_glider_raw_file(file_path)
        
        if data is not None and len(data) > 0:
            # Aggiungi colonna con nome file per tracciabilità
            data['source_file'] = os.path.basename(file_path)
            
            all_dataframes.append(data)
            successful_files += 1
            total_rows += len(data)
            
            print(f"      ✅ Aggiunto: {len(data):,} righe (totale: {total_rows:,})")
        else:
            print(f"      ❌ Saltato: file vuoto o errore")
        
        # Progress ogni 20 file
        if i % 20 == 0:
            print(f"\n📊 PROGRESS: {i}/{len(raw_files)} file processati, {total_rows:,} righe totali")
    
    if not all_dataframes:
        print(f"\n❌ Nessun dato valido trovato!")
        return
    
    print(f"\n🔗 CONCATENAZIONE DATAFRAME...")
    print(f"   File processati: {successful_files}/{len(raw_files)}")
    print(f"   Righe totali: {total_rows:,}")
    
    # Concatena tutti i dataframe
    try:
        combined_data = pd.concat(all_dataframes, ignore_index=True, sort=False)
        print(f"✅ Dati combinati: {len(combined_data):,} righe × {len(combined_data.columns)} colonne")
    except Exception as e:
        print(f"❌ Errore concatenazione: {e}")
        return
    
    # Informazioni sulle colonne
    print(f"\n📊 ANALISI COLONNE FINALI:")
    print("-" * 40)
    
    for i, col in enumerate(combined_data.columns, 1):
        valid_count = combined_data[col].notna().sum()
        percentage = (valid_count / len(combined_data)) * 100
        
        # Mostra solo le prime 15 colonne per non sovraccaricare
        if i <= 15:
            print(f"   {i:2d}. {col:<25} : {valid_count:>7,} ({percentage:5.1f}%)")
        elif i == 16:
            print(f"   ... e altre {len(combined_data.columns)-15} colonne")
    
    # Crea nome file output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"mission_raw_to_csv_{timestamp}.csv"
    
    print(f"\n💾 SALVATAGGIO CSV...")
    
    try:
        # Salva il CSV completo
        combined_data.to_csv(output_file, index=False, encoding='utf-8')
        
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"✅ CSV salvato: {output_file}")
        print(f"   Dimensione: {file_size:.1f} MB")
        print(f"   Righe: {len(combined_data):,}")
        print(f"   Colonne: {len(combined_data.columns)}")
        
    except Exception as e:
        print(f"❌ Errore salvataggio: {e}")
        return
    
    # CREA FILE CSV DI ESEMPIO VISUALIZZABILE
    print(f"\n📄 CREAZIONE FILE CSV DI ESEMPIO...")
    
    try:
        # Prendi un campione rappresentativo
        sample_size = 200
        
        # Prendi campione: prime 100 + ultime 100 righe
        if len(combined_data) > sample_size:
            first_half = combined_data.head(100)
            last_half = combined_data.tail(100)
            sample_data = pd.concat([first_half, last_half], ignore_index=True)
        else:
            sample_data = combined_data.copy()
        
        # Nome file di esempio
        sample_file = f"mission_raw_to_csv_SAMPLE_{timestamp}.csv"
        
        # Salva campione
        sample_data.to_csv(sample_file, index=False, encoding='utf-8')
        
        sample_size_kb = os.path.getsize(sample_file) / 1024
        print(f"✅ CSV di esempio creato: {sample_file}")
        print(f"   Righe di esempio: {len(sample_data)}")
        print(f"   Dimensione: {sample_size_kb:.1f} KB (facilmente visualizzabile)")
        
        # Mostra anteprima delle colonne principali
        print(f"\n📊 ANTEPRIMA DATI (prime 5 righe):")
        print("-" * 80)
        
        # Seleziona colonne principali per anteprima
        important_cols = []
        col_priorities = [
            'PLD_REALTIMECLOCK', 'NAV_LATITUDE', 'NAV_LONGITUDE', 'NAV_DEPTH',
            'LEGATO_TEMPERATURE', 'LEGATO_PRESSURE', 'LEGATO_CONDUCTIVITY', 
            'LEGATO_CODA_DO', 'FLBBCD_CHL_SCALED', 'FLBBCD_BB_700_SCALED'
        ]
        
        for col in col_priorities:
            if col in sample_data.columns:
                important_cols.append(col)
                if len(important_cols) >= 6:  # Limite per visualizzazione
                    break
        
        if important_cols:
            preview_df = sample_data[important_cols].head(5)
            print(preview_df.to_string(index=False))
        else:
            print("   Nessuna colonna prioritaria trovata")
            # Mostra prime 5 colonne disponibili
            preview_cols = list(sample_data.columns)[:5]
            preview_df = sample_data[preview_cols].head(5)
            print(preview_df.to_string(index=False))
        
        print(f"\n💡 APRI I FILE:")
        print(f"   📊 Dataset completo: {output_file}")
        print(f"   👁️ Anteprima: {sample_file} ← QUESTO È FACILMENTE VISUALIZZABILE")
        
    except Exception as e:
        print(f"⚠️ Warning creazione esempio: {e}")
    
    # Crea metadati
    print(f"\n📝 CREAZIONE METADATI...")
    
    try:
        metadata_file = f"raw_to_csv_metadata_{timestamp}.txt"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write("CONVERSIONE RAW TO CSV - SEAEXPLORER\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Data conversione: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"File processati: {successful_files}/{len(raw_files)}\n")
            f.write(f"Righe totali: {len(combined_data):,}\n")
            f.write(f"Colonne totali: {len(combined_data.columns)}\n")
            f.write(f"Dimensione CSV: {file_size:.1f} MB\n\n")
            
            f.write("FILE GENERATI:\n")
            f.write(f"- Dataset completo: {output_file}\n")
            f.write(f"- Campione visualizzabile: {sample_file}\n")
            f.write(f"- Metadati: {metadata_file}\n\n")
            
            f.write("COLONNE NEL DATASET:\n")
            for i, col in enumerate(combined_data.columns, 1):
                valid_count = combined_data[col].notna().sum()
                percentage = (valid_count / len(combined_data)) * 100
                f.write(f"{i:2d}. {col:<30} : {valid_count:>7,} valori ({percentage:5.1f}%)\n")
        
        print(f"✅ Metadati salvati: {metadata_file}")
        
    except Exception as e:
        print(f"⚠️ Warning metadati: {e}")
    
    # RIEPILOGO FINALE
    print(f"\n🎯 CONVERSIONE RAW → CSV COMPLETATA!")
    print("=" * 60)
    print(f"📂 File processati: {successful_files}/{len(raw_files)}")
    print(f"📊 Dati convertiti: {len(combined_data):,} righe × {len(combined_data.columns)} colonne")
    print(f"💾 CSV principale: {output_file} ({file_size:.1f} MB)")
    print(f"👁️ CSV visualizzabile: {sample_file} ({sample_size_kb:.1f} KB)")
    print(f"📝 Metadati: {metadata_file}")
    
    print(f"\n💡 PROSSIMI PASSI:")
    print(f"1. 👁️ Apri {sample_file} per vedere l'anteprima")
    print(f"2. 📊 Usa {output_file} per analisi complete")
    print(f"3. 🏷️ Applica script rinomina variabili se necessario")
    print(f"4. 🔄 Applica conversioni unità se necessario")
    
    print(f"\n🚀 CONVERSIONE COMPLETATA CON SUCCESSO!")

if __name__ == "__main__":
    convert_raw_to_csv()