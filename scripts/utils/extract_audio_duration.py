#!/usr/bin/env python3
"""
Script principal para extraer la duración de archivos MP3 y actualizar Supabase.
Utiliza la clase AudioDurationExtractor para procesar episodios desde Synology NAS.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz al path para importar servicios
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.audio_duration_extractor import AudioDurationExtractor


def main():
    """Función principal del script."""
    start_time = datetime.now()

    print("🎵 EXTRACTOR DE DURACIÓN DE AUDIO MP3")
    print("=" * 60)
    print(f"⏰ Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)

    # Configurar archivo de log
    log_file = (
        f"logs/audio_duration_extraction_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    )

    try:
        # Usar context manager para manejo automático de conexiones
        with AudioDurationExtractor() as extractor:
            print("✅ Conexiones establecidas (Supabase + Synology)")

            # Procesar todos los episodios sin duración
            print("\n🔍 Buscando episodios sin duración...")
            results = extractor.process_all_episodes_without_duration()

            if not results:
                print("✅ No hay episodios para procesar")
                return

            # Generar reporte
            report = extractor.generate_report(results)

            # Guardar reporte en archivo JSON
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            # Mostrar resumen
            print("\n" + "=" * 60)
            print("📊 RESUMEN DEL PROCESAMIENTO")
            print(f"📋 Total episodios: {report['metadata']['total_episodes']}")
            print(f"✅ Exitosos: {report['metadata']['successful']}")
            print(f"❌ Fallidos: {report['metadata']['failed']}")
            print(f"📈 Tasa de éxito: {report['metadata']['success_rate']:.1f}%")
            print(
                f"⏱️  Tiempo total: {report['metadata']['total_processing_time']:.1f} segundos"
            )
            print(
                f"🎵 Duración total: {report['metadata']['total_duration_seconds']:,} segundos"
            )
            print(f"📝 Log detallado: {log_file}")

            # Mostrar errores si los hay
            if report["metadata"]["failed"] > 0:
                print("\n❌ EPISODIOS CON ERRORES:")
                for result in results:
                    if not result["success"]:
                        print(
                            f"  Episodio #{result['program_number']}: {result['error']}"
                        )

            # Generar resumen en texto
            summary_file = log_file.replace(".json", "_summary.txt")
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write("EXTRACCIÓN DE DURACIÓN DE AUDIO MP3\n")
                f.write(f"Fecha: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(
                    f"Duración total: {report['metadata']['total_processing_time']:.1f} segundos\n"
                )
                f.write(f"Total episodios: {report['metadata']['total_episodes']}\n")
                f.write(f"Exitosos: {report['metadata']['successful']}\n")
                f.write(f"Fallidos: {report['metadata']['failed']}\n")
                f.write(f"Tasa de éxito: {report['metadata']['success_rate']:.1f}%\n")
                f.write(
                    f"Duración total extraída: {report['metadata']['total_duration_seconds']:,} segundos\n"
                )

            print(f"📋 Resumen en texto: {summary_file}")

    except Exception as e:
        print(f"❌ Error general: {e}")

        # Guardar error en log
        error_log = {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "start_time": start_time.isoformat(),
        }

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(error_log, f, indent=2, ensure_ascii=False)

    finally:
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        print(f"\n⏰ Duración total del script: {total_duration:.1f} segundos")


if __name__ == "__main__":
    main()
