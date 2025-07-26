#!/usr/bin/env python3
"""
Ejemplo de uso para la extracción de duración de audio MP3.
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from services.audio_duration_extractor import AudioDurationExtractor


def example_basic_usage():
    """Ejemplo básico de uso."""
    print("🎵 EJEMPLO BÁSICO DE USO")
    print("=" * 50)
    
    try:
        # Usar context manager (recomendado)
        with AudioDurationExtractor() as extractor:
            print("✅ Conexiones establecidas")
            
            # Obtener episodios sin duración
            episodes_without_duration = extractor.get_podcasts_without_duration()
            print(f"📊 Episodios sin duración: {len(episodes_without_duration)}")
            
            if episodes_without_duration:
                # Procesar el primer episodio como ejemplo
                first_episode = episodes_without_duration[0]
                program_number = first_episode['program_number']
                
                print(f"\n🎵 Procesando episodio #{program_number} como ejemplo...")
                result = extractor.process_single_episode(program_number)
                
                if result['success']:
                    duration_seconds = result['duration']
                    duration_minutes = duration_seconds // 60
                    duration_remaining = duration_seconds % 60
                    
                    print(f"✅ Éxito!")
                    print(f"  ⏱️  Duración: {duration_minutes}:{duration_remaining:02d}")
                    print(f"  ⏰ Tiempo procesamiento: {result['processing_time']:.1f}s")
                else:
                    print(f"❌ Error: {result['error']}")
            else:
                print("✅ Todos los episodios ya tienen duración")
                
    except Exception as e:
        print(f"❌ Error: {e}")


def example_selective_processing():
    """Ejemplo de procesamiento selectivo."""
    print("\n🎵 EJEMPLO DE PROCESAMIENTO SELECTIVO")
    print("=" * 50)
    
    try:
        # Episodios específicos a procesar
        episodes_to_process = [482, 483, 484]
        
        with AudioDurationExtractor() as extractor:
            print(f"🎵 Procesando episodios específicos: {episodes_to_process}")
            
            results = extractor.process_multiple_episodes(episodes_to_process)
            
            # Mostrar resultados
            successful = sum(1 for r in results if r['success'])
            print(f"\n📊 Resultados: {successful}/{len(results)} exitosos")
            
            for result in results:
                status = "✅" if result['success'] else "❌"
                print(f"{status} Episodio #{result['program_number']}")
                
                if result['success']:
                    duration_seconds = result['duration']
                    duration_minutes = duration_seconds // 60
                    duration_remaining = duration_seconds % 60
                    print(f"    ⏱️  Duración: {duration_minutes}:{duration_remaining:02d}")
                else:
                    print(f"    ❌ Error: {result['error']}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_report_generation():
    """Ejemplo de generación de reportes."""
    print("\n🎵 EJEMPLO DE GENERACIÓN DE REPORTES")
    print("=" * 50)
    
    try:
        with AudioDurationExtractor() as extractor:
            # Procesar algunos episodios
            test_episodes = [482, 483]
            results = extractor.process_multiple_episodes(test_episodes)
            
            # Generar reporte
            report = extractor.generate_report(results)
            
            # Mostrar estadísticas
            metadata = report['metadata']
            print(f"📊 Estadísticas del procesamiento:")
            print(f"  📋 Total episodios: {metadata['total_episodes']}")
            print(f"  ✅ Exitosos: {metadata['successful']}")
            print(f"  ❌ Fallidos: {metadata['failed']}")
            print(f"  📈 Tasa de éxito: {metadata['success_rate']:.1f}%")
            print(f"  ⏱️  Tiempo total: {metadata['total_processing_time']:.1f}s")
            print(f"  🎵 Duración total: {metadata['total_duration_seconds']:,} segundos")
            
            # Mostrar detalles de cada episodio
            print(f"\n📋 Detalles por episodio:")
            for result in results:
                status = "✅" if result['success'] else "❌"
                print(f"  {status} Episodio #{result['program_number']}")
                
                if result['success']:
                    duration_seconds = result['duration']
                    duration_minutes = duration_seconds // 60
                    duration_remaining = duration_seconds % 60
                    print(f"      ⏱️  {duration_minutes}:{duration_remaining:02d} ({duration_seconds}s)")
                    print(f"      ⏰ {result['processing_time']:.1f}s")
                else:
                    print(f"      ❌ {result['error']}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_manual_connection():
    """Ejemplo de uso manual sin context manager."""
    print("\n🎵 EJEMPLO DE USO MANUAL")
    print("=" * 50)
    
    try:
        # Crear instancia
        extractor = AudioDurationExtractor()
        
        # Conectar manualmente a Synology
        from synology.synology_client import SynologyClient
        extractor.synology = SynologyClient()
        
        if extractor.synology.login():
            print("✅ Conexión a Synology establecida")
            
            # Procesar un episodio
            result = extractor.process_single_episode(482)
            
            if result['success']:
                duration_seconds = result['duration']
                duration_minutes = duration_seconds // 60
                duration_remaining = duration_seconds % 60
                print(f"✅ Duración extraída: {duration_minutes}:{duration_remaining:02d}")
            else:
                print(f"❌ Error: {result['error']}")
            
            # Cerrar conexión
            extractor.synology.logout()
            print("✅ Conexión cerrada")
        else:
            print("❌ No se pudo conectar a Synology")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_error_handling():
    """Ejemplo de manejo de errores."""
    print("\n🎵 EJEMPLO DE MANEJO DE ERRORES")
    print("=" * 50)
    
    try:
        with AudioDurationExtractor() as extractor:
            # Intentar procesar un episodio que no existe
            print("🔍 Probando con episodio inexistente...")
            result = extractor.process_single_episode(99999)
            
            if not result['success']:
                print(f"✅ Error manejado correctamente: {result['error']}")
            else:
                print("⚠️  Inesperado: episodio inexistente procesado")
            
            # Verificar episodios sin duración
            episodes_without_duration = extractor.get_podcasts_without_duration()
            print(f"📊 Episodios sin duración disponibles: {len(episodes_without_duration)}")
            
            if episodes_without_duration:
                print("📋 Primeros 3 episodios sin duración:")
                for i, episode in enumerate(episodes_without_duration[:3]):
                    print(f"  {i+1}. Episodio #{episode['program_number']}: {episode.get('title', 'Sin título')}")
                    
    except Exception as e:
        print(f"❌ Error general: {e}")


def main():
    """Función principal con todos los ejemplos."""
    print("🎵 EJEMPLOS DE USO - EXTRACCIÓN DE DURACIÓN DE AUDIO")
    print("=" * 70)
    
    # Ejemplo básico
    example_basic_usage()
    
    # Ejemplo selectivo
    example_selective_processing()
    
    # Ejemplo de reportes
    example_report_generation()
    
    # Ejemplo manual
    example_manual_connection()
    
    # Ejemplo de manejo de errores
    example_error_handling()
    
    print("\n" + "=" * 70)
    print("🎉 EJEMPLOS COMPLETADOS")
    print("📚 Revisa la documentación en docs/README_AUDIO_DURATION.md")
    print("🧪 Ejecuta las pruebas con: python tests/test_audio_duration.py")


if __name__ == "__main__":
    main() 