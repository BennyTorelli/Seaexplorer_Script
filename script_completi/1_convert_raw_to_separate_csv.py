#!/usr/bin/env python3
"""
RAW TO SEPARATE CSV CONVERSION - SEAEXPLORER
Converts raw files (.pld1.raw.*) from SeaExplorer glider to separate CSV files
maintaining numerical order from 1 to 183
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import glob

def read_glider_raw_file(file_path):
    """
    Reads a SeaExplorer glider raw file
    """
    try:
        print(f"  📄 Reading file: {os.path.basename(file_path)}")
        # Read file using semicolon as separator
        data = pd.read_csv(file_path, delimiter=';', encoding='utf-8')
        print(f"      Rows: {len(data):,}, Columns: {len(data.columns)}")
        
        # Remove completely empty rows
        data = data.dropna(how='all')
        
        # Convert timestamp if present
        if 'PLD_REALTIMECLOCK' in data.columns:
            try:
                data['PLD_REALTIMECLOCK'] = pd.to_datetime(data['PLD_REALTIMECLOCK'],
                                                         format='%d/%m/%Y %H:%M:%S.%f',
                                                         errors='coerce')
                print(f"      ✅ Timestamp converted")
            except:
                print(f"      ⚠️ Warning: Unable to convert timestamp")
        
        return data
    except Exception as e:
        print(f"      ❌ Error: {str(e)}")
        return None

def extract_number(filename):
    """
    Extracts number from filename for correct numerical sorting
    """
    try:
        # Extract number from filename (e.g: sea074.67.pld1.raw.123 → 123)
        # Search for number AFTER "raw."
        if "raw." in filename:
            # Take everything after "raw."
            after_raw = filename.split("raw.")[-1]
            # Remove spaces and find the number
            number_part = after_raw.strip().split()[0]
            if number_part.isdigit():
                return int(number_part)
        return 0
    except:
        return 0

def convert_raw_to_separate_csv():
    """
    Converts each raw file to a separate CSV
    """
    
    print("🚀 RAW → SEPARATE CSV CONVERSION - SEAEXPLORER")
    print("=" * 60)
    print("Each .pld1.raw.X file becomes a separate CSV file")
    print("=" * 60)
    
    # Pattern to find glider raw files
    raw_pattern = "pld/logs/*.pld1.raw.*"
    
    # Find all .pld1.raw.* files
    print(f"\n🔍 SEARCHING RAW FILES...")
    print(f"Pattern: {raw_pattern}")
    
    raw_files = glob.glob(raw_pattern)
    
    if not raw_files:
        print(f"❌ No .pld1.raw.* files found in {raw_pattern}")
        print("💡 Verify files are in pld/logs/ directory")
        return
    
    print(f"✅ Found {len(raw_files)} .pld1.raw.* files")
    
    # Sort files numerically
    raw_files.sort(key=extract_number)
    
    # Filter only files from 1 to 183 (exclude 0 and duplicates)
    filtered_files = []
    for file_path in raw_files:
        file_num = extract_number(file_path)
        if 1 <= file_num <= 183:
            filtered_files.append(file_path)
    
    print(f"📋 FILES TO CONVERT (1-183): {len(filtered_files)}")
    file_numbers = [extract_number(f) for f in filtered_files]
    print(f"   Range: {min(file_numbers)} → {max(file_numbers)}")
    print(f"   Missing files: {set(range(1, 184)) - set(file_numbers)}")
    
    # Create directory for separate CSVs if it doesn't exist
    output_dir = "csv_separati"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created directory: {output_dir}")
    
    successful_files = 0
    total_rows = 0
    conversion_log = []
    
    print(f"\n🔄 CONVERTING INDIVIDUAL FILES...")
    
    for i, file_path in enumerate(filtered_files, 1):
        file_num = extract_number(file_path)
        print(f"\n📂 File {i}/{len(filtered_files)}: {os.path.basename(file_path)} (#{file_num})")
        
        # Read the raw file
        data = read_glider_raw_file(file_path)
        
        if data is not None and len(data) > 0:
            # CSV output filename
            csv_filename = f"mission_{file_num:03d}.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            
            try:
                # Add metadata
                data['source_file'] = os.path.basename(file_path)
                data['file_number'] = file_num
                
                # Save CSV
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
                
                print(f"      ✅ {csv_filename}: {len(data):,} rows, {file_size_kb:.1f} KB")
                
            except Exception as e:
                print(f"      ❌ Save error: {e}")
        else:
            print(f"      ❌ Empty file or read error")
        
        # Progress every 20 files
        if i % 20 == 0:
            print(f"\n📊 PROGRESS: {i}/{len(filtered_files)} files, {successful_files} successful, {total_rows:,} total rows")
    
    if successful_files == 0:
        print(f"\n❌ No files converted successfully!")
        return
    
    # Final statistics
    print(f"\n📊 CONVERSION STATISTICS:")
    print("-" * 40)
    print(f"Raw files processed: {len(filtered_files)}")
    print(f"CSVs created: {successful_files}")
    print(f"Total rows: {total_rows:,}")
    print(f"Output directory: {output_dir}")
    
    # Save conversion metadata
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metadata_file = f"csv_separati_metadata_{timestamp}.txt"
    
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write("RAW TO SEPARATE CSV CONVERSION - SEAEXPLORER\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Conversion date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Raw files processed: {len(filtered_files)}\n")
            f.write(f"CSVs created: {successful_files}\n")
            f.write(f"Total rows: {total_rows:,}\n")
            f.write(f"Output directory: {output_dir}\n\n")
            f.write("CONVERTED FILES:\n")
            f.write("-" * 50 + "\n")
            
            for log_entry in conversion_log:
                f.write(f"{log_entry['number']:3d}. {log_entry['csv_file']:<20} "
                       f"← {log_entry['raw_file']:<30} "
                       f"({log_entry['rows']:>6,} rows, {log_entry['size_kb']:>6.1f} KB)\n")
            
            # Missing files
            missing_files = set(range(1, 184)) - set([log['number'] for log in conversion_log])
            if missing_files:
                f.write(f"\nMISSING FILES: {sorted(missing_files)}\n")
        
        print(f"✅ Metadata saved: {metadata_file}")
    except Exception as e:
        print(f"⚠️ Warning metadata: {e}")
    
    # FINAL SUMMARY
    print(f"\n🎯 CONVERSION COMPLETED!")
    print("=" * 60)
    print(f"📂 CSVs created: {successful_files}/183 files in {output_dir}/")
    print(f"📊 Data converted: {total_rows:,} total rows")
    print(f"📝 Metadata: {metadata_file}")
    print(f"\n💡 NEXT STEPS:")
    print(f"1. 📁 Check files in {output_dir}/")
    print(f"2. 🔗 Use merge script to combine CSVs in order")
    print(f"3. 📊 Verify files are ordered from 1 to 183")

if __name__ == "__main__":
    convert_raw_to_separate_csv()