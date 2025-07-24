#!/usr/bin/env python3
"""
Script de prueba mejorado para descargar y subir 3 MP3 al NAS Synology.
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz al path para importar servicios
sys.path.append(os.path.dirname(__file__))

from services.config import get_database_module
from synology_client import SynologyClient


def get_first_3_podcasts_with_download_urls():
    """Obtiene los primeros 3 episodios con URLs de descarga desde Supabase."""
    db_module = get_database_module()
    
    # Conectar a la base de datos
    db = db_module.SupabaseDatabase()
    
    # Obtener todos los podcasts
    podcasts = db.get_all_podcasts()
    
    if not podcasts:
        print("❌ No se encontraron episodios")
        return pd.DataFrame()
    
    # Filtrar solo los que tienen download_url y tomar los primeros 3
    podcasts_with_mp3 = [p for p in podcasts if p.get('download_url')][:3]
    
    if not podcasts_with_mp3:
        print("❌ No se encontraron episodios con URLs de descarga")
        return pd.DataFrame()
    
    # Crear DataFrame
    df = pd.DataFrame([
        {
            'program_number': p['program_number'],
            'download_url': p['download_url']
        }
        for p in podcasts_with_mp3
    ])
    
    # Ordenar por número de episodio
    df = df.sort_values('program_number')
    
    print(f"✅ Encontrados {len(df)} episodios para prueba")
    
    return df


def download_mp3(url, filename):
    """Descarga un archivo MP3 desde una URL."""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"❌ Error descargando {url}: {e}")
        return False


def ensure_folder_exists(synology, folder_path):
    """Asegura que la carpeta existe en el NAS."""
    try:
        # Intentar listar la carpeta para ver si existe
        files = synology.list_files(folder_path)
        if files is not None:
            print(f"✅ Carpeta {folder_path} ya existe")
            return True
    except:
        pass
    
    # Si no existe, intentar crearla
    try:
        if synology.create_folder(folder_path):
            return True
        else:
            print(f"⚠️  No se pudo crear la carpeta {folder_path}, pero continuamos...")
            return True  # Continuamos de todas formas
    except Exception as e:
        print(f"⚠️  Error verificando/creando carpeta: {e}")
        return True  # Continuamos de todas formas


def main():
    """Función principal."""
    print("🎵 PRUEBA MEJORADA: Descarga y subida de 3 MP3 al NAS")
    print("=" * 60)
    
    # Crear directorio temporal para descargas
    temp_dir = Path("temp_mp3_test")
    temp_dir.mkdir(exist_ok=True)
    
    # Obtener 3 episodios desde Supabase
    df = get_first_3_podcasts_with_download_urls()
    if df.empty:
        return
    
    # Mostrar episodios que se van a procesar
    print("\n📋 Episodios a procesar:")
    for _, row in df.iterrows():
        print(f"  Episodio #{row['program_number']}: {row['download_url']}")
    print()
    
    # Inicializar cliente Synology
    try:
        synology = SynologyClient()
        if not synology.login():
            print("❌ No se pudo conectar al NAS")
            return
    except Exception as e:
        print(f"❌ Error inicializando cliente Synology: {e}")
        return
    
    # Verificar/crear carpeta mp3 en el NAS
    ensure_folder_exists(synology, "/mp3")
    
    # Mostrar contenido actual de la carpeta
    print("\n📁 Contenido actual de /mp3:")
    synology.list_files("/mp3")
    print()
    
    # Log de resultados
    log_file = f"logs/mp3_test_3_files_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    os.makedirs("logs", exist_ok=True)
    
    successful_uploads = 0
    failed_uploads = 0
    
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"Log de prueba mejorada - 3 MP3 - {datetime.now()}\n")
        log.write("=" * 60 + "\n\n")
        
        for index, row in df.iterrows():
            program_number = row['program_number']
            download_url = row['download_url']
            
            # Formatear número de episodio con 4 dígitos
            episode_number = f"{program_number:04d}"
            local_filename = temp_dir / f"popcasting_{episode_number}.mp3"
            remote_filename = f"popcasting_{episode_number}.mp3"
            
            print(f"📥 Procesando episodio #{program_number}...")
            
            # Descargar MP3
            if download_mp3(download_url, local_filename):
                print(f"  ✅ Descargado: {local_filename}")
                
                # Verificar tamaño del archivo
                file_size = local_filename.stat().st_size
                print(f"  📊 Tamaño: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
                
                # Subir al NAS
                try:
                    if synology.upload_file(str(local_filename), "/mp3"):
                        print(f"  ✅ Subido al NAS: {remote_filename}")
                        successful_uploads += 1
                        log.write(f"✅ ÉXITO: Episodio #{program_number} - {remote_filename} ({file_size:,} bytes)\n")
                    else:
                        print(f"  ❌ Error subiendo al NAS: {remote_filename}")
                        failed_uploads += 1
                        log.write(f"❌ ERROR SUBIDA: Episodio #{program_number} - {remote_filename}\n")
                except Exception as e:
                    print(f"  ❌ Error subiendo al NAS: {e}")
                    failed_uploads += 1
                    log.write(f"❌ ERROR SUBIDA: Episodio #{program_number} - {e}\n")
                
                # Limpiar archivo temporal
                local_filename.unlink(missing_ok=True)
            else:
                print(f"  ❌ Error descargando: {download_url}")
                failed_uploads += 1
                log.write(f"❌ ERROR DESCARGA: Episodio #{program_number} - {download_url}\n")
            
            print()
        
        # Resumen final
        log.write(f"\nRESUMEN PRUEBA:\n")
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
    print("=" * 60)
    print(f"🎵 PRUEBA COMPLETADA")
    print(f"✅ Subidas exitosas: {successful_uploads}")
    print(f"❌ Fallos: {failed_uploads}")
    print(f"📊 Total procesados: {len(df)}")
    print(f"📝 Log guardado en: {log_file}")
    
    if successful_uploads == len(df):
        print("🎉 ¡PRUEBA EXITOSA! Todos los archivos se subieron correctamente.")
    elif successful_uploads > 0:
        print(f"⚠️  Parcialmente exitoso: {successful_uploads}/{len(df)} archivos subidos.")
    else:
        print("❌ Todos los archivos fallaron. Revisa la configuración del NAS.")


if __name__ == "__main__":
    main() 