import feedparser
import requests
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import pytz
from utils import (
    clean_text, 
    normalize_separators, 
    extract_program_info, 
    validate_song_entry, 
    clean_song_info,
    detect_playlist_section,
    detect_external_links,
    clean_text_from_external_links,
    detect_special_mentions
)


class PopcastingExtractor:
    def __init__(self):
        self.rss_url = "https://feeds.feedburner.com/Popcasting"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def extract_episodes(self) -> List[Dict]:
        """Extrae todos los episodios del RSS de Popcasting"""
        try:
            # Intentar obtener más episodios usando diferentes URLs
            urls_to_try = [
                self.rss_url,
                "https://www.ivoox.com/podcast-popcasting_fg_f1604_feedRSS_o.xml",
                "https://feeds.feedburner.com/Popcasting?format=xml"
            ]
            
            all_episodes = []
            
            for url in urls_to_try:
                try:
                    print(f"Intentando obtener episodios de: {url}")
                    feed = feedparser.parse(url)
                    
                    if feed.entries:
                        print(f"Encontrados {len(feed.entries)} episodios en {url}")
                        
                        for entry in feed.entries:
                            episode_data = self._extract_episode_data(entry)
                            if episode_data:
                                # Evitar duplicados basándose en el título
                                if not any(ep['title'] == episode_data['title'] for ep in all_episodes):
                                    all_episodes.append(episode_data)
                        
                        # Si encontramos episodios, continuar con la siguiente URL
                        if all_episodes:
                            continue
                    else:
                        print(f"No se encontraron episodios en {url}")
                        
                except Exception as e:
                    print(f"Error al procesar {url}: {e}")
                    continue
            
            # Ordenar por número de programa si está disponible
            all_episodes.sort(key=lambda x: int(x.get('program_number', 0) or 0), reverse=True)
            
            return all_episodes
            
        except Exception as e:
            print(f"Error al extraer episodios: {e}")
            return []
    
    def _extract_episode_data(self, entry) -> Optional[Dict]:
        """Extrae datos de un episodio individual"""
        try:
            # Información básica del episodio
            title = entry.get('title', '')
            description = entry.get('description', '')
            published = entry.get('published', '')
            
            # Extraer número del programa del título
            program_number = self._extract_program_number(title)
            
            # Normalizar fecha a zona horaria de Madrid
            published_madrid = self._normalize_to_madrid_timezone(published)
            
            # Extraer enlaces de iVoox
            ivoox_download_url, ivoox_web_url = self._extract_ivoox_links(entry)
            
            # Extraer enlaces externos específicos del episodio
            episode_external_links = self._extract_episode_external_links(description)
            
            # Extraer playlist de canciones (ya limpia de enlaces externos)
            playlist = self._extract_playlist(description)
            
            # Extraer enlaces extra (HTML links)
            extra_links = self._extract_extra_links(description)
            
            return {
                'program_number': program_number,
                'title': title,
                'published': published_madrid,
                'ivoox_download_url': ivoox_download_url,
                'ivoox_web_url': ivoox_web_url,
                'playlist': playlist,
                'extra_links': extra_links,
                'episode_external_links': episode_external_links
            }
        except Exception as e:
            print(f"Error al procesar episodio: {e}")
            return None
    
    def _normalize_to_madrid_timezone(self, published_str: str) -> str:
        """Normaliza la fecha a zona horaria de Madrid"""
        if not published_str:
            return published_str
        
        try:
            # Parsear la fecha original
            dt = datetime.strptime(published_str, '%a, %d %b %Y %H:%M:%S %z')
            
            # Convertir a zona horaria de Madrid
            madrid_tz = pytz.timezone('Europe/Madrid')
            dt_madrid = dt.astimezone(madrid_tz)
            
            # Formatear de vuelta al formato RSS
            return dt_madrid.strftime('%a, %d %b %Y %H:%M:%S %z')
            
        except Exception as e:
            print(f"Error al normalizar fecha {published_str}: {e}")
            return published_str
    
    def _extract_program_number(self, title: str) -> Optional[str]:
        """Extrae el número del programa del título"""
        program_info = extract_program_info(title)
        return program_info.get('number')
    
    def _extract_ivoox_links(self, entry) -> tuple:
        """Extrae URLs de descarga y web de iVoox"""
        download_url = None
        web_url = None
        
        # Buscar en los links del entry
        if hasattr(entry, 'links'):
            for link in entry.links:
                href = link.get('href', '')
                if 'ivoox' in href.lower():
                    if link.get('type') == 'audio/mpeg' or 'download' in href:
                        download_url = href
                    else:
                        web_url = href
        
        # Buscar en enclosures
        if hasattr(entry, 'enclosures'):
            for enclosure in entry.enclosures:
                if 'ivoox' in enclosure.get('href', '').lower():
                    download_url = enclosure.get('href')
        
        # Buscar en el contenido/descripción
        content = entry.get('description', '') + entry.get('content', [{}])[0].get('value', '')
        soup = BeautifulSoup(content, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'ivoox' in href.lower():
                if not web_url:
                    web_url = href
                if 'download' in href.lower() or '.mp3' in href.lower():
                    download_url = href
        
        return download_url, web_url
    
    def _extract_episode_external_links(self, description: str) -> List[Dict]:
        """Extrae enlaces externos específicos del episodio (obituarios, menciones especiales, etc.)"""
        external_links = []
        
        # Limpiar HTML
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text()
        
        # Detectar enlaces externos marcados con múltiples ::
        episode_links = detect_external_links(text)
        
        # Recopilar URLs ya detectadas
        detected_urls = {link['url'] for link in episode_links}
        
        # Detectar menciones especiales (ko-fi, patreon, etc.) evitando duplicados
        special_mentions = detect_special_mentions(text, detected_urls)
        
        # Combinar todos los enlaces (ya sin duplicados)
        external_links = episode_links + special_mentions
        
        return external_links

    def _extract_playlist(self, description: str) -> List[Dict]:
        """Extrae la playlist de canciones de la descripción"""
        playlist = []
        
        # Limpiar HTML
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text()
        
        # Limpiar enlaces externos antes de procesar canciones
        text = clean_text_from_external_links(text)
        
        # Limpiar y normalizar texto
        text = clean_text(text)
        text = normalize_separators(text)
        
        # Buscar sección específica de playlist
        playlist_text = detect_playlist_section(text)
        if not playlist_text:
            # Si no encuentra sección específica, buscar en todo el texto
            playlist_text = text
        
        # Extraer canciones individuales
        # Dividir por :: primero
        songs = re.split(r'\s*::\s*', playlist_text)
        
        position = 1
        for song in songs:
            song = song.strip()
            if not song:
                continue
                
            # Buscar patrón artista · canción
            match = re.search(r'(.+?)\s*·\s*(.+)', song)
            if match:
                artist = match.group(1).strip()
                song_title = match.group(2).strip()
                
                # Limpiar información de artista y canción
                artist, song_title = clean_song_info(artist, song_title)
                
                # Validar entrada
                if validate_song_entry(artist, song_title):
                    playlist.append({
                        'position': position,
                        'artist': artist,
                        'song': song_title
                    })
                    position += 1
        
        return playlist
    
    def _extract_extra_links(self, description: str) -> List[Dict]:
        """Extrae enlaces extra de la descripción (solo enlaces HTML, no los de múltiples ::)"""
        extra_links = []
        seen_urls = set()
        
        soup = BeautifulSoup(description, 'html.parser')
        
        # Buscar todos los enlaces HTML que no sean de iVoox ni de los enlaces externos ya procesados
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # Filtrar enlaces de iVoox (ya procesados) y enlaces que ya están en external_links
            if ('ivoox' not in href.lower() and 
                'ko-fi' not in href.lower() and 
                'jenesaispop' not in href.lower() and
                href not in seen_urls):
                
                seen_urls.add(href)
                extra_links.append({
                    'url': href,
                    'text': text
                })
        
        return extra_links
    
    def save_to_json(self, episodes: List[Dict], filename: str = None):
        """Guarda los episodios en formato JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"outputs/popcasting_episodes_{timestamp}.json"
        
        # Si el filename ya incluye la ruta, no agregar outputs/
        if not filename.startswith('outputs/') and '/' not in filename:
            filepath = f"outputs/{filename}"
        else:
            filepath = filename
        
        try:
            # Asegurar que el directorio existe
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(episodes, f, ensure_ascii=False, indent=2)
            
            print(f"Datos guardados en: {filepath}")
            print(f"Total de episodios procesados: {len(episodes)}")
            
        except Exception as e:
            print(f"Error al guardar archivo: {e}")
    
    def run(self):
        """Ejecuta el proceso completo de extracción"""
        print("Iniciando extracción de datos de Popcasting...")
        episodes = self.extract_episodes()
        
        if episodes:
            self.save_to_json(episodes)
            
            # Mostrar estadísticas
            total_songs = sum(len(ep.get('playlist', [])) for ep in episodes)
            print(f"Total de canciones extraídas: {total_songs}")
        else:
            print("No se pudieron extraer episodios")


if __name__ == "__main__":
    extractor = PopcastingExtractor()
    extractor.run() 