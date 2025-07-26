"""
Prueba del SongProcessor para verificar su funcionamiento.
"""

import sys
import os
import json
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from src.components.song_processor import SongProcessor
from src.components.database_manager import DatabaseManager
from src.components.config_manager import ConfigManager
from src.utils.logger import logger


def test_song_processor():
    """
    Prueba completa del SongProcessor.
    """
    try:
        logger.info("=== PRUEBA DEL SONGPROCESSOR ===")
        
        # 1. Configurar conexión
        logger.info("1. Configurando conexión...")
        cfg_manager = ConfigManager()
        supabase_credentials = cfg_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # 2. Crear SongProcessor
        logger.info("2. Creando SongProcessor...")
        song_processor = SongProcessor(db_manager)
        
        # 3. Probar parseo de playlist JSON
        logger.info("3. Probando parseo de playlist JSON...")
        test_playlist_json = json.dumps([
            {"position": 1, "artist": "the beatles", "title": "rain"},
            {"position": 2, "artist": "pink floyd", "title": "time"},
            {"position": 3, "artist": "led zeppelin", "title": "stairway to heaven"},
            {"position": 4, "artist": "queen", "title": "bohemian rhapsody"},
            {"position": 5, "artist": "the rolling stones", "title": "paint it black"}
        ], ensure_ascii=False)
        
        parsed_songs = song_processor._parse_json_playlist(test_playlist_json)
        logger.info(f"   ✅ Canciones parseadas: {len(parsed_songs)}")
        
        for song in parsed_songs:
            logger.info(f"   - {song['position']}: {song['artist']} · {song['title']}")
        
        # 4. Probar validación
        logger.info("4. Probando validación de canciones...")
        test_song = {"artist": "The Beatles", "title": "Rain"}
        is_valid = song_processor._validate_song_data(test_song)
        logger.info(f"   ✅ Canción válida: {is_valid}")
        
        # 5. Probar información de playlist
        logger.info("5. Probando información de playlist...")
        playlist_info = song_processor.get_playlist_info(web_playlist=test_playlist_json)
        logger.info(f"   ✅ Información: {playlist_info}")
        
        # 6. Probar procesamiento completo (sin guardar en BD)
        logger.info("6. Probando procesamiento completo...")
        
        # Simular datos de podcast
        podcast_id = 999  # ID de prueba
        web_playlist_json = json.dumps([
            {"position": 1, "artist": "The Beatles", "title": "Rain"},
            {"position": 2, "artist": "Pink Floyd", "title": "Time"}
        ], ensure_ascii=False)
        
        # Probar con playlist web
        stored_count = song_processor.process_and_store_songs(
            podcast_id=podcast_id,
            web_playlist=web_playlist_json,
            rss_playlist=test_playlist_json
        )
        
        logger.info(f"   ✅ Canciones procesadas: {stored_count}")
        
        # 7. Cerrar conexión
        logger.info("7. Cerrando conexión...")
        db_manager.close()
        
        logger.info("✅ Prueba completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en la prueba: {e}")
        return False


if __name__ == "__main__":
    success = test_song_processor()
    if success:
        logger.info("🎉 Todas las pruebas pasaron")
    else:
        logger.error("💥 Algunas pruebas fallaron")
        sys.exit(1) 