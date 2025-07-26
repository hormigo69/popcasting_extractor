"""
Componente especializado para el procesamiento de canciones en el sincronizador RSS.
Maneja la decisión de qué playlist usar y el almacenamiento en la tabla songs.
"""

import json
import logging
from typing import List, Dict, Optional


class SongProcessor:
    """
    Procesador especializado para manejar canciones de podcasts.
    
    Responsabilidades:
    - Decidir qué playlist usar (web vs RSS)
    - Almacenar canciones en la tabla songs
    - Validar datos de canciones antes del almacenamiento
    
    Nota: El parseo de playlists ya se hace en RSSDataProcessor y WordPressDataProcessor.
    """
    
    def __init__(self, database_manager):
        """
        Inicializa el procesador de canciones.
        
        Args:
            database_manager: Instancia de DatabaseManager para operaciones de BD
        """
        self.db_manager = database_manager
        self.logger = logging.getLogger(__name__)
    
    def process_and_store_songs(self, podcast_id: int, web_playlist: Optional[str] = None, 
                               rss_playlist: Optional[str] = None) -> int:
        """
        Procesa y almacena las canciones de un podcast.
        
        Args:
            podcast_id: ID del podcast
            web_playlist: JSON string con playlist de la web (ya procesada por WordPressDataProcessor)
            rss_playlist: JSON string con playlist del RSS (ya procesada por RSSDataProcessor)
            
        Returns:
            Número de canciones almacenadas
        """
        try:
            # Decidir qué playlist usar (priorizando web_playlist si existe)
            songs_to_store = []
            
            if web_playlist and isinstance(web_playlist, str):
                self.logger.info(f"Usando playlist web para podcast {podcast_id}")
                songs_to_store = self._parse_json_playlist(web_playlist)
            elif rss_playlist and isinstance(rss_playlist, str):
                self.logger.info(f"Usando playlist RSS para podcast {podcast_id}")
                songs_to_store = self._parse_json_playlist(rss_playlist)
            else:
                self.logger.warning(f"No hay playlist disponible para podcast {podcast_id}")
                return 0
            
            if not songs_to_store:
                self.logger.warning(f"No se encontraron canciones válidas para podcast {podcast_id}")
                return 0
            
            # Validar y limpiar canciones
            valid_songs = []
            for song in songs_to_store:
                if self._validate_song_data(song):
                    valid_songs.append(song)
                else:
                    self.logger.warning(f"Canción omitida por datos inválidos: {song}")
            
            if not valid_songs:
                self.logger.warning(f"No hay canciones válidas para almacenar en podcast {podcast_id}")
                return 0
            
            # Añadir el podcast_id a cada canción
            songs_with_podcast_id = []
            for song in valid_songs:
                song_copy = song.copy()
                song_copy['podcast_id'] = podcast_id
                songs_with_podcast_id.append(song_copy)
            
            # Almacenar en la base de datos
            stored_count = self.db_manager.insert_songs_batch(songs_with_podcast_id)
            
            self.logger.info(f"Almacenadas {stored_count} canciones para el podcast {podcast_id}")
            return stored_count
            
        except Exception as e:
            self.logger.error(f"Error procesando canciones para podcast {podcast_id}: {e}")
            return 0
    
    def _parse_json_playlist(self, playlist_json: str) -> List[Dict]:
        """
        Parsea una playlist en formato JSON string a lista de diccionarios.
        
        Args:
            playlist_json: JSON string con la playlist
            
        Returns:
            Lista de diccionarios con canciones
        """
        try:
            if not playlist_json:
                return []
            
            parsed_data = json.loads(playlist_json)
            
            if isinstance(parsed_data, list):
                return parsed_data
            elif isinstance(parsed_data, dict) and 'songs' in parsed_data:
                return parsed_data['songs']
            else:
                self.logger.warning(f"Formato de playlist JSON no reconocido: {type(parsed_data)}")
                return []
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Error al parsear JSON de playlist: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error inesperado al parsear playlist: {e}")
            return []
    
    def _validate_song_data(self, song: Dict) -> bool:
        """
        Valida que los datos de una canción sean correctos.
        
        Args:
            song: Diccionario con datos de la canción
            
        Returns:
            True si los datos son válidos, False en caso contrario
        """
        try:
            # Verificar campos requeridos
            required_fields = ['artist', 'title']
            for field in required_fields:
                if field not in song or not song[field]:
                    return False
            
            # Verificar longitudes
            if (len(song['artist']) < 2 or len(song['artist']) > 100 or
                len(song['title']) < 2 or len(song['title']) > 100):
                return False
            
            # Verificar que no contengan URLs o texto no deseado
            invalid_patterns = [
                r'http[s]?://',
                r'www\.',
                r'\.com',
                r'\.org',
                r'\.net',
                r'popcasting',
                r'ivoox',
                r'wordpress',
                r'podcast'
            ]
            
            text_to_check = f"{song['artist']} {song['title']}".lower()
            for pattern in invalid_patterns:
                if pattern in text_to_check:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando canción: {e}")
            return False
    
    def get_playlist_info(self, web_playlist: Optional[str] = None, 
                         rss_playlist: Optional[str] = None) -> Dict:
        """
        Obtiene información sobre las playlists disponibles.
        
        Args:
            web_playlist: JSON string con playlist de la web
            rss_playlist: JSON string con playlist del RSS
            
        Returns:
            Diccionario con información de las playlists
        """
        info = {
            'web_playlist_count': 0,
            'rss_playlist_count': 0,
            'selected_playlist': None,
            'selected_count': 0
        }
        
        try:
            if web_playlist:
                web_songs = self._parse_json_playlist(web_playlist)
                info['web_playlist_count'] = len(web_songs)
                info['selected_playlist'] = 'web'
                info['selected_count'] = len(web_songs)
            elif rss_playlist:
                rss_songs = self._parse_json_playlist(rss_playlist)
                info['rss_playlist_count'] = len(rss_songs)
                info['selected_playlist'] = 'rss'
                info['selected_count'] = len(rss_songs)
                
        except Exception as e:
            self.logger.error(f"Error obteniendo información de playlists: {e}")
        
        return info 