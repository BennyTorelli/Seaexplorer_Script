#!/usr/bin/env python3
"""
CONVERSIONE COMPLETA UNITÀ - CSV
Script collettivo per tutte le conversioni di unità del dataset SeaExplorer
Applica tutte le conversioni in sequenza: torbidità, clorofilla, conduttività, coordinate, ossigeno
"""

import pandas as pd
import numpy as np
import gsw
from datetime import datetime
import os
import glob

def convert_turbidity(df, turbidity_var):
    """
    Converte torbidità da m⁻¹ sr⁻¹ a NTU
    """
    print(f"\n🌊 CONVERSIONE TORBIDITÀ: m⁻¹ sr⁻¹ → NTU")
    print("-" * 50)
    
    turbidity_data = df[turbidity_var]
    valid_count = turbidity_data.notna().sum()
    
    print(f"   Variabile: {turbidity_var}")
    print(f"   Valori validi: {valid_count:,}")
    
    if valid_count > 0:
        print(f"   Range originale: {turbidity_data.min():.6f} - {turbidity_data.max():.6f} m⁻¹ sr⁻¹")
        
        # Formula: NTU = β / 0.002727 (equivale a β × 366.70)
        df[turbidity_var] = df[turbidity_var] * 366.70
        
        print(f"   Formula: NTU = β / 0.002727 (fattore ×366.70)")
        print(f"   Range convertito: {df[turbidity_var].min():.2f} - {df[turbidity_var].max():.2f} NTU")
        print(f"   ✅ Torbidità convertita in NTU")
    else:
        print(f"   ⚠️ Nessun dato valido da convertire")

def convert_chlorophyll(df, chlorophyll_var):
    """
    Converte clorofilla da µg/L a mg/m³ (equivalenza 1:1)
    """
    print(f"\n🌱 CONVERSIONE CLOROFILLA: µg/L → mg/m³")
    print("-" * 50)
    
    chlorophyll_data = df[chlorophyll_var]
    valid_count = chlorophyll_data.notna().sum()
    
    print(f"   Variabile: {chlorophyll_var}")
    print(f"   Valori validi: {valid_count:,}")
    
    if valid_count > 0:
        print(f"   Range: {chlorophyll_data.min():.3f} - {chlorophyll_data.max():.3f}")
        print(f"   Equivalenza: 1 µg/L = 1 mg/m³ (stesso valore numerico)")
        print(f"   ✅ Unità aggiornata: µg/L → mg/m³")
    else:
        print(f"   ⚠️ Nessun dato valido")

def convert_conductivity(df, conductivity_var):
    """
    Converte conduttività da mS/cm a S/m
    """
    print(f"\n⚡ CONVERSIONE CONDUTTIVITÀ: mS/cm → S/m")
    print("-" * 50)
    
    conductivity_data = df[conductivity_var]
    valid_count = conductivity_data.notna().sum()
    
    print(f"   Variabile: {conductivity_var}")
    print(f"   Valori validi: {valid_count:,}")
    
    if valid_count > 0:
        print(f"   Range originale: {conductivity_data.min():.3f} - {conductivity_data.max():.3f} mS/cm")
        
        # Conversione: mS/cm → S/m (fattore 0.1)
        df[conductivity_var] = df[conductivity_var] * 0.1
        
        print(f"   Fattore conversione: ×0.1")
        print(f"   Range convertito: {df[conductivity_var].min():.4f} - {df[conductivity_var].max():.4f} S/m")
        print(f"   ✅ Conduttività convertita in S/m")
    else:
        print(f"   ⚠️ Nessun dato valido da convertire")

def convert_coordinates(df, latitude_var, longitude_var):
    """
    Verifica e mantiene coordinate in formato gradi decimali (dd.ddddd)
    """
    print(f"\n🌍 COORDINATE: Mantengo gradi decimali")
    print("-" * 50)
    
    lat_data = df[latitude_var] if latitude_var else None
    lon_data = df[longitude_var] if longitude_var else None
    
    if lat_data is not None:
        valid_lat = lat_data.notna().sum()
        print(f"   Latitudine ({latitude_var}): {valid_lat:,} valori")
        
        if valid_lat > 0:
            print(f"     Range: {lat_data.min():.6f}° - {lat_data.max():.6f}°")
            print(f"     ✅ Mantenuto formato decimale")
        else:
            print(f"     ℹ️ Nessun dato valido")
    
    if lon_data is not None:
        valid_lon = lon_data.notna().sum()
        print(f"   Longitudine ({longitude_var}): {valid_lon:,} valori")
        
        if valid_lon > 0:
            print(f"     Range: {lon_data.min():.6f}° - {lon_data.max():.6f}°")
            print(f"     ✅ Mantenuto formato decimale")
        else:
            print(f"     ℹ️ Nessun dato valido")

