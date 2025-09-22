#!/usr/bin/env python3
"""
ANALIZZATORE STATO PIPELINE SEAEXPLORER
=======================================

Questo script analizza lo stato attuale della pipeline di elaborazione dati
e fornisce un riassunto di quale passo è stato completato e cosa rimane da fare.

La pipeline segue questo ordine:
1. convert_raw_to_separate_csv.py - Converte file raw in CSV separati
2. merge_mission_data_csv.py - Unisce i CSV in un file missione completo  
3. convert_all_units_csv.py - Converte le unità di misura
4. rename_variables_csv.py - Rinomina le variabili secondo convenzioni

Autore: Script di supporto per pipeline SeaExplorer
Data: Settembre 2024
"""

import os
import glob
from datetime import datetime

def trova_file_recenti(pattern, cartella="."):
    """Trova i file più recenti che corrispondono al pattern"""
    percorso_completo = os.path.join(cartella, pattern)
    file = glob.glob(percorso_completo)
    if not file:
        return []
    
    # Ordina per data di modifica (più recente prima)
    file.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return file

def analizza_stato_pipeline():
    """Analizza lo stato attuale della pipeline"""
    print("🔍 ANALISI STATO PIPELINE SEAEXPLORER")
    print("=" * 50)
    
    # Controlla file raw
    file_raw = trova_file_recenti("*.gli")
    print(f"\n📁 FILE RAW (.gli): {len(file_raw)} trovati")
    if file_raw:
        print(f"   Più recente: {os.path.basename(file_raw[0])}")
    
    # Controlla CSV separati
    csv_separati = trova_file_recenti("csv_separati/*.csv")
    print(f"\n📊 CSV SEPARATI: {len(csv_separati)} trovati")
    if csv_separati:
        print(f"   Cartella: csv_separati/ ({len(csv_separati)} file)")
    
    # Controlla file merged
    file_merged = trova_file_recenti("mission_complete_merged_*.csv")
    print(f"\n🔗 FILE UNITI: {len(file_merged)} trovati")
    for file in file_merged[:3]:  # Mostra i primi 3
        print(f"   - {os.path.basename(file)}")
    
    # Controlla file con unità convertite
    file_units = trova_file_recenti("mission_complete_merged_*_units_converted.csv")
    print(f"\n⚡ UNITÀ CONVERTITE: {len(file_units)} trovati")
    for file in file_units[:3]:
        print(f"   - {os.path.basename(file)}")
    
    # Controlla file con variabili rinominate
    file_renamed = trova_file_recenti("mission_complete_merged_*_units_converted_renamed.csv")
    print(f"\n🏷️  VARIABILI RINOMINATE: {len(file_renamed)} trovati")
    for file in file_renamed[:3]:
        print(f"   - {os.path.basename(file)}")
    
    print("\n" + "=" * 50)
    print("📋 STATO PIPELINE:")
    
    # Determina stato di ogni passo
    stato_passi = {
        "Passo 1 (CSV Separati)": "✅ COMPLETATO" if csv_separati else "❌ NON COMPLETATO",
        "Passo 2 (File Uniti)": "✅ COMPLETATO" if file_merged else "❌ NON COMPLETATO", 
        "Passo 3 (Unità Convertite)": "✅ COMPLETATO" if file_units else "❌ NON COMPLETATO",
        "Passo 4 (Variabili Rinominate)": "✅ COMPLETATO" if file_renamed else "✅ COMPLETATO" if file_renamed else "❌ NON COMPLETATO"
    }
    
    for passo, stato in stato_passi.items():
        print(f"   {passo}: {stato}")
    
    # Raccomandazioni
    print("\n💡 RACCOMANDAZIONI:")
    if not csv_separati:
        print("   → Esegui convert_raw_to_separate_csv.py per iniziare")
    elif not file_merged:
        print("   → Esegui merge_mission_data_csv.py per unire i CSV")
    elif not file_units:
        print("   → Esegui convert_all_units_csv.py per convertire unità")
    elif not file_renamed:
        print("   → Esegui rename_variables_csv.py per completare la pipeline")
    else:
        print("   → Pipeline completa! Tutti i passi sono stati eseguiti.")
        if file_renamed:
            print(f"   → File finale: {os.path.basename(file_renamed[0])}")

def main():
    """Funzione principale"""
    try:
        analizza_stato_pipeline()
    except Exception as e:
        print(f"❌ Errore durante l'analisi: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())