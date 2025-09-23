#!/usr/bin/env python3
"""
CONVERT ALL UNITS - CSV VERSION
Converts all physical units to standard oceanographic units with proper scientific conversions.
Optimized order: coordinates first, then oxygen with TEOS-10, then other parameters.
"""

import pandas as pd
import numpy as np
import gsw
from datetime import datetime
import os
import argparse

def ddmm_to_decimal(coord_str):
    """
    Convert coordinates from DDMM.MMM format to DD.DDDD format
    Example: 2838.767 -> 28.646117 (28 + 38.767/60)
    """
    if pd.isna(coord_str) or coord_str == 0:
        return coord_str
    
    try:
        coord_float = float(coord_str)
        if coord_float == 0:
            return 0
            
        # Extract degrees and decimal minutes
        degrees = int(coord_float / 100)
        decimal_minutes = coord_float - (degrees * 100)
        
        # Convert to decimal degrees
        decimal_degrees = degrees + decimal_minutes / 60
        
        return decimal_degrees
    except:
        return coord_str

def convert_coordinates(df):
    """
    Convert NAV_LATITUDE and NAV_LONGITUDE from DDMM.MMM to DD.DDDD format
    """
    print("Converting coordinates from DDMM.MMM to DD.DDDD format...")
    
    if 'NAV_LATITUDE' in df.columns:
        df['NAV_LATITUDE'] = df['NAV_LATITUDE'].apply(ddmm_to_decimal)
        print(f"✓ NAV_LATITUDE converted")
    
    if 'NAV_LONGITUDE' in df.columns:
        # For longitude, make negative (Western coordinates)
        df['NAV_LONGITUDE'] = df['NAV_LONGITUDE'].apply(ddmm_to_decimal)
        df['NAV_LONGITUDE'] = -df['NAV_LONGITUDE'].abs()  # Ensure negative for Western hemisphere
        print(f"✓ NAV_LONGITUDE converted (made negative for Western hemisphere)")
    
    return df

def convert_turbidity(df):
    """
    Convert turbidity to NTU (Nephelometric Turbidity Units)
    Assuming input is already in compatible units (1:1 conversion)
    """
    turbidity_cols = [col for col in df.columns if 'TURBIDITY' in col.upper()]
    
    for col in turbidity_cols:
        print(f"✓ {col}: Converting to NTU (1:1 ratio)")
        # Assuming already in compatible units, just ensure proper naming
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def convert_chlorophyll(df):
    """
    Convert chlorophyll to µg/L
    Assuming input is already in µg/L (1:1 conversion)
    """
    chlorophyll_cols = [col for col in df.columns if 'CHLA' in col.upper() or 'CHLOROPHYLL' in col.upper()]
    
    for col in chlorophyll_cols:
        print(f"✓ {col}: Already in µg/L (1:1 ratio)")
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def convert_oxygen_teos10(df):
    """
    Convert oxygen from µmol/L to µmol/kg using TEOS-10 equation of state
    Requires conductivity, temperature, pressure, and coordinates
    """
    print("Converting oxygen µmol/L → µmol/kg using TEOS-10...")
    
    oxygen_cols = [col for col in df.columns if 'DOXY' in col.upper() or 'OXYGEN' in col.upper()]
    
    if not oxygen_cols:
        print("No oxygen columns found")
        return df
    
    # Required variables for TEOS-10
    required_vars = ['CNDC_SENSOR', 'TEMP_SENSOR', 'PRES_SENSOR', 'NAV_LATITUDE', 'NAV_LONGITUDE']
    missing_vars = [var for var in required_vars if var not in df.columns]
    
    if missing_vars:
        print(f"⚠️  Missing variables for TEOS-10: {missing_vars}")
        print("Cannot perform oxygen conversion without these variables")
        return df
    
    # Create masks for valid data
    valid_mask = (
        pd.notna(df['CNDC_SENSOR']) & (df['CNDC_SENSOR'] > 0) &
        pd.notna(df['TEMP_SENSOR']) &
        pd.notna(df['PRES_SENSOR']) &
        pd.notna(df['NAV_LATITUDE']) & (df['NAV_LATITUDE'] != 0) &
        pd.notna(df['NAV_LONGITUDE']) & (df['NAV_LONGITUDE'] != 0)
    )
    
    valid_count = valid_mask.sum()
    total_count = len(df)
    
    print(f"Valid data points for TEOS-10: {valid_count}/{total_count} ({100*valid_count/total_count:.1f}%)")
    
    if valid_count == 0:
        print("⚠️  No valid data points for TEOS-10 conversion")
        return df
    
    # Apply TEOS-10 conversion only to valid data
    for col in oxygen_cols:
        if col in df.columns:
            print(f"Processing {col}...")
            
            # Initialize output column
            df[f'{col}_CONVERTED'] = np.nan
            
            # Get valid data subset
            valid_data = df[valid_mask].copy()
            
            if len(valid_data) > 0:
                try:
                    # TEOS-10 conversion sequence
                    # 1. Calculate Practical Salinity
                    SP = gsw.SP_from_C(
                        valid_data['CNDC_SENSOR'],
                        valid_data['TEMP_SENSOR'], 
                        valid_data['PRES_SENSOR']
                    )
                    
                    # 2. Calculate Absolute Salinity
                    SA = gsw.SA_from_SP(
                        SP,
                        valid_data['PRES_SENSOR'],
                        valid_data['NAV_LONGITUDE'],
                        valid_data['NAV_LATITUDE']
                    )
                    
                    # 3. Calculate Conservative Temperature
                    CT = gsw.CT_from_t(
                        SA,
                        valid_data['TEMP_SENSOR'],
                        valid_data['PRES_SENSOR']
                    )
                    
                    # 4. Calculate density
                    rho = gsw.rho(SA, CT, valid_data['PRES_SENSOR'])
                    
                    # 5. Convert µmol/L to µmol/kg
                    oxygen_umol_L = pd.to_numeric(valid_data[col], errors='coerce')
                    oxygen_umol_kg = oxygen_umol_L / (rho / 1000)  # rho in kg/m³, convert to kg/L
                    
                    # Store results back in main dataframe
                    df.loc[valid_mask, f'{col}_CONVERTED'] = oxygen_umol_kg
                    
                    # Replace original column
                    df[col] = df[f'{col}_CONVERTED']
                    df.drop(f'{col}_CONVERTED', axis=1, inplace=True)
                    
                    valid_converted = pd.notna(oxygen_umol_kg).sum()
                    print(f"✓ {col}: {valid_converted} values converted from µmol/L to µmol/kg")
                    
                except Exception as e:
                    print(f"❌ Error converting {col}: {str(e)}")
            else:
                print(f"⚠️  No valid data for {col}")
    
    return df

