#!/usr/bin/env python3
"""
Script de prueba completo para el AudioManager con funcionalidad de duración.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

from components.audio_manager import AudioManager
from components.database_manager import DatabaseManager
from components.config_manager import ConfigManager
from utils.logger import logger


def test_audio_manager_complete():
    """Prueba completa del AudioManager con la nueva funcionalidad de duración."""
    
    logger.info("🧪 INICIANDO PRUEBA COMPLETA DEL AUDIOMANAGER")
    
    try:
        # 1. Cargar configuración
        logger.info("Paso 1: Cargando configuración...")
        cfg_manager = ConfigManager()
        supabase_credentials = cfg_manager.get_supabase_credentials()
        
        # 2. Crear instancias
        logger.info("Paso 2: Creando instancias...")
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # Crear un SynologyClient mock para pruebas
        class MockSynologyClient:
            def upload_file(self, file_path, folder):
                logger.info(f"Mock: Subiendo {file_path} a {folder}")
                return True
            
            def file_exists(self, remote_path):
                logger.info(f"Mock: Verificando existencia de {remote_path}")
                return False
        
        audio_manager = AudioManager(db_manager, MockSynologyClient())
        
        # 3. Obtener un podcast real de la base de datos para probar
        logger.info("Paso 3: Obteniendo podcast de prueba...")
        podcasts = db_manager.get_all_podcasts()
        
        if not podcasts:
            logger.warning("⚠️ No hay podcasts en la BD para probar")
            return False
        
        # Usar el primer podcast que tenga download_url
        test_podcast = None
        for podcast in podcasts[:5]:  # Revisar solo los primeros 5
            if podcast.get('download_url') and podcast.get('program_number'):
                test_podcast = podcast
                break
        
        if not test_podcast:
            logger.warning("⚠️ No se encontró un podcast con download_url para probar")
            return False
        
        podcast_id = test_podcast['id']
        program_number = test_podcast['program_number']
        download_url = test_podcast['download_url']
        
        logger.info(f"📻 Podcast de prueba: ID {podcast_id}, Programa #{program_number}")
        logger.info(f"🔗 URL: {download_url}")
        
        # 4. Probar la funcionalidad completa
        logger.info("Paso 4: Probando funcionalidad completa...")
        
        # Verificar si ya existe en NAS (mock)
        exists_in_nas = audio_manager.check_podcast_in_nas(program_number)
        logger.info(f"📁 Existe en NAS: {exists_in_nas}")
        
        # Probar extracción de duración con archivo de prueba
        test_mp3_path = Path("temp_downloads/test_audio.mp3")
        if test_mp3_path.exists():
            duration = audio_manager._get_duration_from_mp3(str(test_mp3_path))
            if duration:
                logger.info(f"✅ Duración extraída: {duration:.2f} segundos")
                
                # Probar actualización en BD
                success = db_manager.update_podcast_mp3_duration(podcast_id, duration)
                if success:
                    logger.info(f"✅ Duración guardada en BD para podcast {podcast_id}")
                else:
                    logger.warning(f"⚠️ No se pudo guardar duración en BD")
            else:
                logger.error("❌ No se pudo extraer duración")
        
        # 5. Probar generación de rutas NAS
        logger.info("Paso 5: Probando generación de rutas...")
        nas_path = audio_manager.get_nas_path_for_podcast(program_number)
        logger.info(f"📁 Ruta NAS generada: {nas_path}")
        
        # 6. Limpiar
        logger.info("Paso 6: Limpiando...")
        db_manager.close()
        
        logger.info("✅ PRUEBA COMPLETA FINALIZADA")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR EN LA PRUEBA: {e}")
        return False


if __name__ == "__main__":
    success = test_audio_manager_complete()
    exit(0 if success else 1) 