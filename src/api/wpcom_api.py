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