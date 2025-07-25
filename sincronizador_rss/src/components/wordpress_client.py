import requests
import sys
import os
import json
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path

# Agregar el directorio src al path para importaciones
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from utils.logger import logger


class WordPressClient:
    def __init__(self, api_url: str):
        """
        Inicializa el cliente de WordPress.
        
        Args:
            api_url: URL base de la API de WordPress (ej: https://popcastingpop.com/wp-json/wp/v2/)
        """
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def get_post_details_by_slug(self, slug: str) -> dict | None:
        """
        Busca un post en WordPress por su slug.
        
        Args:
            slug: El slug del post a buscar
            
        Returns:
            dict: Datos del post si se encuentra, None si no se encuentra o hay error
        """
        try:
            # Construir la URL de la API
            url = f"{self.api_url}/posts"
            params = {
                "slug": slug,
                "_embed": 1  # Incluir datos embebidos como imágenes
            }
            
            # Hacer la petición
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Procesar la respuesta
            posts = response.json()
            
            if posts and len(posts) > 0:
                logger.info(f"Post encontrado con slug '{slug}'")
                return posts[0]  # Devolver el primer post encontrado
            else:
                logger.warning(f"No se encontró post con slug '{slug}'")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión al buscar post '{slug}': {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al buscar post '{slug}': {e}")
            return None

    def get_post_details_by_date_and_number(self, date: str, chapter_number: str) -> dict | None:
        """
        Busca un post en WordPress por fecha y número de capítulo.
        
        Args:
            date: Fecha en formato YYYY-MM-DD
            chapter_number: Número del capítulo
            
        Returns:
            dict: Datos del post si se encuentra, None si no se encuentra o hay error
        """
        try:
            # Construir la URL completa del sitio web con la fecha
            date_parts = date.split('-')
            if len(date_parts) != 3:
                logger.error(f"Formato de fecha inválido: {date}. Debe ser YYYY-MM-DD")
                return None
                
            year, month, day = date_parts
            formatted_date = f"{year}/{month}/{day}"
            
            # Construir la URL completa del sitio web
            base_url = self.api_url.replace('/wp-json/wp/v2', '')  # Obtener la URL base
            full_url = f"{base_url}/{formatted_date}/popcasting-{chapter_number}/"
            
            logger.info(f"Buscando post en URL: {full_url}")
            
            # Hacer la petición a la página web
            response = self.session.get(full_url, timeout=10)
            response.raise_for_status()
            
            # Verificar que la página existe y contiene el contenido esperado
            if response.status_code == 200:
                logger.info(f"Post encontrado en URL: {full_url}")
                
                # Extraer información detallada de la página
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraer campos según la estructura de la BD
                extracted_data = {
                    "wordpress_url": full_url,
                    "cover_image_url": self._extract_cover_image(soup, full_url),
                    "web_extra_links": self._extract_extra_links(soup),
                    "web_playlist": self._extract_playlist(soup),
                    "content_length": len(response.content),
                    "title": self._extract_title(soup),
                    "date": date
                }
                
                logger.info(f"Extraídos {len(extracted_data['web_playlist'])} canciones de la playlist")
                logger.info(f"Extraídos {len(extracted_data['web_extra_links'])} enlaces adicionales")
                
                return extracted_data
            else:
                logger.warning(f"No se encontró post en URL: {full_url}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión al buscar post en URL: {full_url if 'full_url' in locals() else 'URL no construida'}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al buscar post: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrae el título del post."""
        title_elem = soup.find('title')
        if title_elem:
            return title_elem.get_text(strip=True)
        return "Sin título"

    def _extract_cover_image(self, soup: BeautifulSoup, base_url: str) -> str | None:
        """Extrae la URL de la imagen de portada."""
        # Buscar imágenes con el patrón específico de Popcasting
        # Las imágenes tienen data-orig-file con la URL completa
        images = soup.find_all('img', attrs={'data-orig-file': True})
        
        for img in images:
            orig_file = img.get('data-orig-file')
            if orig_file and 'wp-content/uploads' in orig_file:
                logger.info(f"Imagen encontrada: {orig_file}")
                return orig_file
        
        # Fallback: buscar cualquier imagen con wp-content/uploads
        images = soup.find_all('img')
        for img in images:
            src = img.get('src')
            if src and 'wp-content/uploads' in src:
                logger.info(f"Imagen encontrada (fallback): {src}")
                return urljoin(base_url, src)
        
        logger.warning("No se encontró imagen de portada")
        return None

    def _extract_extra_links(self, soup: BeautifulSoup) -> list[dict]:
        """Extrae enlaces adicionales del post."""
        extra_links = []
        
        # Buscar spans con el color específico de Popcasting (#ff99cc)
        colored_spans = soup.find_all('span', style=lambda x: x and '#ff99cc' in x)
        
        for span in colored_spans:
            links = span.find_all('a', href=True)
            for link in links:
                text = link.get_text(strip=True)
                url = link.get('href')
                
                # Filtrar enlaces de Ko-fi
                if text and url and 'ko-fi.com/popcasting' not in url:
                    extra_links.append({"text": text, "url": url})
                    logger.info(f"Enlace adicional encontrado: {text} -> {url}")
                elif 'ko-fi.com/popcasting' in url:
                    logger.info(f"Enlace de Ko-fi filtrado: {text} -> {url}")
        
        # También buscar en párrafos centrados que pueden contener enlaces
        centered_paragraphs = soup.find_all('p', class_='has-text-align-center')
        for p in centered_paragraphs:
            links = p.find_all('a', href=True)
            for link in links:
                text = link.get_text(strip=True)
                url = link.get('href')
                
                # Filtrar enlaces de Ko-fi y duplicados
                if (text and url and 
                    'ko-fi.com/popcasting' not in url and 
                    not any(existing['url'] == url for existing in extra_links)):
                    extra_links.append({"text": text, "url": url})
                    logger.info(f"Enlace adicional encontrado (centrado): {text} -> {url}")
                elif 'ko-fi.com/popcasting' in url:
                    logger.info(f"Enlace de Ko-fi filtrado (centrado): {text} -> {url}")
        
        return extra_links

    def _extract_playlist(self, soup: BeautifulSoup) -> list[dict]:
        """Extrae la playlist del post."""
        playlist = []
        
        # Buscar en el contenido principal (como en web_extractor.py)
        content_area = (
            soup.find("div", class_="entry-content")
            or soup.find("article")
            or soup.find("div", class_="entrybody")  # Para episodios antiguos
        )
        
        if content_area:
            # Primero buscar párrafos centrados (formato moderno)
            centered_paragraphs = content_area.find_all('p', style=lambda x: x and 'text-align: center' in x)
            
            position = 1
            for p in centered_paragraphs:
                text = p.get_text(strip=True)
                
                # Buscar canciones en el texto del párrafo
                songs = self._parse_popcasting_playlist_text(text)
                if songs:
                    for song in songs:
                        if self._is_valid_song(song):
                            playlist.append({
                                "position": position,
                                "artist": song["artist"],
                                "title": song["title"]
                            })
                            position += 1
                            logger.info(f"Canción encontrada: {song['artist']} - {song['title']}")
            
            # Si no encontramos en párrafos centrados, buscar en listas (fallback)
            if not playlist:
                lists = content_area.find_all(["ol", "ul"])
                
                for list_elem in lists:
                    items = list_elem.find_all("li")
                    for i, item in enumerate(items):
                        text = item.get_text(strip=True)
                        song_info = self._parse_song_text(text)
                        if song_info and self._is_valid_song(song_info):
                            playlist.append({
                                "position": i + 1,
                                "artist": song_info["artist"],
                                "title": song_info["title"]
                            })
                            logger.info(f"Canción encontrada (lista): {song_info['artist']} - {song_info['title']}")
            
            # Si aún no encontramos, buscar en párrafos generales
            if not playlist:
                paragraphs = content_area.find_all("p")
                position = 1
                
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    songs = self._parse_popcasting_playlist_text(text)
                    if songs:
                        for song in songs:
                            if self._is_valid_song(song):
                                playlist.append({
                                    "position": position,
                                    "artist": song["artist"],
                                    "title": song["title"]
                                })
                                position += 1
                                logger.info(f"Canción encontrada (párrafo): {song['artist']} - {song['title']}")
                    else:
                        song_info = self._parse_song_text(text)
                        if song_info and self._is_valid_song(song_info):
                            playlist.append({
                                "position": position,
                                "artist": song_info["artist"],
                                "title": song_info["title"]
                            })
                            position += 1
                            logger.info(f"Canción encontrada (párrafo): {song_info['artist']} - {song_info['title']}")
        
        return playlist

    def _parse_popcasting_playlist_text(self, text: str) -> list[dict]:
        """Parsea texto específico de Popcasting con múltiples canciones separadas por ::"""
        songs = []
        
        if "::" in text:
            parts = text.split("::")
            for part in parts:
                part = part.strip()
                if part:
                    song_info = self._parse_song_text(part)
                    if song_info:
                        songs.append(song_info)
        
        return songs

    def _parse_song_text(self, text: str) -> dict | None:
        """Parsea texto para extraer artista y título de una canción."""
        patterns = [
            r"^(.+?)\s*[-–—]\s*(.+)$",  # Artista - Título
            r"^(.+?)\s*:\s*(.+)$",      # Artista: Título
            r'^(.+?)\s*"\s*(.+?)\s*"$', # Artista "Título"
            r"^(.+?)\s*·\s*(.+)$",      # Artista · Título (formato Popcasting)
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text.strip())
            if match:
                artist = match.group(1).strip()
                title = match.group(2).strip()
                
                # Filtrar texto que no parece ser una canción
                if (len(artist) > 1 and len(title) > 1 and
                    not any(word in artist.lower() for word in ['comentarios', 'compartir', 'twitter', 'facebook', 'popcasting'])):
                    return {"artist": artist, "title": title}
        
        return None

    def _is_valid_song(self, song: dict) -> bool:
        """Verifica si una canción extraída es válida (no es una URL o texto no musical)."""
        artist = song.get("artist", "").lower()
        title = song.get("title", "").lower()
        
        # Filtrar URLs
        if artist.startswith("http") or title.startswith("http"):
            logger.warning(f"Canción filtrada (URL): {song['artist']} - {song['title']}")
            return False
        
        # Filtrar texto que no parece ser una canción (como en web_extractor.py)
        invalid_words = [
            "comentarios", "compartir", "twitter", "facebook", "popcasting",
            "https", "www", ".com", ".org", ".net", ".mp3", ".wav",
            "ko-fi", "bandcamp", "spotify", "youtube", "soundcloud"
        ]
        
        for word in invalid_words:
            if word in artist or word in title:
                logger.warning(f"Canción filtrada (texto inválido): {song['artist']} - {song['title']}")
                return False
        
        # Verificar que artista y título tienen longitud mínima
        if len(artist) < 2 or len(title) < 2:
            logger.warning(f"Canción filtrada (muy corta): {song['artist']} - {song['title']}")
            return False
        
        return True


if __name__ == "__main__":
    """
    Punto de entrada para pruebas directas del WordPressClient.
    """
    try:
        from sincronizador_rss.src.components.config_manager import ConfigManager
        
        # Cargar configuración
        config_manager = ConfigManager()
        wordpress_config = config_manager.get_wordpress_config()
        api_url = wordpress_config['api_url']
        
        # Número de capítulo por defecto
        chapter_number = "484"
        
        # Si se proporciona un número de capítulo como argumento, usarlo
        if len(sys.argv) > 1:
            chapter_number = sys.argv[1]
        
        # Fecha necesaria para construir la URL
        date = "2025-07-18"  # Fecha de ejemplo
        if len(sys.argv) > 2:
            date = sys.argv[2]
        
        print(f"Probando WordPressClient con API URL: {api_url}")
        print(f"Buscando capítulo: {chapter_number} con fecha: {date}")
        print("-" * 50)
        
        # Crear instancia del cliente WordPress
        client = WordPressClient(api_url)
        
        # Buscar el post usando fecha y número
        post_data = client.get_post_details_by_date_and_number(date, chapter_number)
        
        if post_data:
            print(f"\n✅ Capítulo {chapter_number} encontrado!")
            print(f"📝 Título: {post_data.get('title', 'Sin título')}")
            print(f"📅 Fecha: {post_data.get('date', 'Sin fecha')}")
            print(f"🔗 WordPress URL: {post_data.get('wordpress_url', 'Sin enlace')}")
            print(f"🖼️  Imagen de portada: {post_data.get('cover_image_url', 'Sin imagen')}")
            print(f"🔗 Enlaces adicionales: {len(post_data.get('web_extra_links', []))} encontrados")
            print(f"🎵 Canciones en playlist: {len(post_data.get('web_playlist', []))} encontradas")
            print(f"📊 Tamaño de contenido: {post_data.get('content_length', 0)} bytes")
            
            # Mostrar algunos enlaces adicionales como ejemplo
            extra_links = post_data.get('web_extra_links', [])
            if extra_links:
                print(f"\n🔗 Enlaces adicionales (primeros 3):")
                for i, link in enumerate(extra_links[:3]):
                    print(f"  {i+1}. {link.get('text', 'Sin texto')} -> {link.get('url', 'Sin URL')}")
            
            # Mostrar algunas canciones como ejemplo
            playlist = post_data.get('web_playlist', [])
            if playlist:
                print(f"\n🎵 Playlist (primeras 3 canciones):")
                for i, song in enumerate(playlist[:3]):
                    print(f"  {song.get('position', i+1)}. {song.get('artist', 'Sin artista')} - {song.get('title', 'Sin título')}")
        else:
            print(f"\n⚠️  No se encontró el capítulo {chapter_number} con fecha {date}")
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        sys.exit(1)

#activar el entorno virtual
#source .venv/bin/activate

# Probar con capítulo 1 (por defecto)
#python src/components/wordpress_client.py

# Probar con capítulo específico (usa fecha por defecto)
#python src/components/wordpress_client.py 484

# Especificar número y fecha
#python src/components/wordpress_client.py 484 2025-07-18
#python src/components/wordpress_client.py 483 2025-07-12