"""
Ejemplo de uso del SongProcessor para el sincronizador RSS.
Este archivo demuestra cómo integrar el SongProcessor en el flujo de trabajo.
"""

import sys
import os
import json
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from components.song_processor import SongProcessor
from components.database_manager import DatabaseManager
from components.config_manager import ConfigManager
from utils.logger import logger


def example_usage():
    """
    Ejemplo de cómo usar el SongProcessor en el flujo de trabajo.
    """
    try:
        # 1. Configurar la conexión a la base de datos
        logger.info("1. Configurando conexión a la base de datos...")
        cfg_manager = ConfigManager()
        supabase_credentials = cfg_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # 2. Crear instancia del SongProcessor
        logger.info("2. Creando instancia del SongProcessor...")
        song_processor = SongProcessor(db_manager)
        
        # 3. Ejemplo de datos de prueba (JSON strings como los que vienen de los procesadores)
        logger.info("3. Preparando datos de prueba...")
        
        # Ejemplo de playlist del RSS (ya procesada por RSSDataProcessor)
        rss_playlist_json = json.dumps([
            {"position": 1, "artist": "the beatles", "title": "rain"},
            {"position": 2, "artist": "pink floyd", "title": "time"},
            {"position": 3, "artist": "led zeppelin", "title": "stairway to heaven"},
            {"position": 4, "artist": "queen", "title": "bohemian rhapsody"},
            {"position": 5, "artist": "the rolling stones", "title": "paint it black"}
        ], ensure_ascii=False)
        
        # Ejemplo de playlist de la web (ya procesada por WordPressDataProcessor)
        web_playlist_json = json.dumps([
            {"position": 1, "artist": "The Beatles", "title": "Rain"},
            {"position": 2, "artist": "Pink Floyd", "title": "Time"},
            {"position": 3, "artist": "Led Zeppelin", "title": "Stairway to Heaven"},
            {"position": 4, "artist": "Queen", "title": "Bohemian Rhapsody"},
            {"position": 5, "artist": "The Rolling Stones", "title": "Paint It Black"}
        ], ensure_ascii=False)
        
        # 4. Simular un podcast_id
        podcast_id = 999  # ID de prueba
        
        logger.info(f"   Playlist RSS JSON: {len(rss_playlist_json)} caracteres")
        logger.info(f"   Playlist Web JSON: {len(web_playlist_json)} caracteres")
        
        # 5. Obtener información de las playlists
        logger.info("4. Obteniendo información de playlists...")
        playlist_info = song_processor.get_playlist_info(
            web_playlist=web_playlist_json,
            rss_playlist=rss_playlist_json
        )
        
        logger.info(f"   Playlist Web: {playlist_info['web_playlist_count']} canciones")
        logger.info(f"   Playlist RSS: {playlist_info['rss_playlist_count']} canciones")
        logger.info(f"   Seleccionada: {playlist_info['selected_playlist']} ({playlist_info['selected_count']} canciones)")
        
        # 6. Procesar y almacenar canciones
        logger.info("5. Procesando y almacenando canciones...")
        stored_count = song_processor.process_and_store_songs(
            podcast_id=podcast_id,
            web_playlist=web_playlist_json,
            rss_playlist=rss_playlist_json
        )
        
        logger.info(f"   ✅ Canciones almacenadas: {stored_count}")
        
        # 7. Ejemplo con solo playlist RSS
        logger.info("6. Probando solo con playlist RSS...")
        stored_count_rss = song_processor.process_and_store_songs(
            podcast_id=podcast_id + 1,
            rss_playlist=rss_playlist_json
        )
        
        logger.info(f"   ✅ Canciones almacenadas desde RSS: {stored_count_rss}")
        
        # 8. Cerrar conexión
        logger.info("7. Cerrando conexión...")
        db_manager.close()
        
        logger.info("✅ Ejemplo completado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en el ejemplo: {e}")
        raise


def test_song_processor_methods():
    """
    Prueba los métodos individuales del SongProcessor.
    """
    try:
        # Configurar conexión
        cfg_manager = ConfigManager()
        supabase_credentials = cfg_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        song_processor = SongProcessor(db_manager)
        
        # Probar parseo de playlist JSON
        logger.info("Probando parseo de playlist JSON...")
        test_playlist_json = json.dumps([
            {"position": 1, "artist": "The Beatles", "title": "Rain"},
            {"position": 2, "artist": "Pink Floyd", "title": "Time"},
            {"position": 3, "artist": "Led Zeppelin", "title": "Stairway to Heaven"}
        ], ensure_ascii=False)
        
        parsed_songs = song_processor._parse_json_playlist(test_playlist_json)
        logger.info(f"   Canciones parseadas: {len(parsed_songs)}")
        for song in parsed_songs:
            logger.info(f"   - {song['position']}: {song['artist']} · {song['title']}")
        
        # Probar validación de canciones
        logger.info("Probando validación de canciones...")
        test_song = {"artist": "The Beatles", "title": "Rain"}
        is_valid = song_processor._validate_song_data(test_song)
        logger.info(f"   Canción válida: {is_valid}")
        
        # Probar canción inválida
        invalid_song = {"artist": "http://spam.com", "title": "Spam"}
        is_invalid = song_processor._validate_song_data(invalid_song)
        logger.info(f"   Canción inválida detectada: {not is_invalid}")
        
        # Probar información de playlist
        logger.info("Probando información de playlist...")
        info = song_processor.get_playlist_info(web_playlist=test_playlist_json)
        logger.info(f"   Información: {info}")
        
        db_manager.close()
        
    except Exception as e:
        logger.error(f"❌ Error en pruebas: {e}")
        raise


if __name__ == "__main__":
    logger.info("=== EJEMPLO DE USO DEL SONGPROCESSOR ===")
    
    # Ejecutar ejemplo principal
    example_usage()
    
    logger.info("\n=== PRUEBAS DE MÉTODOS ===")
    
    # Ejecutar pruebas de métodos
    test_song_processor_methods()
    
    logger.info("✅ Todas las pruebas completadas") 