def convert_oxygen(df, oxygen_var, temp_var, cond_var, pres_var, lat_var=None, lon_var=None):
    """
    Converte ossigeno da µmol/L a µmol/kg usando TEOS-10
    """
    print(f"\n🫧 CONVERSIONE OSSIGENO: µmol/L → µmol/kg (TEOS-10)")
    print("-" * 50)
    
    oxygen_data = df[oxygen_var]
    temp_data = df[temp_var]
    cond_data = df[cond_var]
    pres_data = df[pres_var]
    
    # Identifica righe con dati completi
    mask_complete = (
        oxygen_data.notna() & 
        temp_data.notna() & 
        cond_data.notna() & 
        pres_data.notna()
    )
    
    complete_count = mask_complete.sum()
    print(f"   Righe con dati completi: {complete_count:,}")
    
    if complete_count == 0:
        print(f"   ❌ Nessuna riga con tutti i dati necessari!")
        return
    
    # Coordinate per calcoli TEOS-10
    if lat_var and lon_var and lat_var in df.columns and lon_var in df.columns:
        lat_data = df[lat_var]
        lon_data = df[lon_var]
        valid_coords = (lat_data.notna() & lon_data.notna()).sum()
        
        if valid_coords > 0:
            mean_lat = lat_data.mean()
            mean_lon = lon_data.mean()
            print(f"   Coordinate medie: {mean_lat:.2f}°, {mean_lon:.2f}°")
        else:
            mean_lat, mean_lon = 27.8, -15.5  # Canarie
            print(f"   Coordinate predefinite: 27.8°N, 15.5°W (Canarie)")
    else:
        mean_lat, mean_lon = 27.8, -15.5  # Canarie
        print(f"   Coordinate predefinite: 27.8°N, 15.5°W (Canarie)")
    
    try:
        # Estrae dati completi
        temp_complete = temp_data[mask_complete].values
        cond_complete = cond_data[mask_complete].values
        pres_complete = pres_data[mask_complete].values
        oxygen_complete = oxygen_data[mask_complete].values
        
        # Calcoli TEOS-10
        SP = gsw.SP_from_C(cond_complete, temp_complete, pres_complete)
        SA = gsw.SA_from_SP(SP, pres_complete, mean_lon, mean_lat)
        CT = gsw.CT_from_t(SA, temp_complete, pres_complete)
        rho = gsw.rho(SA, CT, pres_complete)
        
        # Conversione µmol/L → µmol/kg
        oxygen_umol_kg = oxygen_complete * 1000.0 / rho
        
        # Aggiorna dataframe
        oxygen_converted = oxygen_data.copy()
        oxygen_converted.loc[mask_complete] = oxygen_umol_kg
        df[oxygen_var] = oxygen_converted
        
        print(f"   Range originale: {oxygen_complete.min():.2f} - {oxygen_complete.max():.2f} µmol/L")
        print(f"   Range convertito: {oxygen_umol_kg.min():.2f} - {oxygen_umol_kg.max():.2f} µmol/kg")
        print(f"   ✅ Ossigeno convertito con TEOS-10")
        
    except Exception as e:
        print(f"   ❌ Errore conversione TEOS-10: {e}")
        print(f"   ℹ️ Mantengo valori originali di ossigeno")
        # Non modifico df[oxygen_var] in caso di errore

