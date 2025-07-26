#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de extracción de duración de MP3.
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


def test_duration_extraction():
    """Prueba la extracción de duración de un archivo MP3."""
    
    logger.info("🧪 INICIANDO PRUEBA DE EXTRACCIÓN DE DURACIÓN")
    
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
        
        # Crear un AudioManager mock (sin SynologyClient para esta prueba)
        class MockSynologyClient:
            def upload_file(self, file_path, folder):
                logger.info(f"Mock: Subiendo {file_path} a {folder}")
                return True
            
            def file_exists(self, remote_path):
                logger.info(f"Mock: Verificando existencia de {remote_path}")
                return False
        
        audio_manager = AudioManager(db_manager, MockSynologyClient())
        
        # 3. Probar extracción de duración con un archivo de prueba
        logger.info("Paso 3: Probando extracción de duración...")
        
        # Buscar un archivo MP3 de prueba en temp_downloads
        test_mp3_path = Path("temp_downloads")
        if test_mp3_path.exists():
            mp3_files = list(test_mp3_path.glob("*.mp3"))
            if mp3_files:
                test_file = str(mp3_files[0])
                logger.info(f"Archivo de prueba encontrado: {test_file}")
                
                # Probar extracción de duración
                duration = audio_manager._get_duration_from_mp3(test_file)
                
                if duration:
                    logger.info(f"✅ Duración extraída exitosamente: {duration:.2f} segundos")
                    
                    # Probar actualización en BD (usando un podcast de prueba)
                    test_podcast_id = 1  # ID de prueba
                    success = db_manager.update_podcast_mp3_duration(test_podcast_id, duration)
                    
                    if success:
                        logger.info(f"✅ Duración guardada en BD para podcast {test_podcast_id}")
                    else:
                        logger.warning(f"⚠️ No se pudo guardar en BD (podcast {test_podcast_id} puede no existir)")
                else:
                    logger.error("❌ No se pudo extraer la duración")
            else:
                logger.warning("⚠️ No se encontraron archivos MP3 en temp_downloads para probar")
        else:
            logger.warning("⚠️ Directorio temp_downloads no existe")
        
        # 4. Limpiar
        logger.info("Paso 4: Limpiando...")
        db_manager.close()
        
        logger.info("✅ PRUEBA COMPLETADA")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR EN LA PRUEBA: {e}")
        return False


if __name__ == "__main__":
    success = test_duration_extraction()
    exit(0 if success else 1) 