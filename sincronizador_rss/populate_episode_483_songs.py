"""
Script para rellenar las canciones del episodio 483 desde los datos del RSS.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir / "src"))

# Importaciones directas sin usar __init__.py
import importlib.util

# Importar SongProcessor directamente
spec = importlib.util.spec_from_file_location(
    "song_processor", 
    current_dir / "src" / "components" / "song_processor.py"
)
song_processor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(song_processor_module)
SongProcessor = song_processor_module.SongProcessor

# Importar RSSDataProcessor directamente
spec = importlib.util.spec_from_file_location(
    "rss_data_processor", 
    current_dir / "src" / "components" / "rss_data_processor.py"
)
rss_data_processor_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rss_data_processor_module)
RSSDataProcessor = rss_data_processor_module.RSSDataProcessor

# Importar DatabaseManager directamente
spec = importlib.util.spec_from_file_location(
    "database_manager", 
    current_dir / "src" / "components" / "database_manager.py"
)
database_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database_manager_module)
DatabaseManager = database_manager_module.DatabaseManager

# Importar ConfigManager directamente
spec = importlib.util.spec_from_file_location(
    "config_manager", 
    current_dir / "src" / "components" / "config_manager.py"
)
config_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_manager_module)
ConfigManager = config_manager_module.ConfigManager

# Importar logger directamente
spec = importlib.util.spec_from_file_location(
    "logger", 
    current_dir / "src" / "utils" / "logger.py"
)
logger_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger_module)
logger = logger_module.logger


def populate_episode_483_songs():
    """
    Rellena las canciones del episodio 483 desde los datos del RSS.
    """
    try:
        logger.info("=== RELLENANDO CANCIONES DEL EPISODIO 483 ===")
        
        # 1. Configurar conexión
        logger.info("1. Configurando conexión...")
        cfg_manager = ConfigManager()
        supabase_credentials = cfg_manager.get_supabase_credentials()
        
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # 2. Obtener el episodio 483 de la BD
        logger.info("2. Obteniendo episodio 483 de la BD...")
        episode_483 = db_manager.get_podcast_by_program_number(483)
        
        if not episode_483:
            logger.error("❌ No se encontró el episodio 483 en la BD")
            return False
        
        logger.info(f"   ✅ Episodio encontrado: {episode_483.get('title', 'Sin título')}")
        logger.info(f"   ID del episodio: {episode_483.get('id')}")
        
        # 3. Verificar si ya tiene canciones
        logger.info("3. Verificando canciones existentes...")
        existing_songs = db_manager.client.table('songs').select('id').eq('podcast_id', episode_483['id']).execute()
        existing_count = len(existing_songs.data) if existing_songs.data else 0
        
        if existing_count > 0:
            logger.warning(f"⚠️  El episodio ya tiene {existing_count} canciones")
            confirm = input("¿Continuar y agregar más canciones? (escribe 'SI' para confirmar): ")
            if confirm != 'SI':
                logger.info("❌ Operación cancelada por el usuario")
                return False
        
        # 4. Obtener datos del RSS
        logger.info("4. Obteniendo datos del RSS...")
        rss_processor = RSSDataProcessor("https://www.ivoox.com/podcast-popcasting_fg_f158927_filtro_1.xml")
        
        # Buscar el episodio 483 en el RSS
        rss_entries = rss_processor.fetch_and_process_entries()
        episode_483_rss = None
        
        for entry in rss_entries:
            if entry.get('program_number') == 483:
                episode_483_rss = entry
                break
        
        if not episode_483_rss:
            logger.error("❌ No se encontró el episodio 483 en el RSS")
            return False
        
        logger.info(f"   ✅ Episodio encontrado en RSS: {episode_483_rss.get('title', 'Sin título')}")
        
        # 5. Obtener la playlist del RSS
        rss_playlist = episode_483_rss.get('rss_playlist')
        if not rss_playlist:
            logger.error("❌ El episodio 483 no tiene playlist en el RSS")
            return False
        
        logger.info(f"   Playlist RSS encontrada: {len(rss_playlist)} caracteres")
        logger.info(f"   Contenido: {rss_playlist[:200]}...")
        
        # 6. Crear SongProcessor y procesar canciones
        logger.info("5. Procesando canciones con SongProcessor...")
        song_processor = SongProcessor(db_manager)
        
        # Procesar y almacenar canciones
        stored_count = song_processor.process_and_store_songs(
            podcast_id=episode_483['id'],
            rss_playlist=rss_playlist
        )
        
        logger.info(f"   ✅ Canciones almacenadas: {stored_count}")
        
        # 7. Verificar el resultado
        logger.info("6. Verificando resultado...")
        final_songs = db_manager.client.table('songs').select('*').eq('podcast_id', episode_483['id']).execute()
        final_count = len(final_songs.data) if final_songs.data else 0
        
        logger.info(f"   Total de canciones en el episodio: {final_count}")
        
        if final_songs.data:
            logger.info("   Primeras 3 canciones:")
            for i, song in enumerate(final_songs.data[:3]):
                logger.info(f"   - {song.get('position')}: {song.get('artist')} · {song.get('title')}")
        
        # 8. Cerrar conexión
        logger.info("7. Cerrando conexión...")
        db_manager.close()
        
        logger.info("✅ Proceso completado exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error rellenando canciones: {e}")
        return False


if __name__ == "__main__":
    success = populate_episode_483_songs()
    if success:
        logger.info("🎉 Canciones del episodio 483 rellenadas correctamente")
    else:
        logger.error("💥 Error al rellenar las canciones")
        sys.exit(1) 