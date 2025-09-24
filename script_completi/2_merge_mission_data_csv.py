#!/usr/bin/env python3
"""
MERGE MISSION DATA - CSV VERSION
Merges separate CSV files (mission_001.csv, mission_002.csv, etc.) 
into a single complete mission dataset in proper numerical order
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import glob
import re

def extract_file_number(filename):
    """
    Extracts number from filename for correct numerical sorting
    Supports various formats: mission_001.csv, sea074.67.xxx.csv, etc.
    """
    # Pattern for different formats (in priority order)
    patterns = [
        r'mission_(\d+)\.csv$',  # mission_001.csv, mission_123.csv
        r'_(\d+)\.csv$',         # anything_123.csv
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
    Analyzes CSV files to verify compatibility and structure
    """
    print(f"\n🔍 CSV FILE ANALYSIS...")
    
    sample_files = file_paths[:3]  # Analyze first 3 files
    columns_info = {}
    
    for file_path in sample_files:
        try:
            # Read only header for fast analysis
            df_sample = pd.read_csv(file_path, nrows=5)
            file_num = extract_file_number(file_path)
            
            print(f"   📄 {os.path.basename(file_path)} (#{file_num})")
            print(f"      Columns: {len(df_sample.columns)}")
            
            # Save column info from first file as reference
            if not columns_info:
                columns_info = {
                    'reference_file': file_path,
                    'columns': list(df_sample.columns),
                    'count': len(df_sample.columns)
                }
            else:
                # Verify compatibility
                if set(df_sample.columns) != set(columns_info['columns']):
                    print(f"      ⚠️ Different columns from reference file")
                else:
                    print(f"      ✅ Compatible columns")
                    
        except Exception as e:
            print(f"      ❌ Read error: {e}")
    
    return columns_info

