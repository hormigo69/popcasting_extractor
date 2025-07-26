#!/usr/bin/env python3
"""
Procesador de datos RSS para el sincronizador.
"""

import feedparser
from datetime import datetime
import re
import json
from typing import Dict, List, Optional
import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from utils.logger import logger


class RSSDataProcessor:
    """
    Procesa los datos extraídos del RSS y los prepara para la base de datos.
    """
    
    def __init__(self, feed_url: str):
        """
        Inicializa el procesador con la URL del feed RSS.
        
        Args:
            feed_url (str): URL del feed RSS
        """
        self.feed_url = feed_url
        logger.info(f"RSSDataProcessor inicializado con URL: {feed_url}")
    
    def fetch_and_process_entries(self) -> List[Dict]:
        """
        Descarga el feed RSS y procesa todas las entradas.
        
        Returns:
            List[Dict]: Lista de episodios procesados para la BD
        """
        try:
            logger.info(f"Descargando y procesando feed RSS desde: {self.feed_url}")
            
            # Parsear el feed
            feed = feedparser.parse(self.feed_url)
            
            if not feed.entries:
                logger.warning("No se encontraron entradas en el feed RSS")
                return []
            
            logger.info(f"Procesando {len(feed.entries)} entradas del RSS")
            
            # Procesar cada entrada
            processed_episodes = []
            for entry in feed.entries:
                episode_data = self._process_single_entry(entry)
                if episode_data:
                    processed_episodes.append(episode_data)
            
            logger.info(f"Procesados {len(processed_episodes)} episodios exitosamente")
            return processed_episodes
            
        except Exception as e:
            error_msg = f"Error al procesar el feed RSS: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
    
    def _process_single_entry(self, entry) -> Optional[Dict]:
        """
        Procesa una entrada individual del RSS.
        
        Args:
            entry: Entrada del RSS parseada por feedparser
            
        Returns:
            Dict: Datos del episodio procesados para la BD
        """
        try:
            # Extraer campos básicos
            title = entry.get('title', '').strip()
            if not title:
                logger.warning("Entrada sin título, saltando...")
                return None
            
            # Extraer URL del episodio
            url = entry.get('link', '').strip()
            
            # Extraer fecha y convertirla
            published_date = self._parse_date(entry.get('published', ''))
            
            # Extraer datos del archivo de audio
            download_url, file_size = self._extract_audio_data(entry)
            
            # Extraer y procesar playlist del RSS
            raw_rss_playlist = entry.get('summary', '').strip()
            rss_playlist = self._process_rss_playlist(raw_rss_playlist)
            
            # Extraer duración
            duration = self._parse_duration(entry.get('itunes_duration', ''))
            
            # Extraer ID único
            entry_id = entry.get('id', '').strip()
            
            # Extraer URL de imagen
            image_url = self._extract_image_url(entry)
            
            # Crear estructura de datos para la BD
            episode_data = {
                'title': title,
                'date': published_date,
                'url': url,
                'download_url': download_url,
                'file_size': file_size,
                'rss_playlist': rss_playlist,
                'duration': duration,
                'entry_id': entry_id,
                'image_url': image_url,
                'program_number': self._extract_program_number(title),
                'comments': self._extract_comments(title)
            }
            
            logger.debug(f"Episodio procesado: {title}")
            return episode_data
            
        except Exception as e:
            logger.error(f"Error al procesar entrada '{entry.get('title', 'Sin título')}': {str(e)}")
            return None
    
    def _process_rss_playlist(self, playlist_text: str) -> str:
        """
        Procesa la playlist del RSS y la convierte a formato JSON.
        
        Args:
            playlist_text (str): Texto de la playlist del RSS
            
        Returns:
            str: JSON string con la playlist procesada
        """
        try:
            if not playlist_text:
                return json.dumps([], ensure_ascii=False)
            
            # 1. Limpieza inicial: eliminar texto extra como Ko-fi
            cleaned_text = self._clean_playlist_text(playlist_text)
            
            if not cleaned_text:
                return json.dumps([], ensure_ascii=False)
            
            # 2. División por canciones usando ::
            songs_raw = [song.strip() for song in cleaned_text.split('::') if song.strip()]
            
            # 3. Procesar cada canción
            processed_songs = []
            for i, song_raw in enumerate(songs_raw):
                song_data = self._parse_song_text(song_raw)
                if song_data:
                    # Limpiar campos problemáticos como 'duration'
                    cleaned_song = {
                        'position': i + 1,
                        'artist': song_data['artist'],
                        'title': song_data['title']
                    }
                    # Remover campos problemáticos si existen (prevención)
                    problematic_fields = ['duration', 'duration_ms', 'duration_seconds']
                    for field in problematic_fields:
                        if field in cleaned_song:
                            del cleaned_song[field]
                    processed_songs.append(cleaned_song)
            
            # 4. Convertir a JSON
            return json.dumps(processed_songs, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error al procesar playlist del RSS: {e}")
            # En caso de error, devolver playlist vacía
            return json.dumps([], ensure_ascii=False)
    
    def _clean_playlist_text(self, text: str) -> str:
        """
        Limpia el texto de la playlist eliminando contenido extra.
        
        Args:
            text (str): Texto original de la playlist
            
        Returns:
            str: Texto limpio
        """
        if not text:
            return ""
        
        # Eliminar texto de Ko-fi y otros patrones comunes
        patterns_to_remove = [
            r'::::::\s*invita a Popcasting a café\s*https://ko-fi\.com/popcasting.*',
            r'::::::\s*invita a Popcasting a café.*',
            r'https://ko-fi\.com/popcasting.*',
            r'@rss_data_processor\.py.*',
            r'@.*\.py.*',
        ]
        
        cleaned_text = text
        for pattern in patterns_to_remove:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)
        
        # Limpiar espacios extra y líneas vacías
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
    
    def _parse_song_text(self, text: str) -> Optional[Dict[str, str]]:
        """
        Parsea el texto de una canción para extraer artista y título.
        
        Args:
            text (str): Texto de la canción (formato: "artista · título")
            
        Returns:
            Dict: Diccionario con 'artist' y 'title' o None si no se puede parsear
        """
        if not text:
            return None
        
        # Patrones para extraer artista y título
        patterns = [
            r'^(.+?)\s*·\s*(.+)$',  # Artista · Título (formato principal de Popcasting)
            r'^(.+?)\s*[-–—]\s*(.+)$',  # Artista - Título
            r'^(.+?)\s*:\s*(.+)$',  # Artista: Título
            r'^(.+?)\s*"\s*(.+?)\s*"$',  # Artista "Título"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text.strip())
            if match:
                artist = match.group(1).strip()
                title = match.group(2).strip()
                
                # Validar que tanto artista como título tengan contenido válido
                if (len(artist) > 1 and len(title) > 1 and 
                    not any(word in artist.lower() for word in [
                        'comentarios', 'compartir', 'twitter', 'facebook', 
                        'popcasting', 'ko-fi', 'invita'
                    ])):
                    return {
                        'artist': artist,
                        'title': title
                    }
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parsea la fecha del RSS a formato ISO.
        
        Args:
            date_str (str): Fecha en formato RSS
            
        Returns:
            str: Fecha en formato ISO o None si no se puede parsear
        """
        if not date_str:
            return None
        
        try:
            # Intentar parsear con feedparser
            parsed_time = feedparser._parse_date(date_str)
            if parsed_time:
                return datetime(*parsed_time[:6]).isoformat()
        except:
            pass
        
        try:
            # Fallback: intentar parsear manualmente
            dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
            return dt.isoformat()
        except:
            logger.warning(f"No se pudo parsear la fecha: {date_str}")
            return None
    
    def _extract_audio_data(self, entry) -> tuple:
        """
        Extrae los datos del archivo de audio desde enclosures.
        
        Args:
            entry: Entrada del RSS
            
        Returns:
            tuple: (download_url, file_size)
        """
        download_url = None
        file_size = None
        
        if 'enclosures' in entry and entry['enclosures']:
            enclosure = entry['enclosures'][0]
            download_url = enclosure.get('href', '').strip()
            file_size_str = enclosure.get('length', '')
            
            if file_size_str and file_size_str.isdigit():
                file_size = int(file_size_str)
        
        return download_url, file_size
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """
        Convierte la duración de formato HH:MM:SS a segundos.
        
        Args:
            duration_str (str): Duración en formato "HH:MM:SS"
            
        Returns:
            int: Duración en segundos o None si no se puede parsear
        """
        if not duration_str:
            return None
        
        try:
            # Formato: "01:51:12"
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                # Formato: "MM:SS"
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
        except:
            logger.warning(f"No se pudo parsear la duración: {duration_str}")
        
        return None
    
    def _extract_image_url(self, entry) -> Optional[str]:
        """
        Extrae la URL de la imagen del episodio.
        
        Args:
            entry: Entrada del RSS
            
        Returns:
            str: URL de la imagen o None
        """
        if 'image' in entry:
            return entry['image'].get('href', '').strip()
        return None
    
    def _extract_program_number(self, title: str) -> Optional[int]:
        """
        Extrae el número del programa desde el título.
        
        Args:
            title (str): Título del episodio
            
        Returns:
            int: Número del programa o None si no se puede extraer
        """
        # Buscar patrones como "Popcasting485", "Popcasting 484", etc.
        patterns = [
            r'popcasting\s*(\d+)',  # Popcasting485, Popcasting 484
            r'(\d+)$',              # Número al final
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title.lower())
            if match:
                try:
                    return int(match.group(1))
                except:
                    continue
        
        return None
    
    def _extract_comments(self, title: str) -> Optional[str]:
        """
        Extrae los comentarios desde el título (texto después del número).
        
        Args:
            title (str): Título del episodio
            
        Returns:
            str: Comentarios extraídos o None si no hay comentarios
        """
        # Patrones para extraer comentarios
        patterns = [
            r'popcasting\s*\d+\s*\(([^)]+)\)',  # Popcasting195 (especial Smash Hits 1984)
            r'popcasting\s*\d+\s+(.+)$',        # Popcasting195 especial Smash Hits 1984
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                comments = match.group(1).strip()
                if comments:
                    return comments
        
        return None
    
    def get_episode_by_title(self, title: str) -> Optional[Dict]:
        """
        Busca un episodio específico por título.
        
        Args:
            title (str): Título del episodio a buscar
            
        Returns:
            Dict: Datos del episodio o None si no se encuentra
        """
        episodes = self.fetch_and_process_entries()
        
        for episode in episodes:
            if episode['title'].lower() == title.lower():
                return episode
        
        return None


if __name__ == "__main__":
    """
    Punto de entrada para pruebas del procesador RSS.
    """
    import sys
    
    # URL de ejemplo
    test_url = "https://feeds.feedburner.com/popcasting"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    try:
        processor = RSSDataProcessor(test_url)
        
        # Procesar todas las entradas
        episodes = processor.fetch_and_process_entries()
        
        logger.info(f"Prueba RSSDataProcessor exitosa: {len(episodes)} episodios procesados")
        
    except Exception as e:
        logger.error(f"Error durante la prueba RSSDataProcessor: {e}")
        sys.exit(1) 