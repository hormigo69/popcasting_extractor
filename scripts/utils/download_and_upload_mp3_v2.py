#!/usr/bin/env python3
"""
Script mejorado para descargar MP3 desde Supabase y subirlos al NAS Synology.
Usa la clase SynologyClient probada y genera logs detallados y procesables.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

# Añadir el directorio raíz al path para importar servicios
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.config import get_database_module
from synology.synology_client import SynologyClient


def get_podcasts_with_download_urls():
    """Obtiene los episodios con URLs de descarga desde Supabase."""
    db_module = get_database_module()

    # Conectar a la base de datos
    db = db_module.SupabaseDatabase()

    # Obtener todos los podcasts
    podcasts = db.get_all_podcasts()

    if not podcasts:
        print("❌ No se encontraron episodios")
        return pd.DataFrame()

    # Filtrar solo los que tienen download_url
    podcasts_with_mp3 = [p for p in podcasts if p.get("download_url")]

    if not podcasts_with_mp3:
        print("❌ No se encontraron episodios con URLs de descarga")
        return pd.DataFrame()

    # Crear DataFrame
    df = pd.DataFrame(
        [
            {
                "program_number": p["program_number"],
                "download_url": p["download_url"],
                "title": p.get("title", ""),
                "date": p.get("date", ""),
            }
            for p in podcasts_with_mp3
        ]
    )

    # Ordenar por número de episodio
    df = df.sort_values("program_number")

    print(f"✅ Encontrados {len(df)} episodios con URLs de descarga")

    return df


def download_mp3(url, filename):
    """Descarga un archivo MP3 desde una URL."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True
    except Exception as e:
        print(f"❌ Error descargando {url}: {e}")
        return False


def create_detailed_log(log_file, start_time):
    """Crea un log detallado y procesable."""
    log_data = {
        "metadata": {
            "start_time": start_time.isoformat(),
            "end_time": None,
            "total_episodes": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "successful_uploads": 0,
            "failed_uploads": 0,
            "total_size_downloaded": 0,
            "total_size_uploaded": 0,
            "target_folder": "/popcasting_marilyn/mp3",
        },
        "episodes": [],
    }

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    return log_data


def update_log(log_file, log_data, episode_data):
    """Actualiza el log con datos de un episodio."""
    log_data["episodes"].append(episode_data)

    # Actualizar contadores
    if episode_data["download_success"]:
        log_data["metadata"]["successful_downloads"] += 1
        log_data["metadata"]["total_size_downloaded"] += episode_data.get(
            "file_size", 0
        )
    else:
        log_data["metadata"]["failed_downloads"] += 1

    if episode_data["upload_success"]:
        log_data["metadata"]["successful_uploads"] += 1
        log_data["metadata"]["total_size_uploaded"] += episode_data.get("file_size", 0)
    else:
        log_data["metadata"]["failed_uploads"] += 1

    # Guardar log actualizado
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)


