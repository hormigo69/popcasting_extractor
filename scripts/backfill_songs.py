#!/usr/bin/env python3
"""
Script para rellenar el histórico de canciones en la tabla songs.

Este script obtiene todos los podcasts de la base de datos y utiliza SongProcessor
para procesar y almacenar las canciones de cada uno. Es útil para:
- Regenerar datos después de cambios en el esquema
- Poblar canciones para podcasts existentes
- Verificar la integridad de los datos
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir / "src"))

# Importaciones directas sin usar __init__.py
import importlib.util

# Importar ConfigManager directamente
spec = importlib.util.spec_from_file_location(
    "config_manager", 
    current_dir / "src" / "components" / "config_manager.py"
)
config_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_manager_module)
ConfigManager = config_manager_module.ConfigManager

# Importar DatabaseManager directamente
spec = importlib.util.spec_from_file_location(
    "database_manager", 
    current_dir / "src" / "components" / "database_manager.py"
)
database_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database_manager_module)
DatabaseManager = database_manager_module.DatabaseManager

# Importar SongProcessor directamente
spec = importlib.util.spec_from_file_location(
    "song_processor", 
    current_dir / "src" / "components" / "song_processor.py"
)
song_processor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(song_processor_module)
SongProcessor = song_processor_module.SongProcessor

# Importar logger directamente
spec = importlib.util.spec_from_file_location(
    "logger", 
    current_dir / "src" / "utils" / "logger.py"
)
logger_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_module)
logger = logger_module.logger


def backfill_songs():
    """
    Rellena el histórico de canciones para todos los podcasts en la base de datos.
    """
    try:
        logger.info("🚀 Iniciando relleno histórico de canciones")
        
        # Configurar conexión a la base de datos
        cfg_manager = ConfigManager()
        supabase_credentials = cfg_manager.get_supabase_credentials()
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # Crear instancia de SongProcessor
        song_processor = SongProcessor(db_manager)
        
        # Obtener todos los podcasts
        all_podcasts = db_manager.get_all_podcasts()
        logger.info(f"📻 Encontrados {len(all_podcasts)} podcasts para procesar")
        
        # Contadores para el reporte
        total_podcasts = len(all_podcasts)
        processed_podcasts = 0
        error_podcasts = 0
        total_songs_stored = 0
        
        # Procesar cada podcast
        for i, podcast in enumerate(all_podcasts, 1):
            try:
                podcast_id = podcast.get('id')
                program_number = podcast.get('program_number', 'N/A')
                title = podcast.get('title', 'Sin título')
                
                logger.info(f"🎵 [{i}/{total_podcasts}] Procesando podcast {program_number}: {title}")
                
                # Verificar si ya tiene canciones
                existing_songs = db_manager.client.table('songs').select('id').eq('podcast_id', podcast_id).execute()
                if existing_songs.data:
                    logger.info(f"   ⏭️  Ya tiene {len(existing_songs.data)} canciones, saltando...")
                    processed_podcasts += 1
                    continue
                
                # Obtener playlists
                web_playlist = podcast.get('web_playlist')
                rss_playlist = podcast.get('rss_playlist')
                
                # Procesar canciones
                stored_songs_count = song_processor.process_and_store_songs(
                    podcast_id=podcast_id,
                    web_playlist=web_playlist,
                    rss_playlist=rss_playlist
                )
                
                if stored_songs_count > 0:
                    logger.info(f"   ✅ Almacenadas {stored_songs_count} canciones")
                    total_songs_stored += stored_songs_count
                else:
                    logger.warning(f"   ⚠️  No se almacenaron canciones")
                
                processed_podcasts += 1
                
            except Exception as e:
                logger.error(f"   ❌ Error procesando podcast {program_number}: {e}")
                error_podcasts += 1
                continue
        
        # Reporte final
        logger.info("🎉 Relleno histórico completado")
        logger.info(f"📊 Estadísticas finales:")
        logger.info(f"   📻 Total de podcasts: {total_podcasts}")
        logger.info(f"   ✅ Procesados exitosamente: {processed_podcasts}")
        logger.info(f"   ❌ Con errores: {error_podcasts}")
        logger.info(f"   🎵 Total de canciones almacenadas: {total_songs_stored}")
        
        # Cerrar conexión
        db_manager.close()
        
    except Exception as e:
        logger.error(f"❌ Error general en backfill_songs: {e}")
        raise


if __name__ == "__main__":
    backfill_songs() 