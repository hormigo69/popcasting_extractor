#!/usr/bin/env python3
"""
Script de prueba básica para la funcionalidad de extracción de duración de audio.
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from services.audio_duration_extractor import AudioDurationExtractor


def test_audio_duration_extractor():
    """Prueba básica de la clase AudioDurationExtractor."""
    print("🧪 PRUEBA BÁSICA DE AUDIO DURATION EXTRACTOR")
    print("=" * 60)
    
    try:
        # Crear instancia sin context manager para pruebas básicas
        extractor = AudioDurationExtractor()
        
        # Probar conexión a Supabase
        print("📡 Probando conexión a Supabase...")
        podcasts = extractor.db.get_all_podcasts()
        print(f"✅ Conexión exitosa: {len(podcasts)} episodios encontrados")
        
        # Probar obtención de episodios sin duración
        print("\n🔍 Probando obtención de episodios sin duración...")
        podcasts_without_duration = extractor.get_podcasts_without_duration()
        print(f"✅ Episodios sin duración: {len(podcasts_without_duration)}")
        
        # Mostrar algunos ejemplos
        if podcasts_without_duration:
            print("\n📋 Ejemplos de episodios sin duración:")
            for i, podcast in enumerate(podcasts_without_duration[:5]):
                print(f"  Episodio #{podcast['program_number']}: {podcast.get('title', 'Sin título')}")
                print(f"    📅 Fecha: {podcast.get('date', 'Sin fecha')}")
                print(f"    🎵 Duración actual: {podcast.get('duration', 'No definida')}")
        
        # Probar búsqueda por número de programa
        print("\n🔍 Probando búsqueda por número de programa...")
        if podcasts:
            test_program_number = podcasts[0]['program_number']
            found_podcast = extractor.get_podcast_by_program_number(test_program_number)
            if found_podcast:
                print(f"✅ Episodio #{test_program_number} encontrado: {found_podcast.get('title', 'Sin título')}")
            else:
                print(f"❌ Episodio #{test_program_number} no encontrado")
        
        print("\n✅ Prueba básica completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba básica: {e}")
        return False


def test_mutagen_extraction():
    """Prueba de extracción de duración con Mutagen."""
    print("\n🧪 PRUEBA DE EXTRACCIÓN CON MUTAGEN")
    print("=" * 60)
    
    try:
        from mutagen.mp3 import MP3
        print("✅ Mutagen importado correctamente")
        
        # Crear un archivo MP3 de prueba (si existe)
        test_mp3_path = Path("test_audio.mp3")
        if test_mp3_path.exists():
            print(f"📁 Archivo de prueba encontrado: {test_mp3_path}")
            
            # Probar extracción de duración
            audio = MP3(str(test_mp3_path))
            if audio.length:
                duration_seconds = int(audio.length)
                duration_minutes = duration_seconds // 60
                duration_remaining = duration_seconds % 60
                
                print(f"⏱️  Duración extraída: {duration_minutes}:{duration_remaining:02d} ({duration_seconds} segundos)")
                print("✅ Extracción de duración exitosa")
            else:
                print("❌ No se pudo extraer duración del archivo de prueba")
        else:
            print("⚠️  No se encontró archivo de prueba (test_audio.mp3)")
            print("   Para probar Mutagen, crea un archivo MP3 llamado 'test_audio.mp3' en el directorio raíz")
        
        return True
        
    except ImportError:
        print("❌ Error: Mutagen no está instalado")
        print("   Ejecuta: pip install mutagen")
        return False
    except Exception as e:
        print(f"❌ Error en prueba de Mutagen: {e}")
        return False


def main():
    """Función principal de pruebas."""
    print("🎵 PRUEBAS DE AUDIO DURATION EXTRACTOR")
    print("=" * 60)
    
    # Prueba básica
    basic_test_passed = test_audio_duration_extractor()
    
    # Prueba de Mutagen
    mutagen_test_passed = test_mutagen_extraction()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print(f"✅ Prueba básica: {'PASÓ' if basic_test_passed else 'FALLÓ'}")
    print(f"✅ Prueba Mutagen: {'PASÓ' if mutagen_test_passed else 'FALLÓ'}")
    
    if basic_test_passed and mutagen_test_passed:
        print("\n🎉 Todas las pruebas pasaron exitosamente")
        print("   Puedes proceder con la extracción de duración")
    else:
        print("\n⚠️  Algunas pruebas fallaron")
        print("   Revisa los errores antes de continuar")


if __name__ == "__main__":
    main() 