def merge_csv_files():
    """
    Merges multiple CSV files into a single mission dataset
    """
    
    print("🚀 MERGE MISSION DATA - CSV VERSION")
    print("=" * 60)
    print("Merges multiple glider CSV files into a single complete dataset")
    print("=" * 60)
    
    # Patterns to find mission CSV files
    patterns = [
        "../output/csv_separati/mission_*.csv",  # Separate mission files (PRIORITY)
        "../output/mission_*.csv",               # Specific mission files  
        "../output/sea074*.csv",                 # Specific SeaExplorer files
        "../output/netcdf_output/*.csv",         # CSVs in output folder
        "../input/pld/logs/*.csv"               # CSVs in pld/logs folder
    ]
    
    print(f"\n🔍 SEARCHING CSV FILES...")
    all_files = []
    
    for pattern in patterns:
        files = glob.glob(pattern)
        all_files.extend(files)
        if files:
            print(f"   📂 {pattern}: {len(files)} files")
    
    if not all_files:
        print(f"❌ No CSV files found!")
        print(f"💡 Searched patterns: {patterns}")
        return
    
    print(f"📋 Total files found: {len(all_files)}")
    
    # Filter files by size and content
    print(f"\n🔧 FILTERING FILES...")
    
    valid_files = []
    skipped_files = {
        'too_small': [],
        'already_processed': [],
        'read_error': []
    }
    
    for file_path in all_files:
        # Skip already processed files
        skip_keywords = ['merged', 'backup', 'sample', 'metadata', 'units_converted', 'renamed', 'LATEST', 'latest', 'convert_all_units']
        if any(keyword in file_path.lower() for keyword in skip_keywords):
            skipped_files['already_processed'].append(file_path)
            continue
        
        # Check file size
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb < 0.001:  # < 1KB
                skipped_files['too_small'].append(file_path)
                continue
        except:
            skipped_files['read_error'].append(file_path)
            continue
        
        valid_files.append(file_path)
    
    print(f"   ✅ Valid files: {len(valid_files)}")
    print(f"   ⚠️ Skipped files: {sum(len(v) for v in skipped_files.values())}")
    for category, files in skipped_files.items():
        if files:
            print(f"      - {category.replace('_', ' ').title()}: {len(files)}")
    
    if not valid_files:
        print(f"❌ No valid CSV files found!")
        return
    
    # CORRECT NUMERICAL SORTING
    print(f"\n📋 FILE SORTING...")
    file_paths = valid_files  # Rename for consistency
    file_paths.sort(key=extract_file_number)
    
    # Show order
    file_numbers = [extract_file_number(f) for f in file_paths]
    print(f"   First file: {os.path.basename(file_paths[0])} (#{file_numbers[0]})")
    print(f"   Last file: {os.path.basename(file_paths[-1])} (#{file_numbers[-1]})")
    print(f"   Number range: {min(file_numbers)} → {max(file_numbers)}")
    
    if len(file_paths) <= 20:
        print(f"   Complete order: {file_numbers}")
    else:
        print(f"   First 10: {file_numbers[:10]}")
        print(f"   Last 10: {file_numbers[-10:]}")
    
    # Verify order
    if file_numbers != sorted(file_numbers):
        print("⚠️ WARNING: Order might not be correct")
    else:
        print("✅ Numerical order verified")
    
    # Analyze file structure
    columns_info = analyze_csv_files(file_paths)
    
    if not columns_info:
        print(f"❌ Could not analyze file structure!")
        return
    
    print(f"\n📊 FILE STRUCTURE:")
    print(f"   Reference: {os.path.basename(columns_info['reference_file'])}")
    print(f"   Columns: {columns_info['count']}")
    
    # DATA LOADING AND MERGING
    print(f"\n🔄 LOADING AND MERGING CSV FILES...")
    print("=" * 50)
    
    all_dataframes = []
    total_rows = 0
    loading_errors = []
    
    for i, file_path in enumerate(file_paths, 1):
        file_num = extract_file_number(file_path)
        
        try:
            print(f"📂 File {i:3d}/{len(file_paths)}: {os.path.basename(file_path):<25} (#{file_num:3d})", end="")
            
            # Load CSV with specific dtypes to preserve coordinate precision
            # Keep coordinates as strings to avoid float conversion issues
            coordinate_columns = {
                'NAV_LATITUDE': str,
                'NAV_LONGITUDE': str
            }
            
            df = pd.read_csv(file_path, dtype=coordinate_columns)
            
            if len(df) == 0:
                print(" → ❌ Empty")
                continue
            
            # Add file metadata
            df['source_file'] = os.path.basename(file_path)
            df['file_number'] = file_num
            
            all_dataframes.append(df)
            total_rows += len(df)
            
            print(f" → ✅ {len(df):>6,} rows")
            
        except Exception as e:
            print(f" → ❌ Error: {str(e)[:30]}...")
            loading_errors.append((file_path, str(e)))
    
    if not all_dataframes:
        print(f"\n❌ No data loaded!")
        return
    
    print(f"\n📊 LOADING SUMMARY:")
    print(f"   Files loaded: {len(all_dataframes)}/{len(file_paths)}")
    print(f"   Total rows: {total_rows:,}")
    print(f"   Loading errors: {len(loading_errors)}")
    
    # MERGE DATA
    print(f"\n🔗 MERGING DATA...")
    
    try:
        merged_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
        print(f"✅ Data merged: {len(merged_df):,} total rows")
        
        # Try temporal sorting if time column exists
        sort_column = None
        time_columns = ['PLD_REALTIMECLOCK', 'TIMESTAMP', 'TIME', 'DATE_TIME']
        for col in time_columns:
            if col in merged_df.columns:
                sort_column = col
                break
        
        if sort_column:
            print(f"   📅 Sorting by time column: {sort_column}")
            merged_df = merged_df.sort_values(sort_column).reset_index(drop=True)
        else:
            print(f"   📋 Maintaining file order (no time column found)")
        
    except Exception as e:
        print(f"❌ Merge error: {e}")
        return
    
    # SAVE MERGED DATA
    print(f"\n💾 SAVING MERGED DATASET...")
    
    try:
        # Create output filename with script name and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"../output/script2_mission_complete_merged_{timestamp}.csv"
        
        # Save to CSV
        merged_df.to_csv(output_file, index=False, encoding='utf-8')
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✅ Merged dataset saved: {output_file}")
        print(f"   Size: {file_size_mb:.1f} MB")
        print(f"   Rows: {len(merged_df):,}")
        print(f"   Columns: {len(merged_df.columns)}")
        
    except Exception as e:
        print(f"❌ Save error: {e}")
        return

    # SAVE METADATA
    print(f"\n📝 SAVING METADATA...")

    try:
        metadata_file = f"../output/script2_mission_merge_metadata_{timestamp}.txt"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write("MISSION DATA MERGE - CSV VERSION\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Merge date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Files processed: {len(file_paths)}\n")
            f.write(f"Files loaded: {len(all_dataframes)}\n")
            f.write(f"Total rows: {len(merged_df):,}\n")
            f.write(f"Total columns: {len(merged_df.columns)}\n")
            f.write(f"Output file: {output_file}\n\n")
            
            f.write("SOURCE FILES:\n")
            f.write("-" * 30 + "\n")
            for i, file_path in enumerate(file_paths, 1):
                file_num = extract_file_number(file_path)
                f.write(f"{i:3d}. {os.path.basename(file_path):<25} (#{file_num:3d})\n")
            
            if loading_errors:
                f.write(f"\nLOADING ERRORS:\n")
                f.write("-" * 20 + "\n")
                for file_path, error in loading_errors:
                    f.write(f"❌ {os.path.basename(file_path)}: {error}\n")
            
            f.write(f"\nCOLUMNS ({len(merged_df.columns)}):\n")
            f.write("-" * 20 + "\n")
            for i, col in enumerate(merged_df.columns, 1):
                f.write(f"{i:2d}. {col}\n")
        
        print(f"✅ Metadata saved: {metadata_file}")
        
    except Exception as e:
        print(f"⚠️ Warning metadata: {e}")
    
    # FINAL SUMMARY
    print(f"\n🎯 MERGE COMPLETED!")
    print("=" * 60)
    print(f"📊 Data merged: {len(merged_df):,} rows × {len(merged_df.columns)} columns")
    print(f"📁 Files processed: {len(all_dataframes)}/{len(file_paths)}")
    print(f"📄 Output files:")
    print(f"  • Main dataset: {output_file}")
    print(f"  • Metadata: {metadata_file}")
    print(f"\n💡 NEXT STEPS:")
    print(f"1. 📊 Check the merged dataset: {output_file}")
    print(f"2. � Run script 3 for unit conversions")
    print(f"3. 🏷️ Run script 4 for variable renaming")

if __name__ == "__main__":
    merge_csv_files()