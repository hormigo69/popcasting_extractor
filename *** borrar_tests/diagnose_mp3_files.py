#!/usr/bin/env python3
"""
Script de diagnóstico para investigar problemas con archivos MP3.
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from services.audio_duration_extractor import AudioDurationExtractor
from mutagen.mp3 import MP3
from mutagen import File


def diagnose_mp3_file(file_path: Path):
    """Diagnostica un archivo MP3 específico."""
    print(f"\n🔍 DIAGNÓSTICO DE ARCHIVO: {file_path.name}")
    print("=" * 60)
    
    if not file_path.exists():
        print("❌ El archivo no existe")
        return False
    
    # Información básica del archivo
    file_size = file_path.stat().st_size
    print(f"📊 Tamaño: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    
    # Verificar los primeros bytes para identificar el formato
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)
            print(f"🔍 Header (hex): {header.hex()}")
            
            # Verificar si es MP3
            if header.startswith(b'ID3') or header.startswith(b'\xff\xfb') or header.startswith(b'\xff\xf3'):
                print("✅ Header MP3 detectado")
            else:
                print("❌ Header MP3 no detectado")
                print(f"   Primeros bytes: {header}")
    except Exception as e:
        print(f"❌ Error leyendo header: {e}")
    
    # Intentar cargar con Mutagen
    try:
        print("\n📖 Intentando cargar con Mutagen...")
        audio = MP3(str(file_path))
        
        if audio:
            print("✅ Archivo cargado con MP3()")
            
            # Verificar atributos
            print(f"   - info: {type(audio.info)}")
            print(f"   - tags: {type(audio.tags)}")
            
            if hasattr(audio.info, 'length'):
                duration = audio.info.length
                print(f"   - length: {duration}")
                if duration:
                    minutes = int(duration) // 60
                    seconds = int(duration) % 60
                    print(f"   - duración: {minutes}:{seconds:02d}")
            else:
                print("   - length: No disponible")
                
        else:
            print("❌ MP3() retornó None")
            
    except Exception as e:
        print(f"❌ Error con MP3(): {e}")
        print(f"   Tipo de error: {type(e).__name__}")
    
    # Intentar con File() genérico
    try:
        print("\n📖 Intentando cargar con File()...")
        audio = File(str(file_path))
        
        if audio:
            print("✅ Archivo cargado con File()")
            print(f"   - Tipo: {type(audio)}")
            
            if hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                duration = audio.info.length
                print(f"   - length: {duration}")
                if duration:
                    minutes = int(duration) // 60
                    seconds = int(duration) % 60
                    print(f"   - duración: {minutes}:{seconds:02d}")
            else:
                print("   - length: No disponible")
        else:
            print("❌ File() retornó None")
            
    except Exception as e:
        print(f"❌ Error con File(): {e}")
        print(f"   Tipo de error: {type(e).__name__}")
    
    return True


def test_specific_episodes():
    """Prueba episodios específicos que están fallando."""
    print("🧪 DIAGNÓSTICO DE EPISODIOS PROBLEMÁTICOS")
    print("=" * 60)
    
    # Episodios que sabemos que fallan
    problematic_episodes = [335, 334, 367, 366]
    
    try:
        with AudioDurationExtractor() as extractor:
            for episode in problematic_episodes:
                print(f"\n🎵 Probando episodio #{episode}")
                
                # Descargar archivo
                mp3_path = extractor.download_mp3_from_synology(episode)
                
                if mp3_path and mp3_path.exists():
                    # Diagnosticar archivo
                    diagnose_mp3_file(mp3_path)
                    
                    # Limpiar archivo
                    mp3_path.unlink(missing_ok=True)
                else:
                    print(f"❌ No se pudo descargar episodio #{episode}")
                    
    except Exception as e:
        print(f"❌ Error general: {e}")


def test_working_episodes():
    """Prueba episodios que sabemos que funcionan."""
    print("\n🧪 DIAGNÓSTICO DE EPISODIOS QUE FUNCIONAN")
    print("=" * 60)
    
    # Episodios que sabemos que funcionan
    working_episodes = [482, 483, 484]
    
    try:
        with AudioDurationExtractor() as extractor:
            for episode in working_episodes:
                print(f"\n🎵 Probando episodio #{episode}")
                
                # Descargar archivo
                mp3_path = extractor.download_mp3_from_synology(episode)
                
                if mp3_path and mp3_path.exists():
                    # Diagnosticar archivo
                    diagnose_mp3_file(mp3_path)
                    
                    # Limpiar archivo
                    mp3_path.unlink(missing_ok=True)
                else:
                    print(f"❌ No se pudo descargar episodio #{episode}")
                    
    except Exception as e:
        print(f"❌ Error general: {e}")


def main():
    """Función principal."""
    print("🔍 DIAGNÓSTICO DE ARCHIVOS MP3")
    print("=" * 60)
    
    # Probar episodios que funcionan
    test_working_episodes()
    
    # Probar episodios problemáticos
    test_specific_episodes()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNÓSTICO COMPLETADO")
    print("Revisa los resultados para identificar patrones en los archivos problemáticos")


if __name__ == "__main__":
    main() 