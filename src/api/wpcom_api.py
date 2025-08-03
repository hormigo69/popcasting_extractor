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