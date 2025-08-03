"""
Componente especializado para el procesamiento de canciones.
Maneja la conversión de playlists del RSS y web, y su almacenamiento en la base de datos.
"""

import json
import logging
import re
from typing import List, Dict, Optional


class SongProcessor:
    """
    Procesador especializado para manejar canciones de podcasts.
    
    Responsabilidades:
    - Parsear playlists del RSS a formato JSON estructurado
    - Decidir qué playlist usar (web vs RSS)
    - Almacenar canciones en la base de datos
    - Validar y limpiar datos de canciones
    """
    
    def __init__(self, database_manager):
        """
        Inicializa el procesador de canciones.
        
        Args:
            database_manager: Instancia de DatabaseManager para operaciones de BD
        """
        self.db_manager = database_manager
        self.logger = logging.getLogger(__name__)
    
    def _parse_rss_playlist_string(self, playlist_text: str) -> List[Dict]:
        """
        Convierte el texto de la playlist del RSS a una lista de diccionarios JSON.
        
        Args:
            playlist_text: Texto de la playlist del RSS
            
        Returns:
            Lista de diccionarios con estructura: [{"position": int, "artist": str, "title": str}]
        """
        try:
            if not playlist_text:
                return []
            
            # 1. Limpieza inicial: eliminar texto extra como Ko-fi
            cleaned_text = self._clean_playlist_text(playlist_text)
            
            if not cleaned_text:
                return []
            
            # 2. División por canciones usando ::
            songs_raw = [song.strip() for song in cleaned_text.split('::') if song.strip()]
            
            # 3. Procesar cada canción
            processed_songs = []
            for i, song_raw in enumerate(songs_raw):
                song_data = self._parse_song_text(song_raw)
                if song_data:
                    processed_songs.append({
                        'position': i + 1,
                        'artist': song_data['artist'],
                        'title': song_data['title']
                    })
            
            self.logger.debug(f"Playlist RSS procesada: {len(processed_songs)} canciones")
            return processed_songs
            
        except Exception as e:
            self.logger.error(f"Error al procesar playlist del RSS: {e}")
            return []
    
    def _clean_playlist_text(self, playlist_text: str) -> str:
        """
        Limpia el texto de la playlist eliminando contenido no deseado.
        
        Args:
            playlist_text: Texto original de la playlist
            
        Returns:
            Texto limpio para procesamiento
        """
        if not playlist_text:
            return ""
        
        # Eliminar texto de Ko-fi y otros patrones no deseados
        patterns_to_remove = [
            r"::::::\s*invita a Popcasting a café\s*https://ko-fi\.com/popcasting.*$",
            r"@rss_data_processor\.py.*$",
            r"https?://[^\s]+",
            r"invita a popcasting.*$",
            r"flor de pasión.*$",
            r"my favourite.*$",
            r"las felindras.*$",
            r"revisionist history.*$",
            r"ko-fi\.com.*$",
            r"youtu\.be.*$",
        ]
        
        cleaned_text = playlist_text
        for pattern in patterns_to_remove:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)
        
        # Limpiar espacios extra y líneas vacías
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
    
    def _parse_song_text(self, song_raw: str) -> Optional[Dict]:
        """
        Parsea el texto de una canción individual para extraer artista y título.
        
        Args:
            song_raw: Texto de la canción (ej: "the beatles · rain")
            
        Returns:
            Diccionario con 'artist' y 'title' o None si no es válido
        """
        if not song_raw or len(song_raw.strip()) < 3:
            return None
        
        # Limpiar el texto
        song_raw = song_raw.strip()
        
        # Buscar separadores comunes
        separators = [' · ', ' • ', ' - ', ': ', ' "', '" ']
        
        for separator in separators:
            if separator in song_raw:
                parts = song_raw.split(separator, 1)
                if len(parts) == 2:
                    artist = parts[0].strip()
                    title = parts[1].strip()
                    
                    # Validar que ambos campos tengan contenido
                    if (len(artist) >= 2 and len(title) >= 2 and 
                        len(artist) < 100 and len(title) < 100):
                        return {
                            'artist': artist,
                            'title': title
                        }
        
        # Si no se encontró separador válido, considerar todo como título
        if len(song_raw) >= 2 and len(song_raw) < 100:
            return {
                'artist': 'Unknown',
                'title': song_raw
            }
        
        return None
    
    def process_and_store_songs(self, podcast_id: int, web_playlist: Optional[List[Dict]] = None, 
                               rss_playlist: Optional[str] = None) -> int:
        """
        Procesa y almacena las canciones de un podcast.
        
        Args:
            podcast_id: ID del podcast
            web_playlist: Lista de canciones de la web (opcional)
            rss_playlist: Texto de la playlist del RSS (opcional)
            
        Returns:
            Número de canciones almacenadas
        """
        try:
            # Decidir qué playlist usar (priorizando web_playlist si existe)
            songs_to_store = []
            
            if web_playlist:
                # Manejar tanto listas como strings JSON
                if isinstance(web_playlist, list):
                    self.logger.info(f"Usando playlist web (lista) para podcast {podcast_id}")
                    songs_to_store = web_playlist
                elif isinstance(web_playlist, str):
                    # Intentar parsear como JSON
                    try:
                        import json
                        parsed_playlist = json.loads(web_playlist)
                        if isinstance(parsed_playlist, list):
                            self.logger.info(f"Usando playlist web (JSON parseado) para podcast {podcast_id}")
                            songs_to_store = parsed_playlist
                        else:
                            self.logger.warning(f"Playlist web parseada no es una lista: {type(parsed_playlist)}")
                            songs_to_store = []
                    except json.JSONDecodeError:
                        self.logger.warning(f"No se pudo parsear playlist web como JSON: {web_playlist[:100]}...")
                        songs_to_store = []
                else:
                    self.logger.warning(f"Formato de playlist web no reconocido: {type(web_playlist)}")
                    songs_to_store = []
            elif rss_playlist and isinstance(rss_playlist, str):
                self.logger.info(f"Usando playlist RSS para podcast {podcast_id}")
                songs_to_store = self._parse_rss_playlist_string(rss_playlist)
            else:
                self.logger.warning(f"No hay playlist disponible para podcast {podcast_id}")
                return 0
            
            if not songs_to_store:
                self.logger.warning(f"No se encontraron canciones válidas para podcast {podcast_id}")
                return 0
            
            # Añadir el podcast_id a cada canción
            songs_with_podcast_id = []
            for song in songs_to_store:
                song_copy = song.copy()
                song_copy['podcast_id'] = podcast_id
                songs_with_podcast_id.append(song_copy)
            
            # Eliminar canciones existentes para este podcast antes de insertar nuevas
            self.logger.info(f"Limpiando canciones existentes para podcast {podcast_id}")
            self.db_manager.delete_songs_by_podcast_id(podcast_id)
            
            # Almacenar en la base de datos
            stored_count = self.db_manager.insert_songs_batch(songs_with_podcast_id)
            
            self.logger.info(f"Almacenadas {stored_count} canciones para el podcast {podcast_id}")
            return stored_count
            
        except Exception as e:
            self.logger.error(f"Error procesando canciones para podcast {podcast_id}: {e}")
            return 0
    
    def validate_song_data(self, song: Dict) -> bool:
        """
        Valida que los datos de una canción sean correctos.
        
        Args:
            song: Diccionario con datos de la canción
            
        Returns:
            True si los datos son válidos, False en caso contrario
        """
        required_fields = ['artist', 'title']
        
        # Verificar campos requeridos
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
            if re.search(pattern, text_to_check):
                return False
        
        return True 