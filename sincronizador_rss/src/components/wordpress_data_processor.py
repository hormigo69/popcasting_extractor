import urllib.parse
from typing import Dict, Optional, List
import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from utils.logger import logger


class WordPressDataProcessor:
    """
    Procesa los datos extraídos de la API de WordPress.
    """
    
    def __init__(self):
        """
        Inicializa el procesador de datos de WordPress.
        """
        logger.info("WordPressDataProcessor inicializado")
    
    def process_post_data(self, wordpress_data: Dict) -> Dict:
        """
        Procesa los datos de un post de WordPress.
        
        Args:
            wordpress_data: Datos del post obtenidos de la API de WordPress o extracción HTML
            
        Returns:
            Dict: Datos procesados del post
        """
        try:
            if not wordpress_data:
                logger.warning("No se proporcionaron datos de WordPress para procesar")
                return {}
            
            # Detectar el tipo de datos (API REST vs HTML)
            if isinstance(wordpress_data.get('title'), dict):
                # Formato API REST
                processed_data = {
                    'wordpress_id': wordpress_data.get('id'),
                    'title': wordpress_data.get('title', {}).get('rendered', ''),
                    'content': wordpress_data.get('content', {}).get('rendered', ''),
                    'excerpt': wordpress_data.get('excerpt', {}).get('rendered', ''),
                    'slug': wordpress_data.get('slug', ''),
                    'date': wordpress_data.get('date'),
                    'modified': wordpress_data.get('modified'),
                    'featured_image_url': wordpress_data.get('jetpack_featured_media_url'),
                    'author': wordpress_data.get('author'),
                    'status': wordpress_data.get('status'),
                    'link': wordpress_data.get('link', ''),
                    'categories': self._extract_categories(wordpress_data),
                    'tags': self._extract_tags(wordpress_data),
                    'playlist_data': self._extract_playlist_data(wordpress_data)
                }
            else:
                # Formato HTML (extracción directa)
                processed_data = {
                    'wordpress_id': None,  # No disponible en extracción HTML
                    'title': wordpress_data.get('title', ''),
                    'content': '',  # No extraído en HTML
                    'excerpt': '',  # No extraído en HTML
                    'slug': '',  # No disponible
                    'date': wordpress_data.get('date', ''),
                    'modified': None,
                    'featured_image_url': wordpress_data.get('cover_image_url', ''),
                    'author': None,
                    'status': None,
                    'link': wordpress_data.get('wordpress_url', ''),
                    'categories': [],
                    'tags': [],
                    'playlist_data': {
                        'raw_content': '',
                        'has_playlist': len(wordpress_data.get('web_playlist', [])) > 0,
                        'songs_count': len(wordpress_data.get('web_playlist', [])),
                        'songs': wordpress_data.get('web_playlist', [])
                    },
                    'web_extra_links': wordpress_data.get('web_extra_links', []),
                    'content_length': wordpress_data.get('content_length', 0)
                }
            
            logger.debug(f"Post de WordPress procesado: {processed_data.get('title', 'Sin título')}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error al procesar datos de WordPress: {e}")
            return {}
    
    def extract_slug_from_url(self, url: str) -> str:
        """
        Extrae el slug de una URL de WordPress.
        
        Args:
            url: URL completa del post
            
        Returns:
            str: Slug limpio extraído de la URL
        """
        try:
            # Parsear la URL
            parsed_url = urllib.parse.urlparse(url)
            
            # Obtener el path y limpiarlo
            path = parsed_url.path.strip('/')
            
            # Extraer solo el slug final (última parte después de la última barra)
            slug = path.split('/')[-1]
            
            logger.debug(f"URL: {url} -> Path completo: {path} -> Slug final: {slug}")
            return slug
            
        except Exception as e:
            logger.error(f"Error al extraer slug de URL '{url}': {e}")
            return ""
    
    def _extract_categories(self, wordpress_data: Dict) -> List[Dict]:
        """
        Extrae las categorías del post.
        
        Args:
            wordpress_data: Datos del post de WordPress
            
        Returns:
            List[Dict]: Lista de categorías con id y nombre
        """
        categories = []
        try:
            if '_embedded' in wordpress_data and 'wp:term' in wordpress_data['_embedded']:
                for term_group in wordpress_data['_embedded']['wp:term']:
                    for term in term_group:
                        if term.get('taxonomy') == 'category':
                            categories.append({
                                'id': term.get('id'),
                                'name': term.get('name'),
                                'slug': term.get('slug')
                            })
        except Exception as e:
            logger.warning(f"Error al extraer categorías: {e}")
        
        return categories
    
    def _extract_tags(self, wordpress_data: Dict) -> List[Dict]:
        """
        Extrae las etiquetas del post.
        
        Args:
            wordpress_data: Datos del post de WordPress
            
        Returns:
            List[Dict]: Lista de etiquetas con id y nombre
        """
        tags = []
        try:
            if '_embedded' in wordpress_data and 'wp:term' in wordpress_data['_embedded']:
                for term_group in wordpress_data['_embedded']['wp:term']:
                    for term in term_group:
                        if term.get('taxonomy') == 'post_tag':
                            tags.append({
                                'id': term.get('id'),
                                'name': term.get('name'),
                                'slug': term.get('slug')
                            })
        except Exception as e:
            logger.warning(f"Error al extraer etiquetas: {e}")
        
        return tags
    
    def _extract_playlist_data(self, wordpress_data: Dict) -> Optional[Dict]:
        """
        Extrae datos de playlist del contenido del post.
        
        Args:
            wordpress_data: Datos del post de WordPress
            
        Returns:
            Dict: Datos de playlist extraídos o None
        """
        try:
            content = wordpress_data.get('content', {}).get('rendered', '')
            if not content:
                return None
            
            # Aquí podrías implementar lógica específica para extraer playlist
            # Por ahora devolvemos un diccionario básico
            playlist_data = {
                'raw_content': content,
                'has_playlist': 'playlist' in content.lower() or 'canciones' in content.lower()
            }
            
            return playlist_data
            
        except Exception as e:
            logger.warning(f"Error al extraer datos de playlist: {e}")
            return None
    
    def validate_post_data(self, wordpress_data: Dict) -> bool:
        """
        Valida que los datos del post sean válidos.
        
        Args:
            wordpress_data: Datos del post de WordPress
            
        Returns:
            bool: True si los datos son válidos, False en caso contrario
        """
        if not wordpress_data:
            return False
        
        # Detectar el tipo de datos
        if isinstance(wordpress_data.get('title'), dict):
            # Formato API REST
            required_fields = ['id', 'title', 'link']
        else:
            # Formato HTML
            required_fields = ['title', 'wordpress_url']
        
        for field in required_fields:
            if field not in wordpress_data:
                logger.warning(f"Campo requerido '{field}' no encontrado en datos de WordPress")
                return False
        
        return True


