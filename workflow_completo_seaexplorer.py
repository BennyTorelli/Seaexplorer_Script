#!/usr/bin/env python3
"""
WORKFLOW COMPLETO SEAEXPLORER - AUTOMATICO
Esegue tutti gli step in sequenza:
1. Conversione Raw → CSV separati
2. Merge CSV → Dataset unito
3. Conversione unità → Dataset con unità corrette
4. Rename variabili → Dataset finale con nomi standard
"""

import os
import sys
import subprocess
from datetime import datetime

def run_script(script_path, description):
    """
    Esegue uno script Python e gestisce errori
    """
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        # Ottieni il path dell'interprete Python
        python_path = "/Users/benedettatorelli/Desktop/Datos_brutos_1/.venv/bin/python"
        
        # Esegui lo script
        result = subprocess.run([python_path, script_path], 
                              capture_output=True, 
                              text=True,
                              cwd="/Users/benedettatorelli/Desktop/Datos_brutos_1")
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {description} completato con successo!")
            return True
        else:
            print(f"❌ Errore in {description}:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Errore esecuzione {script_path}: {e}")
        return False

def workflow_completo():
    """
    Esegue il workflow completo SeaExplorer
    """
    print("🌊 WORKFLOW COMPLETO SEAEXPLORER")
    print("=" * 80)
    print("Sequenza automatica:")
    print("1. 📂 Conversione Raw → CSV separati")
    print("2. 🔗 Merge CSV → Dataset unito")  
    print("3. 🔧 Conversione unità → Dataset con unità corrette")
    print("4. 🏷️ Rename variabili → Dataset finale")
    print("=" * 80)
    
    # Directory base
    base_dir = "/Users/benedettatorelli/Desktop/Datos_brutos_1"
    os.chdir(base_dir)
    
    # Script da eseguire in sequenza
    scripts = [
        {
            "path": "pld/logs/convert_raw_to_separate_csv.py",
            "description": "STEP 1: Conversione Raw → CSV separati",
            "skip_confirm": False
        },
        {
            "path": "pld/logs/merge_mission_data_csv.py", 
            "description": "STEP 2: Merge CSV → Dataset unito",
            "skip_confirm": False
        },
        {
            "path": "pld/logs/convert_all_units_csv.py",
            "description": "STEP 3: Conversione unità → Dataset corretto",
            "skip_confirm": False
        },
        {
            "path": "pld/logs/rename_variables_csv.py",
            "description": "STEP 4: Rename variabili → Dataset finale",
            "skip_confirm": False
        }
    ]
    
    # Esegui tutti gli script in sequenza
    for i, script in enumerate(scripts, 1):
        success = run_script(script["path"], script["description"])
        
        if not success:
            print(f"\n💥 WORKFLOW INTERROTTO al passo {i}")
            print(f"❌ Errore in: {script['description']}")
            return False
        
        # Pausa tra gli step (opzionale)
        if i < len(scripts):
            print(f"\n⏳ Passaggio al passo {i+1}...")
            # input("Premi ENTER per continuare...")  # Rimuovi se vuoi automatico
    
    # Workflow completato
    print(f"\n🎉 WORKFLOW COMPLETO TERMINATO CON SUCCESSO!")
    print("=" * 80)
    print("📊 RISULTATI FINALI:")
    print("1. ✅ File raw convertiti in CSV separati")
    print("2. ✅ CSV uniti in dataset completo")
    print("3. ✅ Unità di misura convertite")
    print("4. ✅ Variabili rinominate con nomi standard")
    print("\n💡 Il tuo dataset finale è pronto per l'analisi!")
    
    # Mostra file finali
    import glob
    final_files = glob.glob("*renamed*.csv")
    if final_files:
        latest_file = max(final_files, key=os.path.getmtime)
        print(f"📁 Dataset finale: {latest_file}")
    
    return True

if __name__ == "__main__":
    workflow_completo()