#!/usr/bin/env python3
"""
Script para hacer commit saltándose los hooks de pre-commit
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python commit_without_linting.py 'mensaje del commit'")
        sys.exit(1)
    
    commit_message = sys.argv[1]
    
    print("🚀 Haciendo commit saltándose pre-commit hooks...")
    
    try:
        # Agregar todos los cambios
        subprocess.run(["git", "add", "."], check=True)
        print("✅ Archivos agregados al staging")
        
        # Hacer commit saltándose pre-commit
        subprocess.run([
            "git", "commit", 
            "--no-verify",  # Saltarse pre-commit hooks
            "-m", commit_message
        ], check=True)
        
        print(f"🎉 Commit exitoso: {commit_message}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante el commit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 