if __name__ == "__main__":
    """
    Bloque de prueba directa para el WordPressDataProcessor.
    """
    try:
        from .wordpress_client import WordPressClient
        from .config_manager import ConfigManager
        
        # Crear instancias
        config_manager = ConfigManager()
        wordpress_config = config_manager.get_wordpress_config()
        wordpress_client = WordPressClient(wordpress_config['api_url'])
        wordpress_processor = WordPressDataProcessor()
        
        logger.info("Prueba WordPressDataProcessor iniciada")
        
        # URL de ejemplo para extraer slug
        test_url = "https://popcastingpop.com/2025/05/31/popcasting-479/"
        slug = wordpress_processor.extract_slug_from_url(test_url)
        
        # Extraer fecha y número del programa del slug
        import re
        match = re.search(r'popcasting-(\d+)', slug)
        if match:
            chapter_number = match.group(1)
            date = "2025-05-31"  # Fecha de ejemplo
            
            # Obtener datos de WordPress usando el método HTML
            wordpress_data = wordpress_client.get_post_details_by_date_and_number(date, chapter_number)
        else:
            logger.warning(f"No se pudo extraer número de capítulo del slug: {slug}")
            wordpress_data = None
        
        if wordpress_data:
            # Procesar los datos
            processed_data = wordpress_processor.process_post_data(wordpress_data)
            logger.info(f"Prueba WordPressDataProcessor exitosa: datos procesados para capítulo {chapter_number}")
        else:
            logger.warning("No se encontraron datos de WordPress para el slug")
        
        logger.info("Prueba WordPressDataProcessor completada")
        
    except Exception as e:
        logger.error(f"Error durante la prueba WordPressDataProcessor: {e}")
        import traceback
        traceback.print_exc()
        exit(1) 