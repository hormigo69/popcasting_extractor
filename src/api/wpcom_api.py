import requests

# URL base de la API de WordPress.com
BASE_URL = "https://public-api.wordpress.com/rest/v1.2/sites/popcastingpop.com"

#Obtiene datos crudos de la API
def fetch_posts(page: int, per_page: int) -> dict:
    """Llama al endpoint /posts y devuelve el JSON."""
    resp = requests.get(
        f"{BASE_URL}/posts",
        params={"page": page, "number": per_page}
    )
    resp.raise_for_status()
    return resp.json()

# Transforma un post individual
def map_post(raw: dict) -> dict:
    """Transforma un post crudo de WordPress a un formato limpio."""
    return {
        "id": raw["ID"],
        "title": raw["title"],
        "published_at": raw["date"],
        "url": raw["URL"],
        "content": raw["content"],
        "attachments": raw.get("attachments", [])
    } 

# Función combinada que obtiene y transforma todos los posts
def get_attachment_details(attachment_id: str) -> dict:
    """Obtiene los detalles de un attachment por su ID."""
    try:
        resp = requests.get(
            f"{BASE_URL}/media/{attachment_id}"
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error al obtener attachment {attachment_id}: {e}")
        return {}

def extract_best_mp3_url(content: str) -> str:
    """
    Extrae la mejor URL de MP3 del contenido HTML.
    Prioriza URLs sin tokens o con tokens más estables.
    """
    import re
    
    # Buscar todas las URLs de MP3
    mp3_patterns = [
        r'href=["\']([^"\']*\.mp3[^"\']*)["\']',
        r'src=["\']([^"\']*\.mp3[^"\']*)["\']',
        r'https?://[^\s<>"\']*\.mp3[^\s<>"\']*',
    ]
    
    all_urls = []
    for pattern in mp3_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        all_urls.extend(matches)
    
    # Eliminar duplicados y limpiar
    unique_urls = list(set(all_urls))
    unique_urls = [url.strip() for url in unique_urls if url.strip()]
    
    if not unique_urls:
        return None
    
    # Priorizar URLs de iVoox sin tokens o con tokens más simples
    ivoox_urls = [url for url in unique_urls if 'ivoox.com' in url]
    
    if ivoox_urls:
        # Ordenar por prioridad:
        # 1. URLs sin token (?t=...)
        # 2. URLs con token más corto
        # 3. URLs con _wp_1.mp3 (más estables)
        
        def url_priority(url):
            # Sin token = prioridad más alta
            if '?t=' not in url:
                return 0
            # Con _wp_1.mp3 = prioridad media
            if '_wp_1.mp3' in url:
                return 1
            # Con token = prioridad baja
            return 2
        
        # Ordenar por prioridad
        ivoox_urls.sort(key=url_priority)
        
        # Tomar la primera (mejor prioridad)
        best_url = ivoox_urls[0]
        
        # Si la URL tiene un token problemático, intentar limpiarlo
        if '?t=' in best_url and '_wp_1.mp3' in best_url:
            # Usar la URL base sin token
            base_url = best_url.split('?')[0]
            return base_url
        
        return best_url
    
    # Si no hay URLs de iVoox, devolver la primera URL de MP3
    return unique_urls[0]


def extract_ivoox_page_url(content: str) -> str:
    """
    Extrae la URL de la página de iVoox (no la URL directa del MP3).
    Busca enlaces a páginas de iVoox que contengan 'audios-mp3' o similar.
    """
    import re
    
    # Buscar URLs de páginas de iVoox
    ivoox_page_patterns = [
        r'href=["\'](https?://[^"\']*ivoox\.com[^"\']*audios-mp3[^"\']*)["\']',
        r'href=["\'](https?://[^"\']*ivoox\.com[^"\']*\.html[^"\']*)["\']',
        r'https?://[^\s<>"\']*ivoox\.com[^\s<>"\']*audios-mp3[^\s<>"\']*',
        r'https?://[^\s<>"\']*ivoox\.com[^\s<>"\']*\.html[^\s<>"\']*',
    ]
    
    all_urls = []
    for pattern in ivoox_page_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        all_urls.extend(matches)
    
    # Eliminar duplicados y limpiar
    unique_urls = list(set(all_urls))
    unique_urls = [url.strip() for url in unique_urls if url.strip()]
    
    # Filtrar solo URLs de páginas (no archivos MP3 directos)
    page_urls = [url for url in unique_urls if '.html' in url and not url.endswith('.mp3')]
    
    if page_urls:
        # Priorizar URLs que contengan 'audios-mp3'
        audios_mp3_urls = [url for url in page_urls if 'audios-mp3' in url]
        if audios_mp3_urls:
            return audios_mp3_urls[0]
        
        # Si no hay URLs con 'audios-mp3', devolver la primera página
        return page_urls[0]
    
    # Si no encontramos URLs de páginas, intentar construir la URL a partir del MP3
    mp3_url = extract_best_mp3_url(content)
    if mp3_url and 'ivoox.com' in mp3_url:
        # Extraer el ID del episodio de la URL del MP3
        # Ejemplo: https://www.ivoox.com/popcasting486_md_154272934_wp_1.mp3
        # Queremos: https://www.ivoox.com/en/popcasting486-audios-mp3_rf_154272934_1.html
        
        # Buscar el patrón del ID en la URL del MP3
        id_match = re.search(r'_md_(\d+)_', mp3_url)
        if id_match:
            episode_id = id_match.group(1)
            
            # Buscar el número del episodio en el contenido
            episode_number_match = re.search(r'Popcasting\s+(\d+)', content, re.IGNORECASE)
            if episode_number_match:
                episode_number = episode_number_match.group(1)
                
                # Construir la URL de la página
                page_url = f"https://www.ivoox.com/en/popcasting{episode_number}-audios-mp3_rf_{episode_id}_1.html"
                return page_url
    
    return None


def get_file_size(url: str) -> int:
    """
    Obtiene el tamaño del archivo con una petición HEAD.
    
    Args:
        url: URL del archivo MP3
        
    Returns:
        int: Tamaño del archivo en bytes, 0 si no se puede obtener
    """
    try:
        import requests
        response = requests.head(url, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        content_length = response.headers.get('Content-Length')
        if content_length:
            return int(content_length)
        
        return 0
    except Exception as e:
        print(f"⚠️ No se pudo obtener el tamaño del archivo {url}: {e}")
        return 0


def extract_cover_image_url(content: str) -> str:
    """
    Extrae la URL de la imagen de portada del contenido HTML.
    Busca imágenes con data-orig-file que contengan wp-content/uploads.
    
    Args:
        content: Contenido HTML del post
        
    Returns:
        str: URL de la imagen de portada, None si no se encuentra
    """
    import re
    
    # Buscar imágenes con data-orig-file (criterio principal)
    data_orig_pattern = r'data-orig-file=["\']([^"\']+wp-content/uploads[^"\']+)["\']'
    data_orig_matches = re.findall(data_orig_pattern, content, re.IGNORECASE)
    
    if data_orig_matches:
        # Filtrar para encontrar la imagen del número del episodio (ej: 486.png)
        for img_url in data_orig_matches:
            if re.search(r'\d+\.png$', img_url):
                return img_url
        
        # Si no encontramos la imagen del número, devolver la primera
        return data_orig_matches[0]
    
    # Fallback: buscar cualquier imagen con wp-content/uploads
    wp_images_pattern = r'https?://[^\s<>"\']*wp-content/uploads[^\s<>"\']*\.(png|jpg|jpeg|gif)'
    wp_images_matches = re.findall(wp_images_pattern, content, re.IGNORECASE)
    
    if wp_images_matches:
        # Filtrar para encontrar la imagen del número del episodio
        for img_url in wp_images_matches:
            if re.search(r'\d+\.png$', img_url):
                return img_url
        
        # Si no encontramos la imagen del número, devolver la primera
        return wp_images_matches[0]
    
    return None


def extract_web_extra_links(content: str) -> list[dict]:
    """
    Extrae enlaces adicionales del contenido HTML.
    Busca spans con color específico y párrafos centrados con enlaces.
    
    Args:
        content: Contenido HTML del post
        
    Returns:
        list[dict]: Lista de enlaces adicionales con formato {"text": str, "url": str}
    """
    import re
    import html
    
    extra_links = []
    
    # Buscar spans con el color específico de Popcasting (#ff99cc)
    colored_span_pattern = r'<span[^>]*style="[^"]*#ff99cc[^"]*"[^>]*>(.*?)</span>'
    colored_span_matches = re.findall(colored_span_pattern, content, re.IGNORECASE | re.DOTALL)
    
    for span_content in colored_span_matches:
        # Buscar enlaces dentro del span
        link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
        link_matches = re.findall(link_pattern, span_content, re.IGNORECASE)
        
        for url, text in link_matches:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            clean_text = html.unescape(clean_text)
            
            # Filtrar enlaces de Ko-fi
            if clean_text and url and 'ko-fi.com/popcasting' not in url:
                extra_links.append({"text": clean_text, "url": url})
    
    # También buscar en párrafos centrados que pueden contener enlaces
    centered_link_pattern = r'<p[^>]*class="[^"]*has-text-align-center[^"]*"[^>]*>(.*?)</p>'
    centered_link_matches = re.findall(centered_link_pattern, content, re.IGNORECASE | re.DOTALL)
    
    for p_content in centered_link_matches:
        # Buscar enlaces dentro del párrafo
        link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
        link_matches = re.findall(link_pattern, p_content, re.IGNORECASE)
        
        for url, text in link_matches:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            clean_text = html.unescape(clean_text)
            
            # Filtrar enlaces de Ko-fi y duplicados
            if (clean_text and url and 
                'ko-fi.com/popcasting' not in url and 
                not any(existing['url'] == url for existing in extra_links)):
                extra_links.append({"text": clean_text, "url": url})
    
    return extra_links


def extract_web_playlist(content: str) -> list[dict]:
    """
    Extrae la playlist del contenido HTML.
    Busca canciones en párrafos centrados con formato "Artista · Título".
    
    Args:
        content: Contenido HTML del post
        
    Returns:
        list[dict]: Lista de canciones con formato {"position": int, "artist": str, "title": str}
    """
    import re
    import html
    
    playlist = []
    
    # Buscar párrafos centrados (formato moderno de playlist)
    centered_pattern = r'<p[^>]*style="[^"]*text-align:\s*center[^"]*"[^>]*>(.*?)</p>'
    centered_matches = re.findall(centered_pattern, content, re.IGNORECASE | re.DOTALL)
    
    for p_content in centered_matches:
        # Limpiar HTML tags y entidades
        clean_text = re.sub(r'<[^>]+>', '', p_content)
        clean_text = html.unescape(clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Buscar canciones en el texto del párrafo
        songs = _parse_popcasting_playlist_text(clean_text)
        if songs:
            for i, song in enumerate(songs, len(playlist) + 1):
                if _is_valid_song(song):
                    playlist.append({
                        "position": i,
                        "artist": song["artist"],
                        "title": song["title"]
                    })
    
    return playlist


def _parse_popcasting_playlist_text(text: str) -> list[dict]:
    """
    Parsea texto específico de Popcasting con múltiples canciones separadas por ::
    
    Args:
        text: Texto con canciones separadas por ::
        
    Returns:
        list[dict]: Lista de canciones con formato {"artist": str, "title": str}
    """
    songs = []
    
    if "::" in text:
        parts = text.split("::")
        for part in parts:
            part = part.strip()
            if part:
                song_info = _parse_song_text(part)
                if song_info:
                    songs.append(song_info)
    
    return songs


def _parse_song_text(text: str) -> dict | None:
    """
    Parsea texto para extraer artista y título de una canción.
    
    Args:
        text: Texto de la canción
        
    Returns:
        dict | None: Diccionario con {"artist": str, "title": str} o None si no es válido
    """
    import re
    import html
    
    # Limpiar caracteres Unicode antes de procesar
    cleaned_text = _clean_unicode_text(text)
    
    patterns = [
        r"^(.+?)\s*[-–—]\s*(.+)$",  # Artista - Título
        r"^(.+?)\s*:\s*(.+)$",      # Artista: Título
        r'^(.+?)\s*"\s*(.+?)\s*"$', # Artista "Título"
        r"^(.+?)\s*·\s*(.+)$",      # Artista · Título (formato Popcasting)
    ]
    
    for pattern in patterns:
        match = re.match(pattern, cleaned_text.strip())
        if match:
            artist = _clean_unicode_text(match.group(1).strip())
            title = _clean_unicode_text(match.group(2).strip())
            
            # Filtrar texto que no parece ser una canción
            if (len(artist) > 1 and len(title) > 1 and
                not any(word in artist.lower() for word in ['comentarios', 'compartir', 'twitter', 'facebook', 'popcasting'])):
                return {"artist": artist, "title": title}
    
    return None


def _is_valid_song(song: dict) -> bool:
    """
    Verifica si una canción extraída es válida (no es una URL o texto no musical).
    
    Args:
        song: Diccionario con {"artist": str, "title": str}
        
    Returns:
        bool: True si la canción es válida, False en caso contrario
    """
    artist = song.get("artist", "").lower()
    title = song.get("title", "").lower()
    
    # Filtrar URLs
    if artist.startswith("http") or title.startswith("http"):
        return False
    
    # Filtrar texto que no parece ser una canción
    invalid_words = [
        "comentarios", "compartir", "twitter", "facebook", "popcasting",
        "https", "www", ".com", ".org", ".net", ".mp3", ".wav",
        "ko-fi", "bandcamp", "spotify", "youtube", "soundcloud"
    ]
    
    for word in invalid_words:
        if word in artist or word in title:
            return False
    
    # Verificar que artista y título tienen longitud mínima
    if len(artist) < 2 or len(title) < 2:
        return False
    
    return True


def _clean_unicode_text(text: str) -> str:
    """
    Limpia caracteres Unicode escapados y entidades HTML.
    
    Args:
        text: Texto a limpiar
        
    Returns:
        str: Texto limpio
    """
    import html
    
    if not text:
        return text
    
    try:
        # Si detectamos patrones típicos de mala codificación, intentamos decodificar
        if 'Ã' in text or 'Â' in text:
            try:
                text = text.encode('latin-1').decode('utf-8')
            except Exception:
                pass
        
        # Limpiar caracteres Unicode problemáticos específicos
        text = text.replace('┬Ę', '·')  # Punto medio Unicode
        text = text.replace('┬Ā', ' ')  # Espacio no separador Unicode
        text = text.replace('┬', '')    # Otros caracteres Unicode problemáticos
        text = text.replace('•', '·')   # Punto medio Unicode alternativo
        text = text.replace('–', '-')   # Guión medio Unicode
        text = text.replace('—', '-')   # Guión largo Unicode
        
        text = html.unescape(text)
        return text.strip()
    except Exception:
        return text.strip()


def extract_comments(title: str) -> str | None:
    """
    Extrae los comentarios desde el título (texto después del número).
    
    Args:
        title: Título del episodio
        
    Returns:
        str: Comentarios extraídos o None si no hay comentarios
    """
    import re
    
    if not title:
        return None
    
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


def parse_duration(duration_str: str) -> int | None:
    """
    Convierte la duración de formato HH:MM:SS a segundos.
    
    Args:
        duration_str: Duración en formato "HH:MM:SS" o "MM:SS"
        
    Returns:
        int: Duración en segundos o None si no se puede parsear
    """
    if not duration_str:
        return None
    
    try:
        # Formato: "01:51:12" o "MM:SS"
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
        print(f"⚠️ No se pudo parsear la duración: {duration_str}")
    
    return None


def get_duration_from_mp3(url: str) -> int | None:
    """
    Extrae la duración exacta de un archivo MP3 desde una URL usando ffprobe.
    
    Args:
        url: URL del archivo MP3
        
    Returns:
        int: Duración en segundos o None si hay error
    """
    import subprocess
    import json
    import tempfile
    import os
    import requests
    
    try:
        # Descargar temporalmente el archivo
        print(f"🔍 Descargando archivo para extraer duración: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        try:
            # Usar ffprobe para obtener información del archivo
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                temp_file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"❌ Error ejecutando ffprobe: {result.stderr}")
                return None
            
            # Parsear la salida JSON
            probe_data = json.loads(result.stdout)
            
            # Buscar la duración en el formato o en el primer stream de audio
            duration = None
            
            # Primero intentar obtener la duración del formato
            if 'format' in probe_data and 'duration' in probe_data['format']:
                duration = float(probe_data['format']['duration'])
            # Si no está en el formato, buscar en los streams de audio
            elif 'streams' in probe_data:
                for stream in probe_data['streams']:
                    if stream.get('codec_type') == 'audio' and 'duration' in stream:
                        duration = float(stream['duration'])
                        break
            
            if duration:
                print(f"✅ Duración extraída: {duration:.2f} segundos")
                return int(duration)  # Convertir a entero para compatibilidad con BD
            else:
                print(f"⚠️ No se pudo obtener la duración de: {url}")
                return None
                
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout al ejecutar ffprobe en: {url}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando salida JSON de ffprobe: {e}")
        return None
    except Exception as e:
        print(f"❌ Error al extraer duración de {url}: {e}")
        return None


def get_posts(page: int, per_page: int) -> list[dict]:
    """Obtiene posts de WordPress y los transforma a formato limpio."""
    response = fetch_posts(page, per_page)
    posts = response.get('posts', [])
    return [map_post(p) for p in posts]


def get_posts_with_attachments(page: int, per_page: int) -> list[dict]:
    """Obtiene posts de WordPress con detalles completos de attachments."""
    response = fetch_posts(page, per_page)
    posts = response.get('posts', [])
    
    enhanced_posts = []
    for post in posts:
        mapped_post = map_post(post)
        
        # Obtener detalles de attachments
        attachments = mapped_post.get('attachments', [])
        detailed_attachments = []
        
        for attachment_id in attachments:
            if isinstance(attachment_id, str) and attachment_id.isdigit():
                attachment_details = get_attachment_details(attachment_id)
                if attachment_details:
                    detailed_attachments.append(attachment_details)
        
        mapped_post['attachments'] = detailed_attachments
        enhanced_posts.append(mapped_post)
    
    return enhanced_posts