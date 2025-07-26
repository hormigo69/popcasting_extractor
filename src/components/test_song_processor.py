"""
Script de prueba para el componente SongProcessor.
Verifica que el procesamiento de canciones funcione correctamente.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from src.components.song_processor import SongProcessor
from sincronizador_rss.src.components.database_manager import DatabaseManager
from sincronizador_rss.src.components.config_manager import ConfigManager
from sincronizador_rss.src.utils.logger import logger


def test_song_processor():
    """Prueba el componente SongProcessor con datos de ejemplo."""
    
    print("🧪 PRUEBA DEL COMPONENTE SONGPROCESSOR")
    print("=" * 50)
    
    try:
        # 1. Configurar conexión a la base de datos
        print("1. Configurando conexión a la base de datos...")
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # 2. Crear instancia del SongProcessor
        print("2. Creando instancia del SongProcessor...")
        song_processor = SongProcessor(db_manager)
        
        # 3. Probar parseo de playlist RSS
        print("3. Probando parseo de playlist RSS...")
        rss_playlist_text = """
        the beatles · rain  ::  the doors · wintertime love  ::  joni mitchell · don't interrupt the sorrow
        
        :::::: invita a Popcasting a café https://ko-fi.com/popcasting
        """
        
        parsed_songs = song_processor._parse_rss_playlist_string(rss_playlist_text)
        print(f"   ✅ Canciones parseadas: {len(parsed_songs)}")
        for i, song in enumerate(parsed_songs[:3]):  # Mostrar solo las primeras 3
            print(f"      {i+1}. {song['artist']} - {song['title']}")
        
        # 4. Probar validación de canciones
        print("4. Probando validación de canciones...")
        test_songs = [
            {"artist": "the beatles", "title": "rain"},  # Válida
            {"artist": "http://invalid.com", "title": "test"},  # Inválida (URL)
            {"artist": "popcasting", "title": "test"},  # Inválida (palabra clave)
            {"artist": "a", "title": "b"},  # Inválida (muy corta)
        ]
        
        for i, song in enumerate(test_songs):
            is_valid = song_processor.validate_song_data(song)
            print(f"   Canción {i+1}: {'✅ Válida' if is_valid else '❌ Inválida'} - {song['artist']} - {song['title']}")
        
        # 5. Probar limpieza de texto
        print("5. Probando limpieza de texto...")
        dirty_text = """
        the beatles · rain  ::  the doors · wintertime love
        
        :::::: invita a Popcasting a café https://ko-fi.com/popcasting
        @rss_data_processor.py
        """
        
        cleaned_text = song_processor._clean_playlist_text(dirty_text)
        print(f"   Texto original: {repr(dirty_text[:50])}...")
        print(f"   Texto limpio: {repr(cleaned_text)}")
        
        # 6. Probar parseo de canción individual
        print("6. Probando parseo de canción individual...")
        test_song_texts = [
            "the beatles · rain",
            "the doors • wintertime love",
            "joni mitchell - don't interrupt the sorrow",
            "invalid text without separator",
        ]
        
        for song_text in test_song_texts:
            parsed = song_processor._parse_song_text(song_text)
            if parsed:
                print(f"   ✅ '{song_text}' -> {parsed['artist']} - {parsed['title']}")
            else:
                print(f"   ❌ '{song_text}' -> No válido")
        
        print("\n✅ Todas las pruebas completadas exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        logger.error(f"Error en test_song_processor: {e}")
        return False
    
    finally:
        # Cerrar conexión
        if 'db_manager' in locals():
            db_manager.close()


def test_with_real_data():
    """Prueba el SongProcessor con datos reales de la base de datos."""
    
    print("\n🎵 PRUEBA CON DATOS REALES")
    print("=" * 50)
    
    try:
        # Configurar conexión
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        song_processor = SongProcessor(db_manager)
        
        # Obtener un podcast de ejemplo
        podcasts = db_manager.get_podcasts_by_batch(1)
        if not podcasts:
            print("❌ No hay podcasts en la base de datos para probar")
            return False
        
        test_podcast = podcasts[0]
        podcast_id = test_podcast['id']
        title = test_podcast.get('title', 'Sin título')
        
        print(f"Probando con podcast: {title} (ID: {podcast_id})")
        
        # Probar con rss_playlist si existe
        rss_playlist = test_podcast.get('rss_playlist')
        if rss_playlist:
            print(f"   RSS Playlist encontrada: {len(rss_playlist)} caracteres")
            
            # Parsear la playlist
            parsed_songs = song_processor._parse_rss_playlist_string(rss_playlist)
            print(f"   Canciones parseadas: {len(parsed_songs)}")
            
            if parsed_songs:
                print("   Primeras 3 canciones:")
                for i, song in enumerate(parsed_songs[:3]):
                    print(f"      {i+1}. {song['artist']} - {song['title']}")
        
        # Probar con web_playlist si existe
        web_playlist = test_podcast.get('web_playlist')
        if web_playlist:
            print(f"   Web Playlist encontrada: {len(web_playlist)} caracteres")
            
            try:
                import json
                web_songs = json.loads(web_playlist)
                if isinstance(web_songs, list):
                    print(f"   Canciones web: {len(web_songs)}")
                    if web_songs:
                        print("   Primeras 3 canciones web:")
                        for i, song in enumerate(web_songs[:3]):
                            artist = song.get('artist', 'Unknown')
                            title = song.get('title', 'Unknown')
                            print(f"      {i+1}. {artist} - {title}")
            except json.JSONDecodeError:
                print("   ❌ Web playlist no es JSON válido")
        
        print("\n✅ Prueba con datos reales completada!")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba con datos reales: {e}")
        logger.error(f"Error en test_with_real_data: {e}")
        return False
    
    finally:
        if 'db_manager' in locals():
            db_manager.close()


if __name__ == "__main__":
    """Ejecutar las pruebas."""
    print("🚀 INICIANDO PRUEBAS DEL SONGPROCESSOR")
    print("=" * 60)
    
    # Ejecutar pruebas básicas
    basic_test_success = test_song_processor()
    
    # Ejecutar pruebas con datos reales
    real_data_test_success = test_with_real_data()
    
    # Resumen
    print("\n📊 RESUMEN DE PRUEBAS")
    print("=" * 30)
    print(f"Pruebas básicas: {'✅ Exitosas' if basic_test_success else '❌ Fallidas'}")
    print(f"Pruebas con datos reales: {'✅ Exitosas' if real_data_test_success else '❌ Fallidas'}")
    
    if basic_test_success and real_data_test_success:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        exit(0)
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisar los errores arriba.")
        exit(1) 