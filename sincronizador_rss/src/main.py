#!/usr/bin/env python3
"""
Script principal del sincronizador RSS.
Orquesta todos los componentes para leer el RSS, enriquecer los datos con WordPress
y guardarlos en Supabase.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from components.config_manager import ConfigManager
from components.database_manager import DatabaseManager
from components.rss_data_processor import RSSDataProcessor
from components.wordpress_data_processor import WordPressDataProcessor
from components.wordpress_client import WordPressClient
from components.data_processor import DataProcessor
from components.song_processor import SongProcessor
from utils.logger import logger


def main():
    """
    Función principal que orquesta todo el proceso de sincronización.
    """
    logger.info("🚀 Iniciando sincronizador RSS")
    
    try:
        # Inicialización de componentes
        logger.info("📋 Inicializando componentes...")
        
        # 1. Cargar configuración
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        rss_url = config_manager.get_rss_url()
        wordpress_config = config_manager.get_wordpress_config()
        
        logger.info("✅ Configuración cargada correctamente")
        
        # 2. Inicializar gestor de base de datos
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # 3. Inicializar cliente de WordPress
        wordpress_client = WordPressClient(wordpress_config['api_url'])
        
        # 4. Inicializar procesadores de datos
        rss_processor = RSSDataProcessor(rss_url)
        wordpress_processor = WordPressDataProcessor()
        
        # 5. Inicializar procesador principal (orquestador)
        data_processor = DataProcessor(rss_processor, wordpress_processor)
        
        logger.info("✅ Todos los componentes inicializados correctamente")
        
        # Lógica principal de sincronización
        logger.info("🔄 Iniciando proceso de sincronización...")
        
        # 1. Obtener el episodio más reciente de la base de datos
        logger.info("📊 Verificando episodio más reciente en la base de datos...")
        latest_podcast = db_manager.get_latest_podcast()
        
        if latest_podcast:
            latest_program_number = latest_podcast.get('program_number', 0)
            latest_title = latest_podcast.get('title', 'Sin título')
            logger.info(f"📅 Episodio más reciente en BD: {latest_title} (Número: {latest_program_number})")
        else:
            logger.info("📅 No hay episodios en la base de datos, se procesarán todos")
            latest_program_number = 0
        
        # 2. Obtener episodios del RSS
        rss_episodes = rss_processor.fetch_and_process_entries()
        logger.info(f"📻 Encontrados {len(rss_episodes)} episodios en el RSS")
        
        # 3. Filtrar solo episodios nuevos (con número mayor al último en BD)
        new_episodes = []
        if latest_program_number > 0:
            logger.info(f"📊 Comparando por número de episodio: último en BD = {latest_program_number}")
            
            for episode in rss_episodes:
                episode_program_number = episode.get('program_number', 0)
                episode_title = episode.get('title', 'Sin título')
                
                if episode_program_number > latest_program_number:
                    new_episodes.append(episode)
                    logger.debug(f"🆕 Episodio nuevo encontrado: {episode_title} (Número: {episode_program_number})")
                else:
                    # Los episodios están ordenados por número, podemos parar aquí
                    logger.debug(f"⏭️ Episodio ya existe: {episode_title} (Número: {episode_program_number})")
                    break
            
            logger.info(f"🆕 Encontrados {len(new_episodes)} episodios nuevos para procesar")
        else:
            # Si no hay episodios en BD, procesar todos
            new_episodes = rss_episodes
            logger.info(f"🆕 Procesando todos los {len(new_episodes)} episodios (BD vacía)")
        
        # 4. Si no hay episodios nuevos, terminar
        if not new_episodes:
            logger.info("✅ No hay episodios nuevos. Sincronización completada.")
            return
        
        # 5. Procesar solo los episodios nuevos
        logger.info(f"🚀 Procesando {len(new_episodes)} episodios nuevos...")
        
        # Contadores para el reporte
        total_new_episodes = len(new_episodes)
        processed_episodes = 0
        error_episodes = 0
        
        # Procesar cada episodio nuevo
        for i, rss_episode in enumerate(new_episodes, 1):
            episode_title = rss_episode.get('title', 'Sin título')
            episode_date = rss_episode.get('date', 'Sin fecha')
            
            logger.info(f"📝 Procesando episodio nuevo {i}/{total_new_episodes}: {episode_title} ({episode_date})")
            
            try:
                # Enriquecer y unificar datos con WordPress
                logger.info(f"🔗 Enriqueciendo datos con WordPress para: {episode_title}")
                episode_data = data_processor.process_single_episode(
                    rss_episode=rss_episode,
                    wordpress_client=wordpress_client
                )
                
                if not episode_data:
                    logger.warning(f"⚠️ No se pudieron obtener datos unificados para: {episode_title}")
                    error_episodes += 1
                    continue
                
                # Insertar en la base de datos
                logger.info(f"💾 Guardando episodio en la BD: {episode_title}")
                new_podcast_id = db_manager.insert_full_podcast(episode_data)
                
                # Procesar y almacenar canciones con SongProcessor
                logger.info(f"🎵 Procesando canciones para: {episode_title}")
                song_processor = SongProcessor(db_manager)
                
                stored_songs_count = song_processor.process_and_store_songs(
                    podcast_id=new_podcast_id,
                    web_playlist=episode_data.get('web_playlist'),
                    rss_playlist=episode_data.get('rss_playlist')
                )
                
                logger.info(f"✅ Episodio guardado exitosamente: {episode_title} ({stored_songs_count} canciones)")
                processed_episodes += 1
                
            except Exception as e:
                logger.error(f"❌ Error al procesar episodio '{episode_title}': {e}")
                error_episodes += 1
                continue
        
        # Reporte final
        logger.info("📊 === REPORTE FINAL DE SINCRONIZACIÓN ===")
        logger.info(f"📻 Total de episodios en RSS: {len(rss_episodes)}")
        logger.info(f"🆕 Episodios nuevos encontrados: {total_new_episodes}")
        logger.info(f"✅ Episodios procesados exitosamente: {processed_episodes}")
        logger.info(f"❌ Episodios con errores: {error_episodes}")
        logger.info("🎉 Sincronización completada")
        
    except Exception as e:
        logger.error(f"❌ Error crítico en la sincronización: {e}")
        raise
    
    finally:
        # Cerrar conexión a la base de datos
        logger.info("🔒 Cerrando conexión a la base de datos...")
        db_manager.close()
        logger.info("✅ Sincronizador finalizado correctamente")


if __name__ == "__main__":
    """
    Punto de entrada principal del sincronizador RSS.
    """
    main() 


# source .venv/bin/activate
# python src/main.py

