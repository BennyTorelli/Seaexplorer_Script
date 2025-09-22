#!/usr/bin/env python3
"""
ESECUTORE PIPELINE SEQUENZIALE SEAEXPLORER
===========================================

Questo script esegue la pipeline completa di elaborazione dati SeaExplorer 
nell'ordine sequenziale corretto con priorità file appropriata.

PANORAMICA PIPELINE:
- File Raw → CSV Separati → CSV Unito → CSV Unità Convertite → CSV Variabili Rinominate
- Ogni script seleziona automaticamente l'output del passo precedente
- Priorità file assicura elaborazione sequenziale appropriata

STATO ATTUALE (dall'analisi pipeline):
✅ Passo 1: convert_raw_to_separate_csv.py - COMPLETATO (183 file in csv_separati/)
✅ Passo 2: merge_mission_data_csv.py - COMPLETATO (mission_complete_merged_*.csv esiste)
✅ Passo 3: convert_all_units_csv.py - COMPLETATO (file units_converted esistono)
✅ Passo 4: rename_variables_csv.py - COMPLETATO (file renamed esistono)

La pipeline è attualmente completa! Ogni script ha priorità file appropriata:

1. convert_all_units_csv.py dà priorità ai file "merged" e "complete"
2. rename_variables_csv.py dà priorità ai file "units_converted"
3. Entrambi gli script escludono file già elaborati per prevenire duplicazione

MODIFICHE EFFETTUATE:
- Corrette funzioni extract_number() per ordinamento file appropriato
- Rimossa conversione decimal_to_dms() (mantenendo coordinate decimali)
- Aggiunta logica priorità file in tutti gli script
- Aggiunti pattern esclusione per file elaborati
"""

import subprocess
import sys
import os
from datetime import datetime

def run_script(script_name, description):
    """Esegue uno script con gestione errori"""
    print(f"\n{'='*60}")
    print(f"🔄 ESECUZIONE: {script_name}")
    print(f"📝 {description}")
    print(f"{'='*60}")
    
    try:
        # Usa l'ambiente Python configurato
        python_cmd = "/Users/benedettatorelli/Desktop/Datos_brutos_1/.venv/bin/python"
        result = subprocess.run([python_cmd, script_name], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ SUCCESSO: {script_name} completato")
            if result.stdout:
                print("📊 Output:")
                print(result.stdout)
        else:
            print(f"❌ ERRORE: {script_name} fallito")
            if result.stderr:
                print("🚨 Dettagli errore:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {script_name} ha impiegato più di 5 minuti")
        return False
    except Exception as e:
        print(f"💥 ECCEZIONE: {str(e)}")
        return False
    
    return True

def main():
    """Esegue la pipeline completa"""
    
    print("🌊 PIPELINE ELABORAZIONE DATI SEAEXPLORER")
    print("=" * 80)
    print(f"Iniziato alle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cambia alla directory logs dove si trovano gli script
    script_dir = "pld/logs"
    if os.path.exists(script_dir):
        os.chdir(script_dir)
        print(f"📁 Directory di lavoro: {os.getcwd()}")
    else:
        print(f"❌ Directory script {script_dir} non trovata!")
        return False
    
    # Passi pipeline con descrizioni
    pipeline_steps = [
        ("convert_raw_to_separate_csv.py", 
         "Converte file raw .pld1.raw in file individuali mission_XXX.csv"),
        
        ("merge_mission_data_csv.py", 
         "Unisce tutti i file CSV separati in un singolo dataset ordinato"),
        
        ("convert_all_units_csv.py", 
         "Converte unità di misura (torbidità, clorofilla, conduttività, ossigeno)"),
        
        ("rename_variables_csv.py", 
         "Rinomina variabili con nomenclatura oceanografica standard")
    ]
    
    print(f"\n🎯 PIANO ESECUZIONE PIPELINE:")
    for i, (script, desc) in enumerate(pipeline_steps, 1):
        print(f"   {i}. {script}")
        print(f"      → {desc}")
    
    # Chiedi conferma
    print(f"\n⚠️  Questo eseguirà la pipeline completa sequenzialmente.")
    print(f"💡 Ogni script selezionerà automaticamente il file input appropriato.")
    response = input(f"\n🤔 Vuoi procedere? (s/N): ").strip().lower()
    
    if response != 's':
        print("❌ Esecuzione pipeline annullata.")
        return False
    
    # Esegui pipeline
    success_count = 0
    for i, (script, description) in enumerate(pipeline_steps, 1):
        print(f"\n\n🎯 PASSO {i}/{len(pipeline_steps)}")
        
        if not os.path.exists(script):
            print(f"❌ Script {script} non trovato!")
            continue
            
        if run_script(script, description):
            success_count += 1
            print(f"✅ Passo {i} completato con successo")
        else:
            print(f"❌ Passo {i} fallito")
            print(f"🛑 Interruzione esecuzione pipeline")
            break
    
    # Riassunto
    print(f"\n" + "="*80)
    print(f"📊 RIASSUNTO ESECUZIONE PIPELINE")
    print(f"="*80)
    print(f"✅ Passi riusciti: {success_count}/{len(pipeline_steps)}")
    print(f"⏰ Completato alle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_count == len(pipeline_steps):
        print(f"🎉 PIPELINE COMPLETATA CON SUCCESSO!")
        print(f"💡 I tuoi dati SeaExplorer sono stati completamente elaborati.")
    else:
        print(f"⚠️  Pipeline incompleta. Controlla i messaggi di errore sopra.")
    
    return success_count == len(pipeline_steps)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)