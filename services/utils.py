"""
Utilidades para el procesamiento de datos de Popcasting
"""

import re
from typing import List, Dict, Optional


def clean_text(text: str) -> str:
    """Limpia texto eliminando espacios extra y caracteres especiales"""
    if not text:
        return ""
    
    # Eliminar espacios extra
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar caracteres de control
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()


def normalize_separators(text: str) -> str:
    """Normaliza separadores de playlist para manejar errores comunes"""
    # Normalizar :: con espacios variables
    text = re.sub(r'\s*::\s*', ' :: ', text)
    
    # Normalizar · con espacios variables
    text = re.sub(r'\s*·\s*', ' · ', text)
    
    # Manejar casos donde faltan espacios
    text = re.sub(r'::(?!\s)', ':: ', text)
    text = re.sub(r'(?<!\s)::', ' ::', text)
    
    return text


def extract_program_info(title: str) -> Dict[str, Optional[str]]:
    """Extrae información del programa desde el título"""
    info = {
        'number': None,
        'season': None,
        'special': None
    }
    
    # Patrones para número de programa
    number_patterns = [
        r'Popcasting(\d+)',  # Patrón específico para Popcasting483
        r'Programa\s+(\d+)',
        r'#(\d+)',
        r'Ep\.?\s*(\d+)',
        r'Episodio\s+(\d+)',
        r'(\d+)º?\s*programa'
    ]
    
    for pattern in number_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            info['number'] = match.group(1)
            break
    
    # Patrones para temporada
    season_patterns = [
        r'Temporada\s+(\d+)',
        r'T(\d+)',
        r'Season\s+(\d+)'
    ]
    
    for pattern in season_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            info['season'] = match.group(1)
            break
    
    # Detectar episodios especiales
    special_patterns = [
        r'especial',
        r'navidad',
        r'año\s+nuevo',
        r'verano',
        r'extra'
    ]
    
    for pattern in special_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            info['special'] = True
            break
    
    return info


def validate_song_entry(artist: str, song: str) -> bool:
    """Valida que una entrada de canción sea válida"""
    if not artist or not song:
        return False
    
    # Filtrar entradas muy cortas
    if len(artist.strip()) < 2 or len(song.strip()) < 2:
        return False
    
    # Filtrar entradas que parecen ser texto descriptivo
    invalid_patterns = [
        r'^\d+[\.\)]\s*$',  # Solo números
        r'^[^\w]*$',        # Solo caracteres especiales
        r'continuamos',
        r'seguimos',
        r'próxima',
        r'anterior'
    ]
    
    combined_text = f"{artist} {song}".lower()
    for pattern in invalid_patterns:
        if re.search(pattern, combined_text):
            return False
    
    return True


def clean_song_info(artist: str, song: str) -> tuple:
    """Limpia información de artista y canción"""
    # Limpiar artista
    artist = clean_text(artist)
    artist = re.sub(r'^\d+[\.\)]\s*', '', artist)  # Remover numeración
    artist = re.sub(r'\s*\([^)]*\)\s*$', '', artist)  # Remover info entre paréntesis
    
    # Limpiar canción
    song = clean_text(song)
    song = re.sub(r'\s*\([^)]*\)\s*$', '', song)  # Remover info entre paréntesis al final
    
    return artist.strip(), song.strip()


def detect_playlist_section(text: str) -> Optional[str]:
    """Detecta y extrae la sección de playlist del texto"""
    # Patrones para identificar secciones de playlist
    section_patterns = [
        r'playlist[:\s]*(.*?)(?:\n\n|\Z)',
        r'canciones[:\s]*(.*?)(?:\n\n|\Z)',
        r'música[:\s]*(.*?)(?:\n\n|\Z)',
        r'tracklist[:\s]*(.*?)(?:\n\n|\Z)',
        r'temas[:\s]*(.*?)(?:\n\n|\Z)',
        r'sonamos[:\s]*(.*?)(?:\n\n|\Z)'
    ]
    
    for pattern in section_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    
    return None


def extract_timestamps(text: str) -> List[Dict]:
    """Extrae timestamps de las canciones si están disponibles"""
    timestamps = []
    
    # Patrones para timestamps
    timestamp_patterns = [
        r'(\d{1,2}:\d{2})\s*[-–]\s*(.+)',
        r'(\d{1,2}:\d{2}:\d{2})\s*[-–]\s*(.+)',
        r'\[(\d{1,2}:\d{2})\]\s*(.+)',
        r'\((\d{1,2}:\d{2})\)\s*(.+)'
    ]
    
    lines = text.split('\n')
    for line in lines:
        for pattern in timestamp_patterns:
            match = re.search(pattern, line.strip())
            if match:
                timestamp = match.group(1)
                content = match.group(2).strip()
                
                timestamps.append({
                    'timestamp': timestamp,
                    'content': content
                })
    
    return timestamps 


