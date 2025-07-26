#!/usr/bin/env python3
"""
Script de prueba con 3 archivos para la funcionalidad de extracción de duración de audio.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from services.audio_duration_extractor import AudioDurationExtractor


def get_first_3_podcasts_without_duration():
    """Obtiene los primeros 3 episodios sin duración para pruebas."""
    try:
        extractor = AudioDurationExtractor()
        podcasts_without_duration = extractor.get_podcasts_without_duration()
        
        # Tomar los primeros 3
        test_podcasts = podcasts_without_duration[:3]
        
        if not test_podcasts:
            print("❌ No hay episodios sin duración para probar")
            return []
        
        print(f"📋 Episodios seleccionados para prueba:")
        for podcast in test_podcasts:
            print(f"  Episodio #{podcast['program_number']}: {podcast.get('title', 'Sin título')}")
        
        return test_podcasts
        
    except Exception as e:
        print(f"❌ Error obteniendo episodios de prueba: {e}")
        return []


def main():
    """Función principal de prueba con 3 archivos."""
    start_time = datetime.now()
    
    print("🧪 PRUEBA CON 3 ARCHIVOS - EXTRACCIÓN DE DURACIÓN")
    print("=" * 70)
    print(f"⏰ Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Obtener episodios de prueba
    test_podcasts = get_first_3_podcasts_without_duration()
    if not test_podcasts:
        return
    
    # Extraer números de programa
    program_numbers = [p['program_number'] for p in test_podcasts]
    
    # Configurar log
    log_file = f"logs/audio_duration_test_3_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("logs", exist_ok=True)
    
    try:
        # Usar context manager para manejo automático
        with AudioDurationExtractor() as extractor:
            print("✅ Conexiones establecidas (Supabase + Synology)")
            
            # Procesar los 3 episodios
            print(f"\n🎵 Procesando {len(program_numbers)} episodios de prueba...")
            results = extractor.process_multiple_episodes(program_numbers)
            
            # Generar reporte
            report = extractor.generate_report(results)
            
            # Guardar reporte
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # Mostrar resultados detallados
            print("\n" + "=" * 70)
            print("📊 RESULTADOS DETALLADOS")
            
            for result in results:
                status = "✅ ÉXITO" if result['success'] else "❌ FALLO"
                print(f"\n{status} - Episodio #{result['program_number']}")
                
                if result['success']:
                    duration_seconds = result['duration']
                    duration_minutes = duration_seconds // 60
                    duration_remaining = duration_seconds % 60
                    print(f"  ⏱️  Duración: {duration_minutes}:{duration_remaining:02d} ({duration_seconds} segundos)")
                    print(f"  ⏰ Tiempo procesamiento: {result['processing_time']:.1f} segundos")
                else:
                    print(f"  ❌ Error: {result['error']}")
                    print(f"  ⏰ Tiempo procesamiento: {result['processing_time']:.1f} segundos")
            
            # Mostrar resumen
            print("\n" + "=" * 70)
            print("📊 RESUMEN DEL PROCESAMIENTO")
            print(f"📋 Total episodios: {report['metadata']['total_episodes']}")
            print(f"✅ Exitosos: {report['metadata']['successful']}")
            print(f"❌ Fallidos: {report['metadata']['failed']}")
            print(f"📈 Tasa de éxito: {report['metadata']['success_rate']:.1f}%")
            print(f"⏱️  Tiempo total: {report['metadata']['total_processing_time']:.1f} segundos")
            print(f"🎵 Duración total: {report['metadata']['total_duration_seconds']:,} segundos")
            print(f"📝 Log detallado: {log_file}")
            
            # Generar resumen en texto
            summary_file = log_file.replace('.json', '_summary.txt')
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"PRUEBA CON 3 ARCHIVOS - EXTRACCIÓN DE DURACIÓN\n")
                f.write(f"Fecha: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Duración total: {report['metadata']['total_processing_time']:.1f} segundos\n")
                f.write(f"Total episodios: {report['metadata']['total_episodes']}\n")
                f.write(f"Exitosos: {report['metadata']['successful']}\n")
                f.write(f"Fallidos: {report['metadata']['failed']}\n")
                f.write(f"Tasa de éxito: {report['metadata']['success_rate']:.1f}%\n")
                f.write(f"Duración total extraída: {report['metadata']['total_duration_seconds']:,} segundos\n")
            
            print(f"📋 Resumen en texto: {summary_file}")
            
            # Evaluación final
            if report['metadata']['success_rate'] == 100:
                print("\n🎉 ¡PRUEBA EXITOSA! Todos los episodios se procesaron correctamente")
                print("   Puedes proceder con la extracción completa")
            elif report['metadata']['success_rate'] >= 66:
                print("\n⚠️  PRUEBA PARCIALMENTE EXITOSA")
                print("   Algunos episodios fallaron, pero la funcionalidad básica funciona")
                print("   Revisa los errores antes de proceder con la extracción completa")
            else:
                print("\n❌ PRUEBA FALLIDA")
                print("   La mayoría de episodios fallaron")
                print("   Revisa la configuración antes de continuar")
    
    except Exception as e:
        print(f"❌ Error general: {e}")
        
        # Guardar error en log
        error_log = {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "start_time": start_time.isoformat()
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(error_log, f, indent=2, ensure_ascii=False)
    
    finally:
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        print(f"\n⏰ Duración total de la prueba: {total_duration:.1f} segundos")


if __name__ == "__main__":
    main() 