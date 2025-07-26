#!/usr/bin/env python3
"""
Script para sobreescribir un episodio específico en la base de datos.
Utiliza exactamente el mismo flujo que main.py para garantizar consistencia.
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir / "src"))

from components.config_manager import ConfigManager
from components.database_manager import DatabaseManager
from components.rss_data_processor import RSSDataProcessor
from components.wordpress_data_processor import WordPressDataProcessor
from components.wordpress_client import WordPressClient
from components.data_processor import DataProcessor
from utils.logger import logger


def find_episode_by_number(episodes: list, target_number: int) -> dict:
    """
    Busca un episodio específico por número de programa.
    
    Args:
        episodes: Lista de episodios procesados
        target_number: Número del episodio a buscar
        
    Returns:
        dict: Datos del episodio encontrado o None
    """
    for episode in episodes:
        if episode.get('program_number') == target_number:
            return episode
    return None


def overwrite_episode_in_database(episode_number: int, dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Sobreescribe un episodio específico en la base de datos usando el mismo flujo que main.py.
    
    Args:
        episode_number: Número del episodio a sobreescribir
        dry_run: Si es True, solo muestra los datos sin actualizar la BD
        verbose: Si mostrar información detallada
        
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    try:
        logger.info(f"🔄 Iniciando sobreescritura del episodio {episode_number}")
        
        # 1. Cargar configuración (igual que main.py)
        logger.info("📋 Cargando configuración...")
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        rss_url = config_manager.get_rss_url()
        wordpress_config = config_manager.get_wordpress_config()
        
        # 2. Inicializar componentes (igual que main.py)
        logger.info("🔧 Inicializando componentes...")
        
        # Gestor de base de datos
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # Procesadores de datos
        rss_processor = RSSDataProcessor(rss_url)
        wordpress_processor = WordPressDataProcessor()
        wordpress_client = WordPressClient(wordpress_config['api_url'])
        data_processor = DataProcessor(rss_processor, wordpress_processor)
        
        logger.info("✅ Todos los componentes inicializados correctamente")
        
        # 3. Obtener episodios del RSS (igual que main.py)
        logger.info("📻 Descargando episodios del RSS...")
        rss_episodes = rss_processor.fetch_and_process_entries()
        logger.info(f"📊 Encontrados {len(rss_episodes)} episodios en el RSS")
        
        # 4. Buscar el episodio específico
        logger.info(f"🔍 Buscando episodio número {episode_number}...")
        target_episode = find_episode_by_number(rss_episodes, episode_number)
        
        if not target_episode:
            logger.error(f"❌ No se encontró el episodio número {episode_number}")
            return False
        
        logger.info(f"✅ Episodio encontrado: {target_episode.get('title', 'Sin título')}")
        
        # 5. Verificar si el episodio ya existe en la base de datos
        logger.info("🔍 Verificando si el episodio existe en la base de datos...")
        existing_episode = db_manager.get_podcast_by_program_number(episode_number)
        
        if existing_episode:
            logger.info(f"📊 Episodio encontrado en BD con ID: {existing_episode.get('id')}")
            logger.info(f"📅 Fecha en BD: {existing_episode.get('date', 'Sin fecha')}")
            logger.info(f"🎵 Título en BD: {existing_episode.get('title', 'Sin título')}")
            
            if not dry_run:
                # Eliminar el episodio existente para evitar conflictos
                logger.info(f"🗑️ Eliminando episodio existente con ID: {existing_episode.get('id')}")
                delete_result = db_manager.client.table('podcasts').delete().eq('id', existing_episode.get('id')).execute()
                if delete_result.data:
                    logger.info(f"✅ Episodio {existing_episode.get('id')} eliminado correctamente")
                else:
                    logger.warning("⚠️ No se pudo eliminar el episodio existente")
        else:
            logger.info("📊 Episodio no encontrado en BD, se creará uno nuevo")
        
        # 6. Procesar y unificar con datos de WordPress (igual que main.py)
        logger.info("🔗 Enriqueciendo datos con WordPress...")
        episode_data = data_processor.process_single_episode(
            rss_episode=target_episode,
            wordpress_client=wordpress_client
        )
        
        if not episode_data:
            logger.warning("⚠️ No se pudieron obtener datos unificados")
            return False
        
        # 7. Mostrar información del episodio
        logger.info("📋 === INFORMACIÓN DEL EPISODIO A ACTUALIZAR ===")
        logger.info(f"🎵 Título: {episode_data.get('title', 'Sin título')}")
        logger.info(f"📅 Fecha: {episode_data.get('date', 'Sin fecha')}")
        logger.info(f"🔢 Número: {episode_data.get('program_number', 'Sin número')}")
        logger.info(f"⏱️ Duración: {episode_data.get('duration', 'Sin duración')}")
        logger.info(f"📁 Tamaño: {episode_data.get('file_size', 'Sin tamaño')}")
        logger.info(f"🔗 URL: {episode_data.get('url', 'Sin URL')}")
        
        # Información de WordPress si está disponible
        if episode_data.get('wordpress_id'):
            logger.info("🌐 === DATOS DE WORDPRESS ===")
            logger.info(f"🆔 WordPress ID: {episode_data.get('wordpress_id')}")
            logger.info(f"📝 Título WordPress: {episode_data.get('wordpress_title', 'Sin título')}")
            logger.info(f"📄 Extracto: {episode_data.get('wordpress_excerpt', 'Sin extracto')[:100]}...")
            logger.info(f"🏷️ Categorías: {', '.join(episode_data.get('wordpress_categories', []))}")
            logger.info(f"🏷️ Tags: {', '.join(episode_data.get('wordpress_tags', []))}")
            
            if episode_data.get('wordpress_playlist_data'):
                logger.info(f"🎵 Playlist WordPress: {len(episode_data['wordpress_playlist_data'])} canciones")
        
        # Información de playlists
        logger.info("🎵 === INFORMACIÓN DE PLAYLISTS ===")
        rss_playlist = episode_data.get('rss_playlist', '')
        if rss_playlist:
            logger.info(f"📻 Playlist RSS: {len(rss_playlist.split('|'))} canciones")
            if verbose:
                logger.info(f"📻 Contenido RSS: {rss_playlist[:200]}...")
        
        web_playlist = episode_data.get('wordpress_playlist_data', [])
        if web_playlist and isinstance(web_playlist, list):
            logger.info(f"🌐 Playlist Web: {len(web_playlist)} canciones")
            if verbose and web_playlist:
                for i, song in enumerate(web_playlist[:5], 1):
                    logger.info(f"  {i}. {song.get('title', 'Sin título')} - {song.get('artist', 'Sin artista')}")
        else:
            logger.info("🌐 Playlist Web: No disponible")
        
        # 8. Ejecutar la actualización o mostrar preview
        if dry_run:
            logger.info("🔍 === MODO DRY RUN ===")
            logger.info("📝 Los datos están listos para ser insertados")
            logger.info("💡 Ejecuta sin --dry-run para realizar la inserción real")
            
            # Guardar datos en archivo temporal para revisión
            temp_file = f"episodio_{episode_number}_preview.json"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(episode_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"💾 Datos guardados en {temp_file} para revisión")
            
        else:
            logger.info("💾 Insertando episodio en la base de datos...")
            
            # Usar exactamente el mismo método que main.py
            db_manager.insert_full_podcast(episode_data)
            
            logger.info(f"✅ Episodio {episode_number} insertado exitosamente en la base de datos")
            
            # Verificar la inserción
            updated_episode = db_manager.get_podcast_by_program_number(episode_number)
            if updated_episode:
                logger.info(f"✅ Verificación exitosa: episodio {episode_number} insertado")
                logger.info(f"🆔 ID en BD: {updated_episode.get('id')}")
                logger.info(f"📅 Fecha insertada: {updated_episode.get('date', 'Sin fecha')}")
                logger.info(f"🎵 Título insertado: {updated_episode.get('title', 'Sin título')}")
            else:
                logger.warning("⚠️ No se pudo verificar la inserción")
        
        logger.info("🎉 Sobreescritura completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error durante la sobreescritura: {e}")
        return False
    
    finally:
        # Cerrar conexión a la base de datos
        if 'db_manager' in locals():
            logger.info("🔒 Cerrando conexión a la base de datos...")
            db_manager.close()


def main():
    """
    Función principal del script.
    """
    parser = argparse.ArgumentParser(
        description="Sobreescribe un episodio específico en la base de datos usando el mismo flujo que main.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python overwrite_episode.py 95                    # Sobreescribir episodio 95
  python overwrite_episode.py 485 --dry-run         # Preview sin actualizar
  python overwrite_episode.py 100 -v                # Modo verbose
  python overwrite_episode.py 200 --dry-run -v      # Preview verbose
        """
    )
    
    parser.add_argument(
        'episode_number',
        type=int,
        help='Número del episodio a sobreescribir'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mostrar preview sin actualizar la base de datos'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mostrar información detallada'
    )
    
    args = parser.parse_args()
    
    # Validar número de episodio
    if args.episode_number <= 0:
        logger.error("❌ El número de episodio debe ser mayor que 0")
        sys.exit(1)
    
    # Ejecutar sobreescritura
    success = overwrite_episode_in_database(
        episode_number=args.episode_number,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
    
    if success:
        if args.dry_run:
            logger.info("✅ Preview completado exitosamente")
        else:
            logger.info("✅ Sobreescritura completada exitosamente")
        sys.exit(0)
    else:
        logger.error("❌ Sobreescritura falló")
        sys.exit(1)


if __name__ == "__main__":
    main() 