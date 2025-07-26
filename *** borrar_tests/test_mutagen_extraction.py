#!/usr/bin/env python3
"""
Script de prueba específica para Mutagen y extracción de duración de archivos MP3.
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))


def test_mutagen_import():
    """Prueba la importación de Mutagen."""
    print("🧪 PRUEBA DE IMPORTACIÓN DE MUTAGEN")
    print("=" * 50)
    
    try:
        from mutagen import File
        from mutagen.mp3 import MP3
        print("✅ Mutagen importado correctamente")
        print(f"  - File: {File}")
        print(f"  - MP3: {MP3}")
        return True
        
    except ImportError as e:
        print(f"❌ Error importando Mutagen: {e}")
        print("   Ejecuta: pip install mutagen")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_mp3_duration_extraction(file_path: Path):
    """Prueba la extracción de duración de un archivo MP3 específico."""
    print(f"\n🧪 PRUEBA DE EXTRACCIÓN DE DURACIÓN")
    print(f"📁 Archivo: {file_path}")
    print("=" * 50)
    
    try:
        from mutagen.mp3 import MP3
        
        if not file_path.exists():
            print(f"❌ El archivo no existe: {file_path}")
            return False
        
        # Obtener información del archivo
        file_size = file_path.stat().st_size
        print(f"📊 Tamaño del archivo: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
        
        # Cargar archivo con Mutagen
        print("📖 Cargando archivo con Mutagen...")
        audio = MP3(str(file_path))
        
        # Verificar que se cargó correctamente
        if not audio:
            print("❌ No se pudo cargar el archivo con Mutagen")
            return False
        
        print("✅ Archivo cargado correctamente con Mutagen")
        
        # Extraer duración
        if audio.length:
            duration_seconds = int(audio.length)
            duration_minutes = duration_seconds // 60
            duration_remaining = duration_seconds % 60
            
            print(f"⏱️  Duración extraída: {duration_minutes}:{duration_remaining:02d}")
            print(f"⏱️  Duración en segundos: {duration_seconds}")
            
            # Calcular bitrate aproximado
            if duration_seconds > 0:
                bitrate_kbps = (file_size * 8) / (duration_seconds * 1000)
                print(f"🎵 Bitrate aproximado: {bitrate_kbps:.0f} kbps")
            
            return True
        else:
            print("❌ No se pudo extraer la duración del archivo")
            return False
            
    except Exception as e:
        print(f"❌ Error extrayendo duración: {e}")
        return False


def test_multiple_formats():
    """Prueba diferentes formatos de audio."""
    print("\n🧪 PRUEBA DE DIFERENTES FORMATOS")
    print("=" * 50)
    
    try:
        from mutagen import File
        
        # Lista de archivos de prueba comunes
        test_files = [
            "test_audio.mp3",
            "test_audio.m4a",
            "test_audio.flac",
            "test_audio.wav"
        ]
        
        for filename in test_files:
            file_path = Path(filename)
            if file_path.exists():
                print(f"\n📁 Probando formato: {filename}")
                
                try:
                    audio = File(str(file_path))
                    if audio:
                        print(f"✅ Formato soportado: {filename}")
                        if hasattr(audio, 'length') and audio.length:
                            duration_seconds = int(audio.length)
                            duration_minutes = duration_seconds // 60
                            duration_remaining = duration_seconds % 60
                            print(f"  ⏱️  Duración: {duration_minutes}:{duration_remaining:02d}")
                        else:
                            print(f"  ⚠️  No se pudo extraer duración")
                    else:
                        print(f"❌ Formato no soportado: {filename}")
                except Exception as e:
                    print(f"❌ Error con {filename}: {e}")
            else:
                print(f"⚠️  Archivo no encontrado: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de formatos: {e}")
        return False


def test_error_handling():
    """Prueba el manejo de errores con archivos inválidos."""
    print("\n🧪 PRUEBA DE MANEJO DE ERRORES")
    print("=" * 50)
    
    try:
        from mutagen.mp3 import MP3
        
        # Probar con archivo que no existe
        print("📁 Probando con archivo inexistente...")
        try:
            audio = MP3("archivo_inexistente.mp3")
            print("❌ No debería haber cargado un archivo inexistente")
            return False
        except Exception as e:
            print(f"✅ Error manejado correctamente: {type(e).__name__}")
        
        # Probar con archivo de texto (no MP3)
        test_file = Path("test_text.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("Este no es un archivo MP3")
            
            print("📁 Probando con archivo de texto...")
            try:
                audio = MP3(str(test_file))
                print("⚠️  Mutagen intentó cargar archivo de texto")
            except Exception as e:
                print(f"✅ Error manejado correctamente: {type(e).__name__}")
            
            # Limpiar archivo de prueba
            test_file.unlink(missing_ok=True)
            
        except Exception as e:
            print(f"❌ Error creando archivo de prueba: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de manejo de errores: {e}")
        return False


def main():
    """Función principal de pruebas de Mutagen."""
    print("🎵 PRUEBAS DE MUTAGEN Y EXTRACCIÓN DE DURACIÓN")
    print("=" * 60)
    
    # Prueba de importación
    import_success = test_mutagen_import()
    
    if not import_success:
        print("\n❌ No se puede continuar sin Mutagen")
        return
    
    # Prueba con archivo MP3 específico
    test_mp3 = Path("test_audio.mp3")
    if test_mp3.exists():
        extraction_success = test_mp3_duration_extraction(test_mp3)
    else:
        print(f"\n⚠️  No se encontró archivo de prueba: {test_mp3}")
        print("   Para probar la extracción, crea un archivo MP3 llamado 'test_audio.mp3'")
        extraction_success = False
    
    # Prueba de diferentes formatos
    formats_success = test_multiple_formats()
    
    # Prueba de manejo de errores
    error_handling_success = test_error_handling()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS DE MUTAGEN")
    print(f"✅ Importación: {'PASÓ' if import_success else 'FALLÓ'}")
    print(f"✅ Extracción MP3: {'PASÓ' if extraction_success else 'FALLÓ'}")
    print(f"✅ Formatos múltiples: {'PASÓ' if formats_success else 'FALLÓ'}")
    print(f"✅ Manejo de errores: {'PASÓ' if error_handling_success else 'FALLÓ'}")
    
    passed_tests = sum([import_success, extraction_success, formats_success, error_handling_success])
    total_tests = 4
    
    if passed_tests == total_tests:
        print(f"\n🎉 ¡TODAS LAS PRUEBAS PASARON! ({passed_tests}/{total_tests})")
        print("   Mutagen está funcionando correctamente")
    elif passed_tests >= total_tests // 2:
        print(f"\n⚠️  PRUEBAS PARCIALMENTE EXITOSAS ({passed_tests}/{total_tests})")
        print("   Mutagen funciona básicamente, pero hay algunos problemas")
    else:
        print(f"\n❌ MUCHAS PRUEBAS FALLARON ({passed_tests}/{total_tests})")
        print("   Revisa la instalación de Mutagen")


if __name__ == "__main__":
    main() 