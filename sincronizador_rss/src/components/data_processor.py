from typing import Dict, Optional, List
import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from utils.logger import logger
from components.rss_data_processor import RSSDataProcessor
from components.wordpress_data_processor import WordPressDataProcessor


class DataProcessor:
    """
    Orquestador que unifica datos del RSS y WordPress usando procesadores específicos.
    """
    
    def __init__(self, rss_processor: RSSDataProcessor, wordpress_processor: WordPressDataProcessor):
        """
        Inicializa el procesador de datos unificado.
        
        Args:
            rss_processor: Instancia del procesador de RSS
            wordpress_processor: Instancia del procesador de WordPress
        """
        self.rss_processor = rss_processor
        self.wordpress_processor = wordpress_processor
        logger.info("DataProcessor (orquestador) inicializado")
    
    def process_entry(self, rss_entry, wordpress_data: Optional[Dict] = None) -> Dict:
        """
        Procesa y unifica los datos de una entrada RSS con los datos de WordPress.
        
        Args:
            rss_entry: Objeto de entrada del feedparser
            wordpress_data: Diccionario con datos de la API de WordPress (puede ser None)
            
        Returns:
            Dict: Diccionario unificado con todos los datos procesados
        """
        try:
            # Procesar datos del RSS
            rss_processed = self._process_rss_entry(rss_entry)
            
            # Procesar datos de WordPress si están disponibles
            wordpress_processed = {}
            if wordpress_data:
                wordpress_processed = self.wordpress_processor.process_post_data(wordpress_data)
            
            # Unificar los datos
            unified_data = self._unify_data(rss_processed, wordpress_processed)
            
            logger.debug(f"Datos unificados para entrada '{unified_data.get('title', 'Sin título')}'")
            return unified_data
            
        except Exception as e:
            logger.error(f"Error al procesar entrada unificada: {e}")
            return {}
    
    def process_episode_with_wordpress(self, rss_entry, wordpress_client) -> Dict:
        """
        Procesa un episodio del RSS y busca automáticamente sus datos de WordPress.
        
        Args:
            rss_entry: Objeto de entrada del feedparser
            wordpress_client: Cliente de WordPress para buscar datos
            
        Returns:
            Dict: Datos unificados del episodio
        """
        try:
            # Extraer slug de la URL del RSS
            rss_url = getattr(rss_entry, 'link', '') or rss_entry.get('link', '')
            slug = self.wordpress_processor.extract_slug_from_url(rss_url)
            
            if not slug:
                logger.warning(f"No se pudo extraer slug de la URL: {rss_url}")
                return self.process_entry(rss_entry, None)
            
            # Buscar datos de WordPress
            wordpress_data = wordpress_client.get_post_details_by_slug(slug)
            
            if wordpress_data:
                logger.info(f"Datos de WordPress encontrados para slug '{slug}'")
            else:
                logger.warning(f"No se encontraron datos de WordPress para slug '{slug}'")
            
            # Procesar y unificar
            return self.process_entry(rss_entry, wordpress_data)
            
        except Exception as e:
            logger.error(f"Error al procesar episodio con WordPress: {e}")
            return self.process_entry(rss_entry, None)
    
    def _process_rss_entry(self, rss_entry) -> Dict:
        """
        Procesa una entrada del RSS usando el procesador específico.
        
        Args:
            rss_entry: Objeto de entrada del feedparser
            
        Returns:
            Dict: Datos procesados del RSS
        """
        try:
            # Usar el procesador de RSS existente
            episode_data = self.rss_processor._process_single_entry(rss_entry)
            
            if episode_data:
                # Adaptar la estructura para la unificación
                return {
                    'guid': episode_data.get('entry_id', ''),
                    'title': episode_data.get('title', ''),
                    'link': episode_data.get('url', ''),
                    'published_date': episode_data.get('date', ''),
                    'summary': episode_data.get('rss_playlist', ''),
                    'download_url': episode_data.get('download_url', ''),
                    'file_size': episode_data.get('file_size'),
                    'duration': episode_data.get('duration'),
                    'image_url': episode_data.get('image_url', ''),
                    'program_number': episode_data.get('program_number'),
                    'comments': episode_data.get('comments', '')
                }
            else:
                # Fallback si el procesador de RSS falla
                return {
                    'guid': getattr(rss_entry, 'id', getattr(rss_entry, 'link', '')),
                    'title': getattr(rss_entry, 'title', ''),
                    'link': getattr(rss_entry, 'link', ''),
                    'published_date': getattr(rss_entry, 'published', ''),
                    'summary': getattr(rss_entry, 'summary', '')
                }
                
        except Exception as e:
            logger.error(f"Error al procesar entrada RSS: {e}")
            return {}
    
    def _unify_data(self, rss_data: Dict, wordpress_data: Dict) -> Dict:
        """
        Unifica los datos del RSS y WordPress en una estructura coherente.
        
        Args:
            rss_data: Datos procesados del RSS
            wordpress_data: Datos procesados de WordPress
            
        Returns:
            Dict: Datos unificados
        """
        # Empezar con los datos del RSS como base
        unified_data = rss_data.copy()
        
        # Añadir datos de WordPress si están disponibles
        if wordpress_data:
            # Campos básicos de WordPress
            unified_data.update({
                'wordpress_id': wordpress_data.get('wordpress_id'),
                'wordpress_title': wordpress_data.get('title', ''),
                'wordpress_content': wordpress_data.get('content', ''),
                'wordpress_excerpt': wordpress_data.get('excerpt', ''),
                'wordpress_slug': wordpress_data.get('slug', ''),
                'wordpress_date': wordpress_data.get('date'),
                'wordpress_modified': wordpress_data.get('modified'),
                'featured_image_url': wordpress_data.get('featured_image_url'),
                'wordpress_author': wordpress_data.get('author'),
                'wordpress_status': wordpress_data.get('status'),
                'wordpress_link': wordpress_data.get('link', ''),
                'wordpress_categories': wordpress_data.get('categories', []),
                'wordpress_tags': wordpress_data.get('tags', []),
                'wordpress_playlist_data': wordpress_data.get('playlist_data')
            })
            
            # Priorizar imagen destacada de WordPress si está disponible
            if wordpress_data.get('featured_image_url'):
                unified_data['featured_image_url'] = wordpress_data['featured_image_url']
        
        return unified_data
    
    def get_unified_episodes(self, wordpress_client, limit: Optional[int] = None) -> List[Dict]:
        """
        Obtiene episodios unificados del RSS y WordPress.
        
        Args:
            wordpress_client: Cliente de WordPress
            limit: Número máximo de episodios a procesar (None para todos)
            
        Returns:
            List[Dict]: Lista de episodios unificados
        """
        try:
            # Obtener entradas del RSS
            rss_entries = self.rss_processor.fetch_and_process_entries()
            
            if limit:
                rss_entries = rss_entries[:limit]
            
            logger.info(f"Procesando {len(rss_entries)} episodios con datos unificados")
            
            # Procesar cada episodio
            unified_episodes = []
            for entry in rss_entries:
                # Usar directamente los datos del RSS y buscar WordPress por número de programa
                unified_episode = self._unify_rss_with_wordpress(entry, wordpress_client)
                
                if unified_episode:
                    unified_episodes.append(unified_episode)
            
            logger.info(f"Procesados {len(unified_episodes)} episodios unificados")
            return unified_episodes
            
        except Exception as e:
            logger.error(f"Error al obtener episodios unificados: {e}")
            return []
    
    def process_single_episode(self, rss_episode: Dict, wordpress_client) -> Dict:
        """
        Procesa un episodio específico del RSS y lo unifica con datos de WordPress.
        
        Args:
            rss_episode: Datos del episodio del RSS
            wordpress_client: Cliente de WordPress
            
        Returns:
            Dict: Datos unificados del episodio
        """
        try:
            logger.info(f"Procesando episodio individual: {rss_episode.get('title', 'Sin título')}")
            unified_episode = self._unify_rss_with_wordpress(rss_episode, wordpress_client)
            
            if unified_episode:
                logger.info(f"Episodio procesado exitosamente: {unified_episode.get('title', 'Sin título')}")
                return unified_episode
            else:
                logger.warning(f"No se pudo procesar el episodio: {rss_episode.get('title', 'Sin título')}")
                return {}
                
        except Exception as e:
            logger.error(f"Error al procesar episodio individual: {e}")
            return {}
    
    def _unify_rss_with_wordpress(self, rss_entry: Dict, wordpress_client) -> Dict:
        """
        Unifica datos del RSS con WordPress usando el número de programa.
        
        Args:
            rss_entry: Datos del episodio del RSS
            wordpress_client: Cliente de WordPress
            
        Returns:
            Dict: Datos unificados
        """
        try:
            # Usar los datos del RSS como base
            unified_data = rss_entry.copy()
            
            # Asegurar que el campo guid esté presente
            if 'guid' not in unified_data:
                unified_data['guid'] = rss_entry.get('entry_id', '')
            
            # Intentar obtener datos de WordPress usando el número de programa
            program_number = rss_entry.get('program_number')
            if program_number:
                logger.info(f"Buscando datos de WordPress para programa {program_number}")
                
                # Extraer la fecha real del episodio del RSS
                published_date = rss_entry.get('date', '')
                if published_date:
                    # Convertir fecha ISO a formato YYYY-MM-DD
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
                        date = dt.strftime('%Y-%m-%d')
                        logger.info(f"Usando fecha del RSS: {date}")
                    except:
                        date = "2025-05-31"  # Fallback
                        logger.warning(f"No se pudo parsear fecha del RSS: {published_date}")
                else:
                    date = "2025-05-31"  # Fallback
                    logger.warning("No hay fecha disponible en el RSS")
                
                wordpress_data = wordpress_client.get_post_details_by_date_and_number(date, str(program_number))
                
                if wordpress_data:
                    logger.info(f"Datos de WordPress encontrados para programa {program_number}")
                    # Procesar datos de WordPress
                    wordpress_processed = self.wordpress_processor.process_post_data(wordpress_data)
                    
                    # Unificar con los datos del RSS
                    unified_data.update({
                        'wordpress_id': wordpress_processed.get('wordpress_id'),
                        'wordpress_title': wordpress_processed.get('title', ''),
                        'wordpress_content': wordpress_processed.get('content', ''),
                        'wordpress_excerpt': wordpress_processed.get('excerpt', ''),
                        'wordpress_slug': wordpress_processed.get('slug', ''),
                        'wordpress_date': wordpress_processed.get('date'),
                        'wordpress_modified': wordpress_processed.get('modified'),
                        'featured_image_url': wordpress_processed.get('featured_image_url'),
                        'wordpress_author': wordpress_processed.get('author'),
                        'wordpress_status': wordpress_processed.get('status'),
                        'wordpress_link': wordpress_processed.get('link', ''),
                        'wordpress_categories': wordpress_processed.get('categories', []),
                        'wordpress_tags': wordpress_processed.get('tags', []),
                        'wordpress_playlist_data': wordpress_processed.get('playlist_data'),
                        'web_extra_links': wordpress_processed.get('web_extra_links', []),
                        'content_length': wordpress_processed.get('content_length', 0)
                    })
                    
                    # Priorizar imagen destacada de WordPress si está disponible
                    if wordpress_processed.get('featured_image_url'):
                        unified_data['featured_image_url'] = wordpress_processed['featured_image_url']
                else:
                    logger.warning(f"No se encontraron datos de WordPress para programa {program_number}")
            
            return unified_data
            
        except Exception as e:
            logger.error(f"Error al unificar RSS con WordPress: {e}")
            return rss_entry


