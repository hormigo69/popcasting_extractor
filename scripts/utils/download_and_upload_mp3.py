#!/usr/bin/env python3
"""
Script simple para descargar MP3 desde Supabase y subirlos al NAS Synology.
"""

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
            {"program_number": p["program_number"], "download_url": p["download_url"]}
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


def main():
    """Función principal."""
    print("🎵 Iniciando descarga y subida de MP3 al NAS")
    print("=" * 50)

    # Crear directorio temporal para descargas
    temp_dir = Path("temp_mp3")
    temp_dir.mkdir(exist_ok=True)

    # Obtener episodios desde Supabase
    df = get_podcasts_with_download_urls()
    if df.empty:
        return

    # Inicializar cliente Synology
    try:
        synology = SynologyClient()
        if not synology.login():
            print("❌ No se pudo conectar al NAS")
            return
    except Exception as e:
        print(f"❌ Error inicializando cliente Synology: {e}")
        return

    # Crear carpeta mp3 en el NAS si no existe
    synology.create_folder("/mp3")

    # Log de resultados
    log_file = f"logs/mp3_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    os.makedirs("logs", exist_ok=True)

    successful_uploads = 0
    failed_uploads = 0

    with open(log_file, "w", encoding="utf-8") as log:
        log.write(f"Log de subida de MP3 - {datetime.now()}\n")
        log.write("=" * 50 + "\n\n")

        for _index, row in df.iterrows():
            program_number = row["program_number"]
            download_url = row["download_url"]

            # Formatear número de episodio con 4 dígitos
            episode_number = f"{program_number:04d}"
            local_filename = temp_dir / f"popcasting_{episode_number}.mp3"
            remote_filename = f"popcasting_{episode_number}.mp3"

            print(f"📥 Procesando episodio #{program_number}...")

            # Descargar MP3
            if download_mp3(download_url, local_filename):
                print(f"  ✅ Descargado: {local_filename}")

                # Subir al NAS
                try:
                    if synology.upload_file(str(local_filename), "/mp3"):
                        print(f"  ✅ Subido al NAS: {remote_filename}")
                        successful_uploads += 1
                        log.write(
                            f"✅ ÉXITO: Episodio #{program_number} - {remote_filename}\n"
                        )
                    else:
                        print(f"  ❌ Error subiendo al NAS: {remote_filename}")
                        failed_uploads += 1
                        log.write(
                            f"❌ ERROR SUBIDA: Episodio #{program_number} - {remote_filename}\n"
                        )
                except Exception as e:
                    print(f"  ❌ Error subiendo al NAS: {e}")
                    failed_uploads += 1
                    log.write(f"❌ ERROR SUBIDA: Episodio #{program_number} - {e}\n")

                # Limpiar archivo temporal
                local_filename.unlink(missing_ok=True)
            else:
                print(f"  ❌ Error descargando: {download_url}")
                failed_uploads += 1
                log.write(
                    f"❌ ERROR DESCARGA: Episodio #{program_number} - {download_url}\n"
                )

            print()

        # Resumen final
        log.write("\nRESUMEN:\n")
        log.write(f"✅ Subidas exitosas: {successful_uploads}\n")
        log.write(f"❌ Fallos: {failed_uploads}\n")
        log.write(f"📊 Total procesados: {len(df)}\n")

    # Cerrar sesión del NAS
    synology.logout()

    # Limpiar directorio temporal
    if temp_dir.exists():
        for file in temp_dir.glob("*.mp3"):
            file.unlink(missing_ok=True)
        temp_dir.rmdir()

    # Mostrar resumen
    print("=" * 50)
    print("🎵 PROCESO COMPLETADO")
    print(f"✅ Subidas exitosas: {successful_uploads}")
    print(f"❌ Fallos: {failed_uploads}")
    print(f"📊 Total procesados: {len(df)}")
    print(f"📝 Log guardado en: {log_file}")


if __name__ == "__main__":
    main()
