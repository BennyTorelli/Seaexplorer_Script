#!/usr/bin/env python3
"""
SEAEXPLORER PIPELINE STATUS ANALYZER
====================================

This script analyzes the current status of the data processing pipeline
and provides a summary of which steps have been completed and what remains to be done.

The pipeline follows this order:
1. convert_raw_to_separate_csv.py - Converts raw files to separate CSV files
2. merge_mission_data_csv.py - Merges CSV files into a complete mission file  
3. convert_all_units_csv.py - Converts measurement units
4. rename_variables_csv.py - Renames variables according to conventions

Author: Support script for SeaExplorer pipeline
Date: September 2024
"""

import os
import glob
from datetime import datetime

def find_recent_files(pattern, folder="."):
    """Find the most recent files matching the pattern"""
    full_path = os.path.join(folder, pattern)
    files = glob.glob(full_path)
    if not files:
        return []
    
    # Sort by modification date (most recent first)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files

def analyze_pipeline_status():
    """Analyze the current pipeline status"""
    print("🔍 SEAEXPLORER PIPELINE STATUS ANALYSIS")
    print("=" * 50)
    
    # Check raw files
    raw_files = find_recent_files("*.gli")
    print(f"\n📁 RAW FILES (.gli): {len(raw_files)} found")
    if raw_files:
        print(f"   Most recent: {os.path.basename(raw_files[0])}")
    
    # Check separate CSV files
    separate_csv = find_recent_files("csv_separati/*.csv")
    print(f"\n📊 SEPARATE CSV: {len(separate_csv)} found")
    if separate_csv:
        print(f"   Folder: csv_separati/ ({len(separate_csv)} files)")
    
    # Check merged files
    merged_files = find_recent_files("mission_complete_merged_*.csv")
    print(f"\n🔗 MERGED FILES: {len(merged_files)} found")
    for file in merged_files[:3]:  # Show first 3
        print(f"   - {os.path.basename(file)}")
    
    # Check files with converted units
    units_files = find_recent_files("mission_complete_merged_*_units_converted.csv")
    print(f"\n⚡ UNITS CONVERTED: {len(units_files)} found")
    for file in units_files[:3]:
        print(f"   - {os.path.basename(file)}")
    
    # Check files with renamed variables
    renamed_files = find_recent_files("mission_complete_merged_*_units_converted_renamed.csv")
    print(f"\n🏷️  VARIABLES RENAMED: {len(renamed_files)} found")
    for file in renamed_files[:3]:
        print(f"   - {os.path.basename(file)}")
    
    print("\n" + "=" * 50)
    print("📋 PIPELINE STATUS:")
    
    # Determine status of each step
    step_status = {
        "Step 1 (Separate CSV)": "✅ COMPLETED" if separate_csv else "❌ NOT COMPLETED",
        "Step 2 (Merged Files)": "✅ COMPLETED" if merged_files else "❌ NOT COMPLETED", 
        "Step 3 (Units Converted)": "✅ COMPLETED" if units_files else "❌ NOT COMPLETED",
        "Step 4 (Variables Renamed)": "✅ COMPLETED" if renamed_files else "❌ NOT COMPLETED"
    }
    
    for step, status in step_status.items():
        print(f"   {step}: {status}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if not separate_csv:
        print("   → Run convert_raw_to_separate_csv.py to start")
    elif not merged_files:
        print("   → Run merge_mission_data_csv.py to merge CSV files")
    elif not units_files:
        print("   → Run convert_all_units_csv.py to convert units")
    elif not renamed_files:
        print("   → Run rename_variables_csv.py to complete the pipeline")
    else:
        print("   → Pipeline complete! All steps have been executed.")
        if renamed_files:
            print(f"   → Final file: {os.path.basename(renamed_files[0])}")

def main():
    """Main function"""
    try:
        analyze_pipeline_status()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())