if __name__ == "__main__":
    """
    Bloque de prueba directa para el DataProcessor (orquestador).
    """
    try:
        from .config_manager import ConfigManager
        from .rss_reader import RSSReader
        from .wordpress_client import WordPressClient
        
        print("🧪 Iniciando prueba del DataProcessor (orquestador)...")
        print("-" * 60)
        
        # Crear instancias de todos los componentes
        config_manager = ConfigManager()
        
        # Procesadores específicos
        rss_processor = RSSDataProcessor(config_manager.get_rss_url())
        wordpress_processor = WordPressDataProcessor()
        
        # Cliente de WordPress
        wordpress_config = config_manager.get_wordpress_config()
        wordpress_client = WordPressClient(wordpress_config['api_url'])
        
        # Orquestador
        data_processor = DataProcessor(rss_processor, wordpress_processor)
        
        print("✅ Todos los componentes inicializados correctamente")
        
        # Procesar varios episodios para encontrar uno con datos de WordPress
        print("\n📡 Procesando episodios con datos unificados...")
        unified_episodes = data_processor.get_unified_episodes(wordpress_client, limit=5)
        
        if unified_episodes:
            print(f"\n📊 Episodios unificados procesados ({len(unified_episodes)}):")
            print("-" * 50)
            
            for i, episode in enumerate(unified_episodes, 1):
                print(f"\n{i}. {episode.get('title', 'Sin título')}")
                print(f"   Programa: {episode.get('program_number', 'N/A')}")
                
                # Verificar si tiene datos de WordPress
                wordpress_fields = [k for k in episode.keys() if k.startswith('wordpress_')]
                if wordpress_fields:
                    print(f"   ✅ Datos unificados (RSS + WordPress)")
                    if episode.get('featured_image_url'):
                        print(f"   🖼️  Imagen: {episode.get('featured_image_url')}")
                    if episode.get('wordpress_playlist_data', {}).get('songs_count'):
                        print(f"   🎵 Playlist: {episode.get('wordpress_playlist_data', {}).get('songs_count')} canciones")
                else:
                    print(f"   ⚠️  Solo RSS (WordPress no disponible para este programa)")
            
            # Mostrar estadísticas del primer episodio
            if unified_episodes:
                episode = unified_episodes[0]
                print(f"\n📈 Estadísticas del primer episodio:")
                print(f"  - Campos RSS: {len([k for k in episode.keys() if not k.startswith('wordpress_')])}")
                print(f"  - Campos WordPress: {len([k for k in episode.keys() if k.startswith('wordpress_')])}")
                print(f"  - Total campos: {len(episode)}")
            
        else:
            print("❌ No se pudieron procesar episodios unificados")
        
        print("\n✅ Prueba del orquestador completada exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        exit(1) 