def main():
    """Función principal."""
    start_time = datetime.now()

    print("🎵 INICIANDO DESCARGA Y SUBIDA DE MP3 AL NAS SYNOLOGY")
    print("=" * 70)
    print(f"⏰ Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Crear directorio temporal para descargas
    temp_dir = Path("temp_mp3")
    temp_dir.mkdir(exist_ok=True)

    # Obtener episodios desde Supabase
    df = get_podcasts_with_download_urls()
    if df.empty:
        return

    # Configurar log detallado
    log_file = f"logs/mp3_upload_detailed_{start_time.strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("logs", exist_ok=True)

    log_data = create_detailed_log(log_file, start_time)
    log_data["metadata"]["total_episodes"] = len(df)

    # Inicializar cliente Synology usando la clase probada
    try:
        with SynologyClient() as synology:
            print("✅ Conexión al NAS establecida")

            # Verificar carpeta correcta
            print("📁 Verificando carpeta /popcasting_marilyn/mp3...")
            try:
                synology.list_files("/popcasting_marilyn/mp3")
                print("✅ Carpeta /popcasting_marilyn/mp3 existe y es accesible")
            except Exception as e:
                print(f"⚠️  Error verificando /popcasting_marilyn/mp3: {e}")

            # Procesar episodios
            for index, row in df.iterrows():
                program_number = row["program_number"]
                download_url = row["download_url"]
                title = row["title"]
                date = row["date"]

                # Formatear número de episodio con 4 dígitos
                episode_number = f"{program_number:04d}"
                local_filename = temp_dir / f"popcasting_{episode_number}.mp3"
                remote_filename = f"popcasting_{episode_number}.mp3"

                print(f"\n📥 Procesando episodio #{program_number}: {title}")
                print(f"   📅 Fecha: {date}")
                print(f"   🔗 URL: {download_url}")

                # Datos del episodio para el log
                episode_data = {
                    "episode_number": program_number,
                    "title": title,
                    "date": date,
                    "download_url": download_url,
                    "local_filename": str(local_filename),
                    "remote_filename": remote_filename,
                    "download_success": False,
                    "upload_success": False,
                    "file_size": 0,
                    "download_error": None,
                    "upload_error": None,
                    "download_time": None,
                    "upload_time": None,
                    "processing_time": None,
                }

                episode_start = datetime.now()

                # Descargar MP3
                download_start = datetime.now()
                if download_mp3(download_url, local_filename):
                    download_time = (datetime.now() - download_start).total_seconds()
                    file_size = local_filename.stat().st_size

                    episode_data.update(
                        {
                            "download_success": True,
                            "file_size": file_size,
                            "download_time": download_time,
                        }
                    )

                    print(
                        f"   ✅ Descargado: {file_size:,} bytes ({file_size/1024/1024:.1f} MB) en {download_time:.1f}s"
                    )

                    # Subir al NAS (carpeta correcta)
                    upload_start = datetime.now()
                    try:
                        if synology.upload_file(
                            str(local_filename), "/popcasting_marilyn/mp3"
                        ):
                            upload_time = (
                                datetime.now() - upload_start
                            ).total_seconds()

                            episode_data.update(
                                {"upload_success": True, "upload_time": upload_time}
                            )

                            print(
                                f"   ✅ Subido al NAS: {remote_filename} en {upload_time:.1f}s"
                            )
                        else:
                            episode_data["upload_error"] = (
                                "Error en subida (código de error del NAS)"
                            )
                            print(f"   ❌ Error subiendo al NAS: {remote_filename}")
                    except Exception as e:
                        episode_data["upload_error"] = str(e)
                        print(f"   ❌ Error subiendo al NAS: {e}")

                    # Limpiar archivo temporal
                    local_filename.unlink(missing_ok=True)
                else:
                    episode_data["download_error"] = "Error en descarga"
                    print(f"   ❌ Error descargando: {download_url}")

                # Calcular tiempo total de procesamiento
                episode_data["processing_time"] = (
                    datetime.now() - episode_start
                ).total_seconds()

                # Actualizar log
                update_log(log_file, log_data, episode_data)

                # Mostrar progreso
                processed = index + 1
                progress = (processed / len(df)) * 100
                print(f"   📊 Progreso: {processed}/{len(df)} ({progress:.1f}%)")

    except Exception as e:
        print(f"❌ Error general: {e}")
        log_data["metadata"]["error"] = str(e)

    # Finalizar log
    end_time = datetime.now()
    log_data["metadata"]["end_time"] = end_time.isoformat()
    log_data["metadata"]["total_duration"] = (end_time - start_time).total_seconds()

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    # Limpiar directorio temporal
    if temp_dir.exists():
        for file in temp_dir.glob("*.mp3"):
            file.unlink(missing_ok=True)
        temp_dir.rmdir()

    # Mostrar resumen final
    print("\n" + "=" * 70)
    print("🎵 PROCESO COMPLETADO")
    print(f"⏰ Duración total: {(end_time - start_time).total_seconds():.1f} segundos")
    print(f"📊 Episodios procesados: {log_data['metadata']['total_episodes']}")
    print(f"✅ Descargas exitosas: {log_data['metadata']['successful_downloads']}")
    print(f"❌ Descargas fallidas: {log_data['metadata']['failed_downloads']}")
    print(f"✅ Subidas exitosas: {log_data['metadata']['successful_uploads']}")
    print(f"❌ Subidas fallidas: {log_data['metadata']['failed_uploads']}")
    print(
        f"💾 Tamaño total descargado: {log_data['metadata']['total_size_downloaded']:,} bytes ({log_data['metadata']['total_size_downloaded']/1024/1024:.1f} MB)"
    )
    print(
        f"💾 Tamaño total subido: {log_data['metadata']['total_size_uploaded']:,} bytes ({log_data['metadata']['total_size_uploaded']/1024/1024:.1f} MB)"
    )
    print(f"📝 Log detallado: {log_file}")

    # Generar resumen en formato texto
    summary_file = log_file.replace(".json", "_summary.txt")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("RESUMEN DE DESCARGA Y SUBIDA DE MP3\n")
        f.write(f"Fecha: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duración: {(end_time - start_time).total_seconds():.1f} segundos\n")
        f.write(f"Total episodios: {log_data['metadata']['total_episodes']}\n")
        f.write(f"Descargas exitosas: {log_data['metadata']['successful_downloads']}\n")
        f.write(f"Descargas fallidas: {log_data['metadata']['failed_downloads']}\n")
        f.write(f"Subidas exitosas: {log_data['metadata']['successful_uploads']}\n")
        f.write(f"Subidas fallidas: {log_data['metadata']['failed_uploads']}\n")
        f.write(
            f"Tamaño descargado: {log_data['metadata']['total_size_downloaded']:,} bytes\n"
        )
        f.write(
            f"Tamaño subido: {log_data['metadata']['total_size_uploaded']:,} bytes\n"
        )

    print(f"📋 Resumen en texto: {summary_file}")


if __name__ == "__main__":
    main()
