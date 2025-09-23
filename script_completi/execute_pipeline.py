#!/usr/bin/env python3
"""
SEAEXPLORER SEQUENTIAL PIPELINE EXECUTOR
=========================================

This script executes the complete SeaExplorer data processing pipeline 
in the correct sequential order with appropriate file priority.

PIPELINE OVERVIEW:
- Raw Files → Separate CSV → Merged CSV → Unit Converted CSV → Renamed Variables CSV
- Each script automatically selects the output from the previous step
- File priority ensures appropriate sequential processing

CURRENT STATUS (from pipeline analysis):
✅ Step 1: convert_raw_to_separate_csv.py - COMPLETED (183 files in csv_separati/)
✅ Step 2: merge_mission_data_csv.py - COMPLETED (mission_complete_merged_*.csv exists)
✅ Step 3: convert_all_units_csv.py - COMPLETED (units_converted files exist)
✅ Step 4: rename_variables_csv.py - COMPLETED (renamed files exist)

The pipeline is currently complete! Each script has appropriate file priority:

1. convert_all_units_csv.py prioritizes "merged" and "complete" files
2. rename_variables_csv.py prioritizes "units_converted" files
3. Both scripts exclude already processed files to prevent duplication

CHANGES MADE:
- Fixed extract_number() functions for appropriate file ordering
- Removed decimal_to_dms() conversion (keeping decimal coordinates)
- Added file priority logic in all scripts
- Added exclusion patterns for processed files
"""

import subprocess
import sys
import os
from datetime import datetime

def run_script(script_name, description):
    """Execute a script with error handling"""
    print(f"\n{'='*60}")
    print(f"🔄 EXECUTING: {script_name}")
    print(f"📝 {description}")
    print(f"{'='*60}")
    
    try:
        # Use the configured Python environment
        python_cmd = "/Users/benedettatorelli/Desktop/Datos_brutos_1/.venv/bin/python"
        result = subprocess.run([python_cmd, script_name], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {script_name} completed")
            if result.stdout:
                print("📊 Output:")
                print(result.stdout)
        else:
            print(f"❌ ERROR: {script_name} failed")
            if result.stderr:
                print("🚨 Error details:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {script_name} took more than 5 minutes")
        return False
    except Exception as e:
        print(f"💥 EXCEPTION: {str(e)}")
        return False
    
    return True

def main():
    """Execute the complete pipeline"""
    
    print("🌊 SEAEXPLORER DATA PROCESSING PIPELINE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Change to the logs directory where the scripts are located
    script_dir = "pld/logs"
    if os.path.exists(script_dir):
        os.chdir(script_dir)
        print(f"📁 Working directory: {os.getcwd()}")
    else:
        print(f"❌ Script directory {script_dir} not found!")
        return False
    
    # Pipeline steps with descriptions
    pipeline_steps = [
        ("convert_raw_to_separate_csv.py", 
         "Converts raw .pld1.raw files to individual mission_XXX.csv files"),
        
        ("merge_mission_data_csv.py", 
         "Merges all separate CSV files into a single ordered dataset"),
        
        ("convert_all_units_csv.py", 
         "Converts measurement units (turbidity, chlorophyll, conductivity, oxygen)"),
        
        ("rename_variables_csv.py", 
         "Renames variables with standard oceanographic nomenclature")
    ]
    
    print(f"\n🎯 PIPELINE EXECUTION PLAN:")
    for i, (script, desc) in enumerate(pipeline_steps, 1):
        print(f"   {i}. {script}")
        print(f"      → {desc}")
    
    # Ask for confirmation
    print(f"\n⚠️  This will execute the complete pipeline sequentially.")
    print(f"💡 Each script will automatically select the appropriate input file.")
    response = input(f"\n🤔 Do you want to proceed? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Pipeline execution cancelled.")
        return False
    
    # Execute pipeline
    success_count = 0
    for i, (script, description) in enumerate(pipeline_steps, 1):
        print(f"\n\n🎯 STEP {i}/{len(pipeline_steps)}")
        
        if not os.path.exists(script):
            print(f"❌ Script {script} not found!")
            continue
            
        if run_script(script, description):
            success_count += 1
            print(f"✅ Step {i} completed successfully")
        else:
            print(f"❌ Step {i} failed")
            print(f"🛑 Stopping pipeline execution")
            break
    
    # Summary
    print(f"\n" + "="*80)
    print(f"📊 PIPELINE EXECUTION SUMMARY")
    print(f"="*80)
    print(f"✅ Successful steps: {success_count}/{len(pipeline_steps)}")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_count == len(pipeline_steps):
        print(f"🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"💡 Your SeaExplorer data has been fully processed.")
    else:
        print(f"⚠️  Incomplete pipeline. Check error messages above.")
    
    return success_count == len(pipeline_steps)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)