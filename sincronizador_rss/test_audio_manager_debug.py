#!/usr/bin/env python3
"""
Script de prueba para debuggear el AudioManager con el episodio 485.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.components.config_manager import ConfigManager
from src.components.database_manager import DatabaseManager
from src.components.synology_client import SynologyClient
from src.components.audio_manager import AudioManager
from src.utils.logger import setup_logger

def main():
    # Configurar logger
    logger = setup_logger()
    logger.info("🔍 Iniciando prueba de AudioManager para episodio 485")
    
    try:
        # 1. Inicializar componentes
        logger.info("📋 Inicializando componentes...")
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # 2. Inicializar Synology
        logger.info("🔗 Conectando a Synology...")
        synology_credentials = config_manager.get_synology_credentials()
        synology_client = SynologyClient(
            host=synology_credentials["ip"],
            port=synology_credentials["port"],
            username=synology_credentials["user"],
            password=synology_credentials["password"]
        )
        
        if not synology_client.login():
            logger.error("❌ No se pudo conectar al NAS Synology")
            return
        
        logger.info("✅ Conectado a Synology")
        
        # 3. Inicializar AudioManager
        logger.info("🎵 Inicializando AudioManager...")
        audio_manager = AudioManager(db_manager, synology_client)
        
        # 4. Obtener información del episodio 485
        logger.info("📊 Obteniendo información del episodio 485...")
        podcast = db_manager.get_podcast_by_id(549)  # ID del episodio 485
        
        if not podcast:
            logger.error("❌ No se encontró el episodio 485 en la BD")
            return
        
        logger.info(f"📻 Episodio encontrado: {podcast.get('title', 'Sin título')}")
        logger.info(f"🔗 URL de descarga: {podcast.get('download_url', 'No disponible')}")
        logger.info(f"📅 Número de programa: {podcast.get('program_number', 'No disponible')}")
        
        # 5. Verificar si el archivo ya existe en el NAS
        program_number = podcast.get('program_number')
        if program_number:
            nas_filename = f"popcasting_{program_number:04d}.mp3"
            nas_folder = "/popcasting_marilyn/mp3"
            nas_path = f"{nas_folder}/{nas_filename}"
            
            logger.info(f"🔍 Verificando si existe: {nas_path}")
            exists = audio_manager._file_exists_in_nas(nas_filename, nas_folder)
            logger.info(f"📁 Archivo existe en NAS: {exists}")
        
        # 6. Ejecutar AudioManager
        logger.info("🚀 Ejecutando AudioManager.archive_podcast_audio(549)...")
        result = audio_manager.archive_podcast_audio(549)
        
        logger.info(f"✅ Resultado: {result}")
        
    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 