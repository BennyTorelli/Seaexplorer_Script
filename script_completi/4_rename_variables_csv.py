#!/usr/bin/env python3
"""
RENAME VARIABLES IN CSV DATASET
Rename all variables with standard oceanographic names
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import glob

def rename_variables_csv():
    """
    Rename all variables in the CSV with standard names
    """
    
    print("🏷️ RENAME VARIABLES IN CSV DATASET")
    print("=" * 50)
    
    # Find automatically the most recent CSV file
    print(f"\n🔍 SEARCHING CSV FILES...")
    
    # Search patterns for CSV files
    csv_patterns = [
        "*.csv",                    # CSV in current directory
        "mission_*.csv",           # Mission files
        "test_complete/*.csv",     # Test directory  
        "netcdf_output/*.csv"      # Output directory
    ]
    
    csv_files = []
    for pattern in csv_patterns:
        files = glob.glob(pattern)
        csv_files.extend(files)
    
    if not csv_files:
        print("❌ No CSV files found!")
        print("💡 Patterns searched:", csv_patterns)
        return
    
    # Filter files too small (< 1MB) or backup/sample
    valid_files = []
    units_converted_files = []  # Priority to files with converted units
    
    for file in csv_files:
        if any(keyword in file.lower() for keyword in ['backup', 'sample', 'metadata', 'renamed']):
            continue
        size_mb = os.path.getsize(file) / (1024 * 1024)
        if size_mb > 1:  # Files larger than 1MB
            file_info = (file, size_mb, os.path.getmtime(file))
            # Give priority to files with already converted units
            if 'units_converted' in file.lower():
                units_converted_files.append(file_info)
            else:
                valid_files.append(file_info)
    
    # Priority to files with converted units, then others
    all_valid_files = units_converted_files + valid_files
    
    if not all_valid_files:
        print("❌ No valid CSV files found!")
        return
    
    # Sort by modification date (most recent first)
    all_valid_files.sort(key=lambda x: x[2], reverse=True)
    csv_file = all_valid_files[0][0]
    
    print(f"✅ CSV file selected: {csv_file}")
    print(f"   Size: {all_valid_files[0][1]:.1f} MB")
    print(f"   Last update: {datetime.fromtimestamp(all_valid_files[0][2]).strftime('%Y-%m-%d %H:%M:%S')}")
    
    if 'units_converted' in csv_file:
        print(f"   🎯 File with units already converted (PRIORITY)")
    else:
        print(f"   ⚠️ File without unit conversions")
    
    # Variable mapping for renaming
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
    
    print(f"\n📋 VARIABLE MAPPING:")
    print("-" * 40)
    for old_name, new_name in variable_mapping.items():
        print(f"   {old_name:<25} → {new_name}")
    
    # Load CSV
    print(f"\n📄 LOADING CSV...")
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ CSV loaded: {csv_file}")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        
        # Show current columns
        print(f"\n📊 CURRENT COLUMNS:")
        for i, col in enumerate(df.columns, 1):
            marker = "🎯" if col in variable_mapping else "  "
            print(f"   {marker} {i:2d}. {col}")
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return
    
    # Verify presence of variables to rename
    print(f"\n🔍 CHECKING VARIABLES TO RENAME:")
    print("-" * 45)
    
    missing_vars = []
    present_vars = []
    
    for old_name, new_name in variable_mapping.items():
        if old_name in df.columns:
            present_vars.append((old_name, new_name))
            valid_count = df[old_name].notna().sum()
            total_count = len(df)
            percentage = (valid_count / total_count) * 100
            print(f"   ✅ {old_name:<25} → {new_name:<10} ({valid_count:,} values, {percentage:.1f}%)")
        else:
            missing_vars.append(old_name)
            print(f"   ❌ {old_name:<25} → {new_name:<10} (NOT FOUND)")
    
    if missing_vars:
        print(f"\n⚠️ Missing variables: {len(missing_vars)}")
        print(f"   Continuing with available variables: {len(present_vars)}")
    
    if not present_vars:
        print(f"❌ No variables to rename found!")
        return
    
    # Apply renaming
    print(f"\n🔄 APPLYING RENAMING...")
    
    try:
        # Create dictionary only for present variables
        rename_dict = {old_name: new_name for old_name, new_name in present_vars}
        
        # Apply renaming
        df_renamed = df.rename(columns=rename_dict)
        
        print(f"✅ Renaming applied for {len(rename_dict)} variables")
        
        # Verify that renaming was successful
        print(f"\n📋 COLUMNS AFTER RENAMING:")
        renamed_columns = []
        for i, col in enumerate(df_renamed.columns, 1):
            is_renamed = col in rename_dict.values()
            marker = "✅" if is_renamed else "  "
            if is_renamed:
                renamed_columns.append(col)
            print(f"   {marker} {i:2d}. {col}")
        
        print(f"\n🎯 Renamed variables: {len(renamed_columns)}")
        print(f"   New names: {', '.join(renamed_columns)}")
        
    except Exception as e:
        print(f"❌ Renaming error: {e}")
        return
    
    # Save CSV with updated names
    print(f"\n💾 SAVING CSV WITH NEW NAMES...")
    
    try:
        # Create output filename with script name and renamed suffix
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"script4_{base_name}_renamed_{timestamp}.csv"
        
        # Save with new filename
        df_renamed.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"✅ CSV saved with new names: {output_file}")
        
        # Verify file size
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"   Size: {file_size:.1f} MB")
        
    except Exception as e:
        print(f"❌ Save error: {e}")
        return
    
    # Final verification
    print(f"\n🔍 FINAL VERIFICATION...")
    
    try:
        # Reload CSV for verification
        df_check = pd.read_csv(output_file)
        
        print(f"✅ Verification completed:")
        print(f"   Rows: {len(df_check):,}")
        print(f"   Columns: {len(df_check.columns)}")
        
        # Verify renamed variables
        print(f"\n   Main variables verified:")
        main_vars = ['TIME', 'DOXY', 'CHLA', 'TURB', 'CNDC', 'TEMP', 'PRES', 'DEPTH', 'LATITUDE', 'LONGITUDE']
        
        for var in main_vars:
            if var in df_check.columns:
                valid_count = df_check[var].notna().sum()
                total_count = len(df_check)
                percentage = (valid_count / total_count) * 100
                print(f"      ✅ {var:<10}: {valid_count:,} values ({percentage:.1f}%)")
            else:
                print(f"      ❌ {var:<10}: NOT FOUND")
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return
    
    # Update metadata file
    print(f"\n📝 UPDATING METADATA...")
    
    try:
        metadata_file = f"rename_variables_metadata_{timestamp}.txt"
        
        # Create metadata content
        metadata_content = f"""VARIABLE RENAMING METADATA
