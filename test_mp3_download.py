#!/usr/bin/env python3
"""
Script de prueba para descargar un MP3 de prueba sin subir al NAS.
"""

import sys
import os
import requests
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(__file__))

from services.config import get_database_module


def download_test_mp3():
    """Descarga un MP3 de prueba para verificar que funciona."""
    print("🎵 Probando descarga de MP3...")
    
    try:
        db_module = get_database_module()
        db = db_module.SupabaseDatabase()
        
        # Obtener el primer episodio con download_url
        podcasts = db.get_all_podcasts()
        test_podcast = None
        
        for podcast in podcasts:
            if podcast.get('download_url'):
                test_podcast = podcast
                break
        
        if not test_podcast:
            print("❌ No se encontró ningún episodio con URL de descarga")
            return False
        
        print(f"📥 Probando con episodio #{test_podcast['program_number']}")
        print(f"🔗 URL: {test_podcast['download_url']}")
        
        # Crear directorio temporal
        temp_dir = Path("test_download")
        temp_dir.mkdir(exist_ok=True)
        
        # Descargar archivo de prueba
        test_filename = temp_dir / f"test_episode_{test_podcast['program_number']}.mp3"
        
        print(f"💾 Descargando a: {test_filename}")
        
        response = requests.get(test_podcast['download_url'], stream=True, timeout=30)
        response.raise_for_status()
        
        file_size = 0
        with open(test_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                file_size += len(chunk)
        
        # Verificar que el archivo se descargó correctamente
        if test_filename.exists() and file_size > 0:
            print(f"✅ Descarga exitosa: {file_size:,} bytes")
            print(f"📁 Archivo guardado en: {test_filename}")
            
            # Limpiar archivo de prueba
            test_filename.unlink()
            temp_dir.rmdir()
            
            return True
        else:
            print("❌ Error: El archivo no se descargó correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False


if __name__ == "__main__":
    download_test_mp3() 