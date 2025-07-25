#!/usr/bin/env python3
"""
Clase para extraer la duración de archivos MP3 y actualizar la base de datos Supabase.
Utiliza Mutagen para extraer metadatos de audio y el cliente Synology existente.
"""

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Añadir el directorio raíz al path para importar servicios
sys.path.append(str(Path(__file__).parent.parent))

# Mutagen ya no se usa, pero lo mantenemos por compatibilidad
# from mutagen import File
# from mutagen.mp3 import MP3
import subprocess
import json

# Verificar si ffprobe está disponible
try:
    subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
    FFPROBE_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    FFPROBE_AVAILABLE = False
from services.config import get_database_module
from synology.synology_client import SynologyClient


class AudioDurationExtractor:
    """Clase para extraer duración de archivos MP3 y actualizar Supabase."""
    
    def __init__(self):
        """Inicializa el extractor de duración."""
        self.db_module = get_database_module()
        self.db = self.db_module.SupabaseDatabase()
        self.synology = None
        self.temp_dir = None
        
    def __enter__(self):
        """Context manager entry."""
        # Conectar a Synology
        self.synology = SynologyClient()
        if not self.synology.login():
            raise Exception("No se pudo conectar al NAS Synology")
        
        # Crear directorio temporal
        self.temp_dir = Path(tempfile.mkdtemp(prefix="audio_duration_"))
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Cerrar conexión Synology
        if self.synology:
            self.synology.logout()
        
        # Limpiar directorio temporal
        if self.temp_dir and self.temp_dir.exists():
            for file in self.temp_dir.glob("*"):
                file.unlink(missing_ok=True)
            self.temp_dir.rmdir()
    
    def get_podcasts_without_duration(self) -> List[Dict]:
        """
        Obtiene episodios que no tienen duración en la base de datos.
        
        Returns:
            List[Dict]: Lista de episodios sin duración
        """
        try:
            # Obtener todos los podcasts
            podcasts = self.db.get_all_podcasts()
            
            # Filtrar los que no tienen duración
            podcasts_without_duration = [
                p for p in podcasts 
                if p.get('duration') is None or p.get('duration') == 0
            ]
            
            print(f"📊 Encontrados {len(podcasts_without_duration)} episodios sin duración")
            return podcasts_without_duration
            
        except Exception as e:
            print(f"❌ Error obteniendo episodios sin duración: {e}")
            return []
    
    def get_podcast_by_program_number(self, program_number: int) -> Optional[Dict]:
        """
        Obtiene un episodio por su número de programa.
        
        Args:
            program_number: Número del episodio
            
        Returns:
            Optional[Dict]: Datos del episodio o None si no se encuentra
        """
        try:
            podcasts = self.db.get_all_podcasts()
            for podcast in podcasts:
                if podcast.get('program_number') == program_number:
                    return podcast
            return None
            
        except Exception as e:
            print(f"❌ Error obteniendo episodio #{program_number}: {e}")
            return None
    
    def download_mp3_from_synology(self, program_number: int) -> Optional[Path]:
        """
        Descarga un MP3 desde Synology NAS.
        
        Args:
            program_number: Número del episodio
            
        Returns:
            Optional[Path]: Ruta del archivo descargado o None si hay error
        """
        try:
            # Formatear nombre del archivo
            episode_number = f"{program_number:04d}"
            remote_filename = f"popcasting_{episode_number}.mp3"
            local_filename = self.temp_dir / remote_filename
            
            print(f"📥 Descargando {remote_filename} desde Synology...")
            
            # Descargar archivo
            remote_path = f"/popcasting_marilyn/mp3/{remote_filename}"
            if self.synology.download_file(remote_path, str(self.temp_dir)):
                if local_filename.exists():
                    file_size = local_filename.stat().st_size
                    print(f"✅ Descargado: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
                    return local_filename
                else:
                    print(f"❌ Archivo no encontrado localmente: {local_filename}")
                    return None
            else:
                print(f"❌ Error descargando {remote_filename}")
                return None
                
        except Exception as e:
            print(f"❌ Error descargando MP3 del episodio #{program_number}: {e}")
            return None
    
    def extract_duration_from_mp3(self, mp3_path: Path) -> Optional[int]:
        """
        Extrae la duración de un archivo MP3 usando ffprobe.
        
        Args:
            mp3_path: Ruta al archivo MP3
            
        Returns:
            Optional[int]: Duración en segundos o None si hay error
        """
        try:
            if not FFPROBE_AVAILABLE:
                print("❌ ffprobe no está disponible en el sistema")
                return None
            
            print("🔍 Extrayendo duración con ffprobe...")
            
            # Usar ffprobe para obtener información del archivo
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                str(mp3_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            if 'format' in data and 'duration' in data['format']:
                duration_seconds = int(float(data['format']['duration']))
                duration_minutes = duration_seconds // 60
                duration_remaining = duration_seconds % 60
                print(f"✅ Duración extraída: {duration_minutes}:{duration_remaining:02d} ({duration_seconds} segundos)")
                return duration_seconds
            else:
                print(f"❌ ffprobe no pudo extraer duración del archivo: {mp3_path}")
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error ejecutando ffprobe: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando salida de ffprobe: {e}")
            return None
        except Exception as e:
            print(f"❌ Error extrayendo duración de {mp3_path}: {e}")
            return None
    
    def update_podcast_duration(self, podcast_id: int, duration: int) -> bool:
        """
        Actualiza la duración de un episodio en Supabase.
        
        Args:
            podcast_id: ID del episodio
            duration: Duración en segundos
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            # Actualizar en la base de datos
            self.db.client.table("podcasts").update({"duration": duration}).eq("id", podcast_id).execute()
            print(f"✅ Duración actualizada en Supabase: {duration} segundos")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando duración en Supabase: {e}")
            return False
    
    def process_single_episode(self, program_number: int) -> Dict:
        """
        Procesa un episodio individual: descarga, extrae duración y actualiza.
        
        Args:
            program_number: Número del episodio
            
        Returns:
            Dict: Resultado del procesamiento
        """
        result = {
            "program_number": program_number,
            "success": False,
            "duration": None,
            "error": None,
            "processing_time": None
        }
        
        start_time = datetime.now()
        
        try:
            # Obtener datos del episodio
            podcast = self.get_podcast_by_program_number(program_number)
            if not podcast:
                result["error"] = f"Episodio #{program_number} no encontrado en Supabase"
                return result
            
            # Descargar MP3
            mp3_path = self.download_mp3_from_synology(program_number)
            if not mp3_path:
                result["error"] = f"No se pudo descargar MP3 del episodio #{program_number}"
                return result
            
            # Extraer duración
            duration = self.extract_duration_from_mp3(mp3_path)
            if not duration:
                result["error"] = f"No se pudo extraer duración del MP3 del episodio #{program_number}"
                return result
            
            # Actualizar en Supabase
            if self.update_podcast_duration(podcast["id"], duration):
                result["success"] = True
                result["duration"] = duration
            else:
                result["error"] = f"No se pudo actualizar duración en Supabase para episodio #{program_number}"
            
            # Limpiar archivo temporal
            mp3_path.unlink(missing_ok=True)
            
        except Exception as e:
            result["error"] = str(e)
        
        finally:
            result["processing_time"] = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def process_multiple_episodes(self, program_numbers: List[int]) -> List[Dict]:
        """
        Procesa múltiples episodios.
        
        Args:
            program_numbers: Lista de números de episodio
            
        Returns:
            List[Dict]: Resultados del procesamiento
        """
        results = []
        
        for i, program_number in enumerate(program_numbers, 1):
            print(f"\n📋 Procesando episodio {i}/{len(program_numbers)}: #{program_number}")
            
            result = self.process_single_episode(program_number)
            results.append(result)
            
            # Mostrar progreso
            progress = (i / len(program_numbers)) * 100
            print(f"📊 Progreso: {i}/{len(program_numbers)} ({progress:.1f}%)")
        
        return results
    
    def process_all_episodes_without_duration(self) -> List[Dict]:
        """
        Procesa todos los episodios que no tienen duración.
        
        Returns:
            List[Dict]: Resultados del procesamiento
        """
        # Obtener episodios sin duración
        podcasts = self.get_podcasts_without_duration()
        
        if not podcasts:
            print("✅ Todos los episodios ya tienen duración")
            return []
        
        # Extraer números de programa
        program_numbers = [p["program_number"] for p in podcasts]
        
        print(f"🎵 Procesando {len(program_numbers)} episodios sin duración...")
        
        return self.process_multiple_episodes(program_numbers)
    
    def generate_report(self, results: List[Dict]) -> Dict:
        """
        Genera un reporte de los resultados del procesamiento.
        
        Args:
            results: Lista de resultados del procesamiento
            
        Returns:
            Dict: Reporte completo
        """
        total_episodes = len(results)
        successful = sum(1 for r in results if r["success"])
        failed = total_episodes - successful
        
        total_duration = sum(r.get("duration", 0) for r in results if r["success"])
        total_processing_time = sum(r.get("processing_time", 0) for r in results)
        
        report = {
            "metadata": {
                "total_episodes": total_episodes,
                "successful": successful,
                "failed": failed,
                "success_rate": (successful / total_episodes * 100) if total_episodes > 0 else 0,
                "total_duration_seconds": total_duration,
                "total_processing_time": total_processing_time,
                "timestamp": datetime.now().isoformat()
            },
            "results": results
        }
        
        return report 