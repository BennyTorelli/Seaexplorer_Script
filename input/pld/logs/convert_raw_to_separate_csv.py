#!/usr/bin/env python3
"""
CONVERSIONE RAW TO CSV SEPARATI - SEAEXPLORER
Converte i file raw (.pld1.raw.*) del glider SeaExplorer in file CSV separati
mantenendo l'ordine numerico da 1 a 183
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

def extract_number(filename):
    """
    Estrae il numero dal nome del file per ordinamento numerico corretto
    """
    try:
        # Estrae il numero dal nome del file (es: sea074.67.pld1.raw.123 → 123)
        # Cerca il numero DOPO "raw."
        if "raw." in filename:
            # Prende tutto dopo "raw."
            after_raw = filename.split("raw.")[-1]
            # Rimuove eventuali spazi e cerca il numero
            number_part = after_raw.strip().split()[0]
            if number_part.isdigit():
                return int(number_part)
        return 0
    except:
        return 0

def convert_raw_to_separate_csv():
    """
    Converte ogni file raw in un CSV separato
    """
    
    print("🚀 CONVERSIONE RAW → CSV SEPARATI - SEAEXPLORER")
    print("=" * 60)
    print("Ogni file .pld1.raw.X diventa un file CSV separato")
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
    
    # Ordina i file numericamente
    raw_files.sort(key=extract_number)
    
    # Filtra solo i file da 1 a 183 (escludi 0 e duplicati)
    filtered_files = []
    for file_path in raw_files:
        file_num = extract_number(file_path)
        if 1 <= file_num <= 183:
            filtered_files.append(file_path)
    
    print(f"📋 FILE DA CONVERTIRE (1-183): {len(filtered_files)}")
    file_numbers = [extract_number(f) for f in filtered_files]
    print(f"   Range: {min(file_numbers)} → {max(file_numbers)}")
    print(f"   File mancanti: {set(range(1, 184)) - set(file_numbers)}")
    
    # Crea directory per i CSV separati se non esiste
    output_dir = "csv_separati"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Creata directory: {output_dir}")
    
    successful_files = 0
    total_rows = 0
    conversion_log = []
    
    print(f"\n🔄 CONVERSIONE FILE INDIVIDUALI...")
    
    for i, file_path in enumerate(filtered_files, 1):
        file_num = extract_number(file_path)
        print(f"\n📂 File {i}/{len(filtered_files)}: {os.path.basename(file_path)} (#{file_num})")
        
        # Leggi il file raw
        data = read_glider_raw_file(file_path)
        
        if data is not None and len(data) > 0:
            # Nome file CSV output
            csv_filename = f"mission_{file_num:03d}.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            
            try:
                # Aggiungi metadati
                data['source_file'] = os.path.basename(file_path)
                data['file_number'] = file_num
                
                # Salva CSV
                data.to_csv(csv_path, index=False, encoding='utf-8')
                file_size_kb = os.path.getsize(csv_path) / 1024
                
                successful_files += 1
                total_rows += len(data)
                conversion_log.append({
                    'number': file_num,
                    'raw_file': os.path.basename(file_path),
                    'csv_file': csv_filename,
                    'rows': len(data),
                    'size_kb': file_size_kb
                })
                
                print(f"      ✅ {csv_filename}: {len(data):,} righe, {file_size_kb:.1f} KB")
                
            except Exception as e:
                print(f"      ❌ Errore salvataggio: {e}")
        else:
            print(f"      ❌ File vuoto o errore lettura")
        
        # Progress ogni 20 file
        if i % 20 == 0:
            print(f"\n📊 PROGRESS: {i}/{len(filtered_files)} file, {successful_files} successi, {total_rows:,} righe totali")
    
    if successful_files == 0:
        print(f"\n❌ Nessun file convertito con successo!")
        return
    
    # Statistiche finali
    print(f"\n📊 STATISTICHE CONVERSIONE:")
    print("-" * 40)
    print(f"File raw processati: {len(filtered_files)}")
    print(f"CSV creati: {successful_files}")
    print(f"Righe totali: {total_rows:,}")
    print(f"Directory output: {output_dir}")
    
    # Salva metadati conversione
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metadata_file = f"csv_separati_metadata_{timestamp}.txt"
    
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write("CONVERSIONE RAW TO CSV SEPARATI - SEAEXPLORER\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Data conversione: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"File raw processati: {len(filtered_files)}\n")
            f.write(f"CSV creati: {successful_files}\n")
            f.write(f"Righe totali: {total_rows:,}\n")
            f.write(f"Directory output: {output_dir}\n\n")
            f.write("FILE CONVERTITI:\n")
            f.write("-" * 50 + "\n")
            
            for log_entry in conversion_log:
                f.write(f"{log_entry['number']:3d}. {log_entry['csv_file']:<20} "
                       f"← {log_entry['raw_file']:<30} "
                       f"({log_entry['rows']:>6,} righe, {log_entry['size_kb']:>6.1f} KB)\n")
            
            # File mancanti
            missing_files = set(range(1, 184)) - set([log['number'] for log in conversion_log])
            if missing_files:
                f.write(f"\nFILE MANCANTI: {sorted(missing_files)}\n")
        
        print(f"✅ Metadati salvati: {metadata_file}")
    except Exception as e:
        print(f"⚠️ Warning metadati: {e}")
    
    # RIEPILOGO FINALE
    print(f"\n🎯 CONVERSIONE COMPLETATA!")
    print("=" * 60)
    print(f"📂 CSV creati: {successful_files}/183 file in {output_dir}/")
    print(f"📊 Dati convertiti: {total_rows:,} righe totali")
    print(f"📝 Metadati: {metadata_file}")
    print(f"\n💡 PROSSIMI PASSI:")
    print(f"1. 📁 Controlla i file in {output_dir}/")
    print(f"2. 🔗 Usa lo script merge per unire i CSV in ordine")
    print(f"3. 📊 Verifica che i file siano ordinati da 1 a 183")

if __name__ == "__main__":
    convert_raw_to_separate_csv()