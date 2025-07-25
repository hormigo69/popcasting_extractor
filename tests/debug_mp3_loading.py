#!/usr/bin/env python3
"""
Script de debug detallado para investigar problemas con carga de MP3.
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from services.audio_duration_extractor import AudioDurationExtractor
from mutagen.mp3 import MP3
from mutagen import File
from mutagen.easyid3 import EasyID3


def debug_mp3_loading(file_path: Path):
    """Debug detallado de carga de MP3."""
    print(f"\n🔍 DEBUG DETALLADO: {file_path.name}")
    print("=" * 80)
    
    if not file_path.exists():
        print("❌ El archivo no existe")
        return False
    
    # Información básica del archivo
    file_size = file_path.stat().st_size
    print(f"📊 Tamaño: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    
    # Verificar los primeros bytes para identificar el formato
    try:
        with open(file_path, 'rb') as f:
            header = f.read(32)  # Leer más bytes
            print(f"🔍 Header (hex): {header.hex()}")
            print(f"🔍 Header (ascii): {header}")
            
            # Verificar si es MP3
            if header.startswith(b'ID3'):
                print("✅ Header ID3 detectado (con metadatos)")
            elif header.startswith(b'\xff\xfb') or header.startswith(b'\xff\xf3'):
                print("✅ Header MP3 sin metadatos detectado")
            else:
                print("❌ Header MP3 no detectado")
                print(f"   Primeros bytes: {header[:16]}")
    except Exception as e:
        print(f"❌ Error leyendo header: {e}")
    
    # Intentar diferentes métodos de carga
    print("\n📖 PRUEBAS DE CARGA CON MUTAGEN:")
    
    # Método 1: MP3() directo
    try:
        print("1️⃣ Intentando MP3() directo...")
        audio = MP3(str(file_path))
        print(f"   Resultado: {audio}")
        if audio:
            print(f"   Tipo: {type(audio)}")
            print(f"   Info: {type(audio.info) if hasattr(audio, 'info') else 'No info'}")
            print(f"   Tags: {type(audio.tags) if hasattr(audio, 'tags') else 'No tags'}")
            if hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                print(f"   Length: {audio.info.length}")
        else:
            print("   ❌ MP3() retornó None")
    except Exception as e:
        print(f"   ❌ Error con MP3(): {e}")
        print(f"   Tipo de error: {type(e).__name__}")
    
    # Método 2: File() genérico
    try:
        print("2️⃣ Intentando File() genérico...")
        audio = File(str(file_path))
        print(f"   Resultado: {audio}")
        if audio:
            print(f"   Tipo: {type(audio)}")
            if hasattr(audio, 'info'):
                print(f"   Info: {type(audio.info)}")
                if hasattr(audio.info, 'length'):
                    print(f"   Length: {audio.info.length}")
        else:
            print("   ❌ File() retornó None")
    except Exception as e:
        print(f"   ❌ Error con File(): {e}")
        print(f"   Tipo de error: {type(e).__name__}")
    
    # Método 3: EasyID3
    try:
        print("3️⃣ Intentando EasyID3...")
        audio = EasyID3(str(file_path))
        print(f"   Resultado: {audio}")
        if audio:
            print(f"   Tipo: {type(audio)}")
            print(f"   Tags: {audio}")
    except Exception as e:
        print(f"   ❌ Error con EasyID3: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
    
    # Método 4: Verificar si el archivo está corrupto
    try:
        print("4️⃣ Verificando integridad del archivo...")
        with open(file_path, 'rb') as f:
            # Leer todo el archivo para verificar integridad
            f.seek(0, 2)  # Ir al final
            file_size_check = f.tell()
            print(f"   Tamaño real: {file_size_check:,} bytes")
            
            if file_size_check == file_size:
                print("   ✅ Tamaño del archivo correcto")
            else:
                print(f"   ❌ Tamaño incorrecto: esperado {file_size}, real {file_size_check}")
                
            # Verificar si el archivo termina correctamente
            f.seek(-128, 2)  # Últimos 128 bytes
            end_bytes = f.read()
            print(f"   Últimos bytes: {end_bytes.hex()}")
            
    except Exception as e:
        print(f"   ❌ Error verificando integridad: {e}")
    
    return True


def test_with_working_file():
    """Probar con un archivo que sabemos que funciona."""
    print("\n🧪 PRUEBA CON ARCHIVO QUE FUNCIONA")
    print("=" * 80)
    
    try:
        with AudioDurationExtractor() as extractor:
            # Probar con episodio #482 que sabemos que funciona
            mp3_path = extractor.download_mp3_from_synology(482)
            
            if mp3_path and mp3_path.exists():
                debug_mp3_loading(mp3_path)
                mp3_path.unlink(missing_ok=True)
            else:
                print("❌ No se pudo descargar episodio #482")
                
    except Exception as e:
        print(f"❌ Error general: {e}")


def test_with_problematic_file():
    """Probar con un archivo problemático."""
    print("\n🧪 PRUEBA CON ARCHIVO PROBLEMÁTICO")
    print("=" * 80)
    
    try:
        with AudioDurationExtractor() as extractor:
            # Probar con episodio #446 que sabemos que falla
            mp3_path = extractor.download_mp3_from_synology(446)
            
            if mp3_path and mp3_path.exists():
                debug_mp3_loading(mp3_path)
                mp3_path.unlink(missing_ok=True)
            else:
                print("❌ No se pudo descargar episodio #446")
                
    except Exception as e:
        print(f"❌ Error general: {e}")


def test_mutagen_installation():
    """Verificar la instalación de Mutagen."""
    print("\n🔧 VERIFICACIÓN DE INSTALACIÓN DE MUTAGEN")
    print("=" * 80)
    
    try:
        import mutagen
        print(f"✅ Mutagen instalado: versión {mutagen.version}")
        
        # Verificar módulos específicos
        modules_to_check = [
            'mutagen.mp3',
            'mutagen.id3', 
            'mutagen.easyid3',
            'mutagen.file'
        ]
        
        for module in modules_to_check:
            try:
                __import__(module)
                print(f"✅ {module} disponible")
            except ImportError as e:
                print(f"❌ {module} no disponible: {e}")
                
    except ImportError as e:
        print(f"❌ Mutagen no instalado: {e}")


def main():
    """Función principal."""
    print("🔍 DEBUG DETALLADO DE CARGA DE MP3")
    print("=" * 80)
    
    # Verificar instalación
    test_mutagen_installation()
    
    # Probar archivos
    test_with_working_file()
    test_with_problematic_file()
    
    print("\n" + "=" * 80)
    print("📊 DEBUG COMPLETADO")
    print("Revisa los resultados para identificar el problema específico")


if __name__ == "__main__":
    main() 