def convert_all_units_csv():
    """
    Converte tutte le unità di misura nel file CSV
    """
    
    print("🚀 CONVERSIONE COMPLETA UNITÀ - DATASET SEAEXPLORER")
    print("=" * 80)
    print("Conversioni applicate:")
    print("  1. Torbidità: m⁻¹ sr⁻¹ → NTU")
    print("  2. Clorofilla: µg/L → mg/m³")
    print("  3. Conduttività: mS/cm → S/m")
    print("  4. Ossigeno: µmol/L → µmol/kg (TEOS-10)")
    print("  📍 Coordinate: Mantenute in gradi decimali (dd.ddddd)")
    print("=" * 80)
    
    # Trova automaticamente il file CSV più recente
    print(f"\n🔍 RICERCA FILE CSV...")
    
    # Patterns di ricerca per file CSV
    csv_patterns = [
        "*.csv",                    # CSV nella directory corrente
        "mission_*.csv",           # Mission files
        "test_complete/*.csv",     # Test directory  
        "netcdf_output/*.csv"      # Output directory
    ]
    
    csv_files = []
    for pattern in csv_patterns:
        files = glob.glob(pattern)
        csv_files.extend(files)
    
    if not csv_files:
        print("❌ Nessun file CSV trovato!")
        print("💡 Patterns cercati:", csv_patterns)
        return
    
    # Filtra file troppo piccoli (< 1MB) o backup
    valid_files = []
    merged_files = []  # Priorità ai file merged (output del merge)
    
    for file in csv_files:
        # Escludi file già processati e sample
        if any(keyword in file.lower() for keyword in ['backup', 'sample', 'metadata', 'units_converted', 'renamed']):
            continue
        size_mb = os.path.getsize(file) / (1024 * 1024)
        if size_mb > 1:  # File maggiori di 1MB
            file_info = (file, size_mb, os.path.getmtime(file))
            # Dai priorità ai file merged (output del merge)
            if 'merged' in file.lower() and 'complete' in file.lower():
                merged_files.append(file_info)
            else:
                valid_files.append(file_info)
    
    # Priorità ai file merged, poi agli altri
    all_valid_files = merged_files + valid_files
    
    if not all_valid_files:
        print("❌ Nessun file CSV valido trovato!")
        return
    
    # Ordina per data di modifica (più recente primo)
    all_valid_files.sort(key=lambda x: x[2], reverse=True)
    csv_file = all_valid_files[0][0]
    
    print(f"✅ File CSV selezionato: {csv_file}")
    print(f"   Dimensione: {all_valid_files[0][1]:.1f} MB")
    print(f"   Ultimo aggiornamento: {datetime.fromtimestamp(all_valid_files[0][2]).strftime('%Y-%m-%d %H:%M:%S')}")
    
    if 'merged' in csv_file and 'complete' in csv_file:
        print(f"   🎯 File merged (PRIORITÀ per conversioni)")
    else:
        print(f"   ⚠️ File non merged")
    
    # Carica CSV
    print(f"\n📄 CARICAMENTO DATASET...")
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ CSV caricato: {csv_file}")
        print(f"   Righe: {len(df):,}")
        print(f"   Colonne: {len(df.columns)}")
        print(f"   Dimensione: {os.path.getsize(csv_file) / (1024*1024):.1f} MB")
    except Exception as e:
        print(f"❌ Errore caricamento CSV: {e}")
        return
    
    # Identifica variabili automaticamente
    print(f"\n🔍 IDENTIFICAZIONE VARIABILI...")
    
    # Mappa possibili nomi per ogni variabile
    variable_map = {
        'turbidity': ['TURB', 'TURBIDITY', 'BACKSCATTER', 'FLBBCD_BB_700_SCALED', 'FLBBCD_BB_700_NTU'],
        'chlorophyll': ['CHLA', 'CHLOROPHYLL', 'CHL_A', 'FLBBCD_CHL_SCALED'],
        'conductivity': ['CNDC', 'CONDUCTIVITY', 'CTD_CONDUCTIVITY', 'LEGATO_CONDUCTIVITY'],
        'temperature': ['TEMP', 'TEMPERATURE', 'CTD_TEMP', 'LEGATO_TEMPERATURE'],
        'pressure': ['PRES', 'PRESSURE', 'CTD_PRESSURE', 'LEGATO_PRESSURE'],
        'oxygen': ['DOXY', 'DISSOLVED_OXYGEN', 'OXYGEN', 'O2', 'LEGATO_CODA_DO'],
        'latitude': ['LATITUDE', 'NAV_LATITUDE'],
        'longitude': ['LONGITUDE', 'NAV_LONGITUDE']
    }
    
    # Trova variabili
    variables = {}
    for var_type, possible_names in variable_map.items():
        for name in possible_names:
            if name in df.columns:
                variables[var_type] = name
                break
        else:
            variables[var_type] = None
    
    # Report variabili trovate
    print(f"   Variabili identificate:")
    for var_type, var_name in variables.items():
        status = "✅" if var_name else "❌"
        print(f"     {status} {var_type.capitalize()}: {var_name}")
    
    # Crea backup
    print(f"\n💾 CREAZIONE BACKUP...")
    try:
        backup_file = csv_file.replace('.csv', '_backup_before_conversions.csv')
        df.to_csv(backup_file, index=False, encoding='utf-8')
        print(f"✅ Backup creato: {backup_file}")
    except Exception as e:
        print(f"❌ Errore backup: {e}")
        return
    
    # APPLICAZIONE CONVERSIONI
    print(f"\n🔄 APPLICAZIONE CONVERSIONI...")
    print("=" * 60)
    
    conversions_applied = []
    
    # 1. TORBIDITÀ
    if variables['turbidity']:
        try:
            convert_turbidity(df, variables['turbidity'])
            conversions_applied.append("Torbidità: m⁻¹ sr⁻¹ → NTU")
        except Exception as e:
            print(f"   ❌ Errore conversione torbidità: {e}")
    
    # 2. CLOROFILLA
    if variables['chlorophyll']:
        try:
            convert_chlorophyll(df, variables['chlorophyll'])
            conversions_applied.append("Clorofilla: µg/L → mg/m³")
        except Exception as e:
            print(f"   ❌ Errore conversione clorofilla: {e}")
    
    # 3. CONDUTTIVITÀ
    if variables['conductivity']:
        try:
            convert_conductivity(df, variables['conductivity'])
            conversions_applied.append("Conduttività: mS/cm → S/m")
        except Exception as e:
            print(f"   ❌ Errore conversione conduttività: {e}")
    
    # 4. COORDINATE
    if variables['latitude'] or variables['longitude']:
        try:
            convert_coordinates(df, variables['latitude'], variables['longitude'])
            conversions_applied.append("Coordinate: Gradi decimali → DMS")
        except Exception as e:
            print(f"   ❌ Errore conversione coordinate: {e}")
    
    # 5. OSSIGENO (richiede più variabili)
    if all(variables[var] for var in ['oxygen', 'temperature', 'conductivity', 'pressure']):
        try:
            convert_oxygen(
                df, 
                variables['oxygen'],
                variables['temperature'], 
                variables['conductivity'], 
                variables['pressure'],
                variables.get('latitude'),
                variables.get('longitude')
            )
            conversions_applied.append("Ossigeno: µmol/L → µmol/kg (TEOS-10)")
        except Exception as e:
            print(f"   ❌ Errore conversione ossigeno: {e}")
    else:
        print(f"\n🫧 CONVERSIONE OSSIGENO: SALTATA")
        print("-" * 50)
        missing = [var for var in ['oxygen', 'temperature', 'conductivity', 'pressure'] 
                  if not variables[var]]
        print(f"   ⚠️ Variabili mancanti: {missing}")
    
    # Salva CSV aggiornato
    print(f"\n💾 SALVATAGGIO DATASET CONVERTITO...")
    
    try:
        # Crea nome file con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = csv_file.replace('.csv', f'_units_converted_{timestamp}.csv')
        
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"✅ Dataset convertito salvato: {output_file}")
        print(f"   Dimensione: {os.path.getsize(output_file) / (1024*1024):.1f} MB")
        
        # Aggiorna anche il file originale
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"✅ File originale aggiornato: {csv_file}")
        
    except Exception as e:
        print(f"❌ Errore salvataggio: {e}")
        return
    
    # Crea/aggiorna metadati
    print(f"\n📝 AGGIORNAMENTO METADATI...")
    
    try:
        metadata_file = "dataset_metadata_conversions.txt"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write("CONVERSIONI UNITÀ APPLICATE - DATASET SEAEXPLORER\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Data conversione: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"File processato: {csv_file}\n")
            f.write(f"Righe totali: {len(df):,}\n")
            f.write(f"Colonne totali: {len(df.columns)}\n\n")
            
            f.write("CONVERSIONI APPLICATE:\n")
            for i, conversion in enumerate(conversions_applied, 1):
                f.write(f"  {i}. ✅ {conversion}\n")
            
            f.write("\nVARIABILI IDENTIFICATE:\n")
            for var_type, var_name in variables.items():
                status = "✅" if var_name else "❌"
                f.write(f"  {status} {var_type.capitalize()}: {var_name}\n")
            
            f.write(f"\nFILE BACKUP: {backup_file}\n")
            f.write(f"FILE OUTPUT: {output_file}\n")
        
        print(f"✅ Metadati salvati: {metadata_file}")
        
    except Exception as e:
        print(f"⚠️ Warning metadati: {e}")
    
    # CREA FILE CSV DI ESEMPIO VISUALIZZABILE
    print(f"\n📄 CREAZIONE FILE CSV DI ESEMPIO...")
    
    try:
        # Prendi un campione per visualizzazione
        sample_size = 300
        
        if len(df) > sample_size:
            # Campione rappresentativo: inizio, metà, fine
            third = len(df) // 3
            start_sample = df.head(100)
            mid_sample = df.iloc[third:third+100]
            end_sample = df.tail(100)
            sample_df = pd.concat([start_sample, mid_sample, end_sample], ignore_index=True)
        else:
            sample_df = df.copy()
        
        # Nome file di esempio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sample_file = f"units_converted_SAMPLE_{timestamp}.csv"
        
        # Salva campione
        sample_df.to_csv(sample_file, index=False, encoding='utf-8')
        
        sample_size_kb = os.path.getsize(sample_file) / 1024
        print(f"✅ CSV di esempio creato: {sample_file}")
        print(f"   Righe di esempio: {len(sample_df)}")
        print(f"   Dimensione: {sample_size_kb:.1f} KB (facilmente visualizzabile)")
        
        # Mostra anteprima delle conversioni applicate
        print(f"\n📊 ANTEPRIMA CONVERSIONI (prime 5 righe):")
        print("-" * 70)
        
        # Seleziona variabili che sono state convertite
        converted_vars = []
        var_priorities = ['TURB', 'CHLA', 'CNDC', 'DOXY', 'TEMP', 'PRES', 'LATITUDE', 'LONGITUDE']
        
        for var in var_priorities:
            if var in sample_df.columns:
                converted_vars.append(var)
                if len(converted_vars) >= 6:  # Limite per visualizzazione
                    break
        
        if converted_vars:
            preview_df = sample_df[converted_vars].head(5)
            print(preview_df.to_string(index=False))
        else:
            # Fallback: prime colonne disponibili
            preview_cols = list(sample_df.columns)[:6]
            preview_df = sample_df[preview_cols].head(5)
            print(preview_df.to_string(index=False))
        
        print(f"\n💡 APRI IL FILE: {sample_file}")
        print(f"   👁️ Visualizza facilmente le conversioni applicate")
        print(f"   📊 Confronta unità prima/dopo conversione")
        
    except Exception as e:
        print(f"⚠️ Warning creazione esempio: {e}")

    # RIEPILOGO FINALE
    print(f"\n🎯 CONVERSIONI COMPLETATE!")
    print("=" * 80)
    print(f"📊 Dataset processato: {len(df):,} righe × {len(df.columns)} colonne")
    print(f"✅ Conversioni applicate: {len(conversions_applied)}/5")
    
    for i, conversion in enumerate(conversions_applied, 1):
        print(f"  {i}. {conversion}")
    
    print(f"\n📄 File aggiornati:")
    print(f"  • Dataset principale: {csv_file}")
    print(f"  • Dataset con timestamp: {output_file}")
    print(f"  • CSV di esempio: {sample_file}")
    print(f"  • Backup originale: {backup_file}")
    print(f"  • Metadati: {metadata_file}")
    
    print(f"\n🚀 TUTTE LE CONVERSIONI COMPLETATE CON SUCCESSO!")
    
    # Verifica finale rapida
    print(f"\n🔍 VERIFICA FINALE RAPIDA...")
    
    for var_type, var_name in variables.items():
        if var_name and var_name in df.columns:
            data = df[var_name]
            valid_count = data.notna().sum()
            if valid_count > 0:
                print(f"  ✅ {var_type.capitalize()} ({var_name}): {valid_count:,} valori, range: {data.min():.3f} - {data.max():.3f}")

if __name__ == "__main__":
    convert_all_units_csv()