def convert_conductivity(df):
    """
    Convert conductivity to S/m (Siemens per meter)
    Assuming input is in mS/cm, convert to S/m
    """
    conductivity_cols = [col for col in df.columns if 'CNDC' in col.upper() or 'CONDUCTIVITY' in col.upper()]
    
    for col in conductivity_cols:
        print(f"✓ {col}: Converting mS/cm → S/m (factor: 0.1)")
        df[col] = pd.to_numeric(df[col], errors='coerce') * 0.1  # mS/cm to S/m
    
    return df

def main():
    parser = argparse.ArgumentParser(description='Convert units in merged mission CSV file')
    parser.add_argument('input_file', nargs='?', help='Input CSV file path')
    parser.add_argument('--no-sample', action='store_true', help='Do not create sample file')
    
    args = parser.parse_args()
    
    # Find input file
    if args.input_file:
        input_file = args.input_file
    else:
        # Look for latest merged file
        csv_files = [f for f in os.listdir('.') if f.startswith('script2_mission_complete_merged_') and f.endswith('.csv')]
        if not csv_files:
            print("❌ No merged CSV file found. Run script 2 first.")
            return
        
        input_file = sorted(csv_files)[-1]  # Get most recent
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    print(f"📖 Reading file: {input_file}")
    
    # Read CSV with proper data types
    try:
        coordinate_columns = ['NAV_LATITUDE', 'NAV_LONGITUDE']
        dtype_dict = {col: str for col in coordinate_columns}
        
        df = pd.read_csv(input_file, dtype=dtype_dict)
        print(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    print("\n🔄 Starting unit conversions...")
    print("Order: 1) Coordinates, 2) Turbidity, 3) Chlorophyll, 4) Oxygen (TEOS-10), 5) Conductivity")
    
    # Apply conversions in optimized order
    try:
        # 1. Convert coordinates first (needed for TEOS-10)
        df = convert_coordinates(df)
        
        # 2. Convert turbidity
        df = convert_turbidity(df)
        
        # 3. Convert chlorophyll
        df = convert_chlorophyll(df)
        
        # 4. Convert oxygen using TEOS-10 (requires coordinates)
        df = convert_oxygen_teos10(df)
        
        # 5. Convert conductivity
        df = convert_conductivity(df)
        
        print("\n✅ All unit conversions completed!")
        
    except Exception as e:
        print(f"❌ Error during conversions: {e}")
        return
    
    # Generate output filename with script identification
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"script3_{base_name}_units_converted_{timestamp}.csv"
    
    # Save results
    try:
        df.to_csv(output_file, index=False)
        print(f"\n💾 Saved: {output_file}")
        print(f"📊 Final dataset: {len(df)} rows, {len(df.columns)} columns")
        
        # Print summary of conversions
        print("\n📋 CONVERSION SUMMARY:")
        print("• Coordinates: DDMM.MMM → DD.DDDD")
        print("• Turbidity: → NTU")
        print("• Chlorophyll: → µg/L")
        print("• Oxygen: µmol/L → µmol/kg (TEOS-10)")
        print("• Conductivity: mS/cm → S/m")
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == "__main__":
    main()