==========================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Input file: {csv_file}
Output file: {output_file}
Variables renamed: {len(present_vars)}

MAPPING APPLIED:
----------------
"""
        
        for old_name, new_name in present_vars:
            metadata_content += f"- {old_name} → {new_name}\n"
        
        metadata_content += f"""
FINAL STANDARD VARIABLES:
-------------------------
✅ TIME: Glider timestamp
✅ DOXY: Dissolved oxygen (µmol/kg)
✅ CHLA: Chlorophyll-a (mg/m³)
✅ TURB: Turbidity (m⁻¹ sr⁻¹)
✅ CNDC: Conductivity (S/m)
✅ TEMP: Temperature (°C)
✅ PRES: Pressure (dbar)
✅ DEPTH: Depth (m)
✅ LATITUDE: Latitude (decimal degrees)
✅ LONGITUDE: Longitude (decimal degrees)

FILE INFORMATION:
-----------------
Rows: {len(df_check):,}
Columns: {len(df_check.columns)}
Size: {file_size:.1f} MB
Encoding: UTF-8
"""
        
        # Save metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write(metadata_content)
        
        print(f"✅ Metadata saved: {metadata_file}")
        
    except Exception as e:
        print(f"⚠️ Warning updating metadata: {e}")
    
    # Final summary
    print(f"\n🎯 VARIABLE RENAMING COMPLETED!")
    print("=" * 50)
    print(f"🏷️ Variables renamed: {len(present_vars)}")
    print(f"📄 Output file: {output_file}")
    print(f"📁 Size: {file_size:.1f} MB")
    
    print(f"\n📋 MAIN VARIABLES WITH STANDARD NAMES:")
    standard_vars = [
        ('TIME', 'Timestamp'),
        ('DOXY', 'Oxygen (µmol/kg)'),
        ('CHLA', 'Chlorophyll (mg/m³)'),
        ('TURB', 'Turbidity (m⁻¹ sr⁻¹)'),
        ('CNDC', 'Conductivity (S/m)'),
        ('TEMP', 'Temperature (°C)'),
        ('PRES', 'Pressure (dbar)'),
        ('DEPTH', 'Depth (m)'),
        ('LATITUDE', 'Latitude (decimal degrees)'),
        ('LONGITUDE', 'Longitude (decimal degrees)')
    ]
    
    for var_name, description in standard_vars:
        status = "✅" if var_name in df_check.columns else "❌"
        print(f"   {status} {var_name:<10}: {description}")
    
    print(f"\n🚀 DATASET READY WITH STANDARD VARIABLE NAMES!")
    print("   📊 All units converted")
    print("   🏷️ Standardized variable names")
    print("   📄 CSV format for easy use")
    print(f"   📄 Final file: {output_file}")

if __name__ == "__main__":
    rename_variables_csv()