def detect_external_links(text: str) -> List[Dict]:
    """Detecta enlaces externos marcados con múltiples :: en el texto"""
    external_links = []
    seen_urls = set()  # Deduplicar solo por URL
    
    # Buscar patrones con múltiples :: (4 o más)
    # Ejemplo: :::::: obituario brian wilson · https://... ::::::
    patterns = [
        r':{4,}\s*([^:]+?)\s*·\s*(https?://[^\s\]]+)',  # Con · separador
        r':{4,}\s*([^:]+?)\s+(https?://[^\s\]]+)',  # Sin · separador
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            description = clean_text(match[0]).strip()
            url = match[1].strip()
            
            # Limpiar descripción: remover · al final
            description = re.sub(r'\s*·\s*$', '', description)
            
            # Limpiar URL duplicada si existe
            if url.count('http') > 1:
                # Tomar solo la primera URL completa hasta el primer espacio o duplicación
                urls = re.findall(r'https?://[^\s]+', url)
                if urls:
                    url = urls[0]  # Tomar la primera URL
            
            # Limpiar caracteres finales no deseados
            url = re.sub(r'[^\w\-\./:?=&%#]+$', '', url)
            
            # Detectar y corregir URLs duplicadas en el path
            # Ejemplo: https://site.com/path/https://site.com/path -> https://site.com/path
            if url.count('https://') > 1:
                # Tomar solo hasta la primera duplicación
                first_https = url.find('https://')
                second_https = url.find('https://', first_https + 1)
                if second_https > 0:
                    url = url[:second_https]
            
            # Limpiar trailing slash y caracteres extra
            url = url.rstrip('/')
            
            # Solo agregar si la URL no se ha visto antes
            if description and url and url not in seen_urls:
                seen_urls.add(url)
                external_links.append({
                    'description': description,
                    'url': url,
                    'type': 'external_link'
                })
    
    return external_links


def clean_text_from_external_links(text: str) -> str:
    """Limpia el texto removiendo los enlaces externos marcados con múltiples ::"""
    
    # Primero, dividir el texto en líneas para procesamiento más preciso
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Saltar líneas que contienen patrones de enlaces externos
        if re.search(r':{4,}', line):
            continue  # Omitir completamente estas líneas
        
        # Limpiar cualquier resto de enlaces que pudiera haberse mezclado
        line = re.sub(r'invita a Popcasting a (?:un )?café\s+https?://[^\s]+', '', line, flags=re.IGNORECASE)
        line = re.sub(r'https?://[^\s]+', '', line)  # Remover cualquier URL restante
        
        if line.strip():  # Solo añadir líneas no vacías
            cleaned_lines.append(line.strip())
    
    # Reunir las líneas limpias
    cleaned_text = '\n'.join(cleaned_lines)
    
    # Limpiar espacios extra
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text)
    
    return cleaned_text.strip()


def detect_special_mentions(text: str, existing_urls: set = None) -> List[Dict]:
    """Detecta menciones especiales como invitaciones a café, etc."""
    special_mentions = []
    seen_links = existing_urls or set()  # Usar URLs ya detectadas para evitar duplicados
    
    # Buscar patrones específicos (más flexibles)
    patterns = [
        (r'invita a Popcasting a (?:un )?café\s+(https?://[^\s]+)', 'coffee_invitation'),
        (r'apoya.*?popcasting.*?(https?://[^\s]+)', 'support_link'),
        (r'patreon.*?(https?://[^\s]+)', 'patreon'),
        (r'ko-fi.*?(https?://[^\s]+)', 'kofi')
    ]
    
    for pattern, link_type in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            url = match.strip()
            # Limpiar caracteres finales no deseados
            url = re.sub(r'[^\w\-\./:?=&%#]+$', '', url)
            
            # Solo agregar si la URL no existe ya en external_links
            if url and url not in seen_links:
                seen_links.add(url)
                special_mentions.append({
                    'description': f'{link_type.replace("_", " ").title()}',
                    'url': url,
                    'type': link_type
                })
    
    return special_mentions 