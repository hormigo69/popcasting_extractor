"""
Componente para gestionar la descarga de archivos MP3 de podcasts y su subida al NAS.
"""

import os
import requests
import shutil
import logging
import json
import subprocess
from pathlib import Path
from typing import Optional


class MP3Manager:
    """
    Gestor de archivos MP3 para descargar archivos de podcasts y subirlos al NAS.
    
    Responsabilidades:
    - Descargar archivos MP3 desde URLs de podcasts
    - Subir archivos al NAS Synology
    - Actualizar la base de datos con las rutas del NAS
    - Limpiar archivos temporales
    """
    
    def __init__(self, database_manager, synology_client):
        """
        Inicializa el gestor de MP3.
        
        Args:
            database_manager: Instancia de DatabaseManager para operaciones de BD
            synology_client: Instancia de SynologyClient para operaciones del NAS
        """
        self.db_manager = database_manager
        self.synology_client = synology_client
        self.logger = logging.getLogger(__name__)
        
        # Definir carpeta temporal para descargas
        self.temp_downloads = Path("temp_downloads")
        
        # Crear carpeta temporal si no existe
        self.temp_downloads.mkdir(exist_ok=True)
        
        self.logger.info(f"MP3Manager inicializado. Carpeta temporal: {self.temp_downloads}")
    
    def archive_podcast_audio(self, podcast_id: int) -> bool:
        """
        Método principal para archivar el audio de un podcast.
        
        Args:
            podcast_id: ID del podcast a procesar
            
        Returns:
            bool: True si el proceso fue exitoso, False en caso contrario
        """
        try:
            self.logger.info(f"🔄 Iniciando archivo de audio para podcast ID: {podcast_id}")
            
            # 1. Obtener información del podcast
            podcast = self.db_manager.get_podcast_by_id(podcast_id)
            if not podcast:
                self.logger.error(f"❌ Podcast con ID {podcast_id} no encontrado")
                return False
            
            # Verificar que tiene URL de descarga
            download_url = podcast.get('download_url')
            if not download_url:
                self.logger.error(f"❌ Podcast {podcast_id} no tiene URL de descarga")
                return False
            
            # Verificar que tiene número de programa
            program_number = podcast.get('program_number')
            if not program_number:
                self.logger.error(f"❌ Podcast {podcast_id} no tiene número de programa")
                return False
            
            # 2. Verificar si el archivo ya existe en el NAS
            nas_filename = f"popcasting_{program_number:04d}.mp3"
            nas_folder = "/popcasting_marilyn/mp3"
            nas_path = f"{nas_folder}/{nas_filename}"
            
            if self._file_exists_in_nas(nas_filename, nas_folder):
                self.logger.info(f"ℹ️ Archivo ya existe en NAS: {nas_path}")
                return True
            
            self.logger.info(f"📥 Descargando desde: {download_url}")
            
            # 3. Descargar archivo MP3
            local_file_path = self._download_file(download_url, self.temp_downloads)
            if not local_file_path:
                self.logger.error(f"❌ Error al descargar archivo para podcast {podcast_id}")
                return False
            
            self.logger.info(f"✅ Archivo descargado: {local_file_path}")
            
            # 4. Extraer duración exacta del archivo MP3
            mp3_duration = self._get_duration_from_mp3(str(local_file_path))
            
            # Aplicar lógica de prioridad para la duración
            final_duration = None
            if mp3_duration:
                final_duration = mp3_duration
                self.logger.info(f"⏱️ Usando duración extraída del MP3: {final_duration:.2f}s")
            else:
                # Usar duración del RSS como respaldo
                rss_duration = podcast.get('duration')
                if rss_duration:
                    final_duration = rss_duration
                    self.logger.info(f"⏱️ Usando duración del RSS como respaldo: {final_duration}s")
                else:
                    self.logger.warning(f"⚠️ No se pudo obtener duración del podcast {podcast_id}")
            
            # Guardar duración en la base de datos si se obtuvo
            if final_duration:
                # Redondear a segundos enteros para compatibilidad con BD
                duration_seconds = int(round(final_duration))
                duration_saved = self.db_manager.update_podcast_mp3_duration(podcast_id, duration_seconds)
                if duration_saved:
                    self.logger.info(f"💾 Duración guardada en BD: {duration_seconds}s (original: {final_duration:.2f}s)")
                else:
                    self.logger.warning(f"⚠️ No se pudo guardar la duración en la BD")
            
            self.logger.info(f"📁 Subiendo como: {nas_filename}")
            
            # 5. Renombrar archivo local al formato correcto antes de subir
            renamed_file_path = local_file_path.parent / nas_filename
            try:
                local_file_path.rename(renamed_file_path)
                self.logger.info(f"📝 Archivo renombrado: {renamed_file_path}")
            except Exception as e:
                self.logger.error(f"❌ Error al renombrar archivo: {e}")
                self._cleanup_temp_file(local_file_path)
                return False
            
            # 6. Subir archivo al NAS con el nombre correcto
            upload_success = self.synology_client.upload_file(renamed_file_path, nas_folder)
            
            if not upload_success:
                self.logger.error(f"❌ Error al subir archivo al NAS para podcast {podcast_id}")
                # Limpiar archivo temporal
                self._cleanup_temp_file(renamed_file_path)
                return False
            
            self.logger.info(f"✅ Archivo subido al NAS: {nas_path}")
            
            # 7. Limpiar archivo temporal
            self._cleanup_temp_file(renamed_file_path)
            
            self.logger.info(f"🎉 Proceso completado exitosamente para podcast {podcast_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error inesperado en archive_podcast_audio: {e}")
            return False
    
    def _download_file(self, url: str, destination_folder: Path) -> Optional[Path]:
        """
        Descarga un archivo desde una URL a una carpeta de destino.
        
        Args:
            url: URL del archivo a descargar
            destination_folder: Carpeta de destino
            
        Returns:
            Path: Ruta completa al archivo descargado o None si falla
        """
        try:
            self.logger.info(f"📥 Iniciando descarga desde: {url}")
            
            # Crear carpeta de destino si no existe
            destination_folder.mkdir(parents=True, exist_ok=True)
            
            # Realizar la descarga
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            # Extraer nombre del archivo de la URL
            filename = url.split('/')[-1]
            if not filename or '?' in filename:
                # Si no se puede extraer el nombre, usar un nombre genérico
                filename = f"podcast_audio_{hash(url) % 10000}.mp3"
            
            file_path = destination_folder / filename
            
            # Guardar archivo
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verificar que el archivo se descargó correctamente
            if file_path.exists() and file_path.stat().st_size > 0:
                self.logger.info(f"✅ Archivo descargado exitosamente: {file_path}")
                return file_path
            else:
                self.logger.error(f"❌ Archivo descargado está vacío o no existe: {file_path}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Error de red durante la descarga: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error inesperado durante la descarga: {e}")
            return None
    
    def _file_exists_in_nas(self, filename: str, folder: str) -> bool:
        """
        Verifica si un archivo ya existe en el NAS usando file_exists (más eficiente).
        Args:
            filename: Nombre del archivo a verificar
            folder: Carpeta donde buscar
        Returns:
            bool: True si el archivo existe, False en caso contrario
        """
        try:
            remote_path = os.path.join(folder, filename)
            return self.synology_client.file_exists(remote_path)
        except Exception as e:
            self.logger.warning(f"⚠️ Error al verificar existencia de archivo en NAS: {e}")
            return False
    
    def _get_duration_from_mp3(self, file_path: str) -> float | None:
        """
        Extrae la duración exacta de un archivo MP3 usando ffprobe.
        
        Args:
            file_path: Ruta al archivo MP3 local
            
        Returns:
            float: Duración en segundos o None si hay error
        """
        try:
            self.logger.debug(f"🔍 Extrayendo duración de: {file_path}")
            
            # Usar ffprobe para obtener información del archivo
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.logger.error(f"❌ Error ejecutando ffprobe: {result.stderr}")
                return None
            
            # Parsear la salida JSON
            probe_data = json.loads(result.stdout)
            
            # Buscar la duración en el formato o en el primer stream de audio
            duration = None
            
            # Primero intentar obtener la duración del formato
            if 'format' in probe_data and 'duration' in probe_data['format']:
                duration = float(probe_data['format']['duration'])
            # Si no está en el formato, buscar en los streams de audio
            elif 'streams' in probe_data:
                for stream in probe_data['streams']:
                    if stream.get('codec_type') == 'audio' and 'duration' in stream:
                        duration = float(stream['duration'])
                        break
            
            if duration:
                self.logger.info(f"✅ Duración extraída: {duration:.2f} segundos")
                return duration
            else:
                self.logger.warning(f"⚠️ No se pudo obtener la duración de: {file_path}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ Timeout al ejecutar ffprobe en: {file_path}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Error parseando salida JSON de ffprobe: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error al extraer duración de {file_path}: {e}")
            return None
    
    def _cleanup_temp_file(self, file_path: Path) -> None:
        """
        Elimina un archivo temporal.
        
        Args:
            file_path: Ruta del archivo a eliminar
        """
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.debug(f"🗑️ Archivo temporal eliminado: {file_path}")
        except Exception as e:
            self.logger.warning(f"⚠️ Error al eliminar archivo temporal {file_path}: {e}")
    
    def cleanup_temp_folder(self) -> None:
        """
        Limpia toda la carpeta temporal de descargas.
        """
        try:
            if self.temp_downloads.exists():
                shutil.rmtree(self.temp_downloads)
                self.logger.info(f"🗑️ Carpeta temporal eliminada: {self.temp_downloads}")
        except Exception as e:
            self.logger.warning(f"⚠️ Error al eliminar carpeta temporal: {e}")
    
    def get_nas_path_for_podcast(self, program_number: int) -> str:
        """
        Genera la ruta del NAS para un podcast basado en su número de programa.
        
        Args:
            program_number: Número del programa
            
        Returns:
            str: Ruta completa del archivo en el NAS
        """
        nas_filename = f"popcasting_{program_number:04d}.mp3"
        return f"/popcasting_marilyn/mp3/{nas_filename}"
    
    def check_podcast_in_nas(self, program_number: int) -> bool:
        """
        Verifica si un podcast existe en el NAS basado en su número de programa.
        
        Args:
            program_number: Número del programa
            
        Returns:
            bool: True si el archivo existe en el NAS
        """
        nas_filename = f"popcasting_{program_number:04d}.mp3"
        return self._file_exists_in_nas(nas_filename, "/popcasting_marilyn/mp3")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup_temp_folder() 