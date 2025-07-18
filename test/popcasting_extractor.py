#!/usr/bin/env python3
"""
Extractor de información del podcast Popcasting
Extrae información de todos los episodios desde el RSS y genera un JSON
"""

import requests
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

def extract_episode_number(title):
    """Extrae el número del episodio del título"""
    match = re.search(r'Popcasting(\d+)', title)
    return int(match.group(1)) if match else None

def parse_playlist(description):
    """
    Parsea la descripción para extraer las canciones y enlaces extra
    Formato: artista · canción :: artista · canción :: ...
    """
    songs = []
    extra_links = []
    
    # Dividir por :: para obtener cada elemento
    parts = description.split(' :: ')
    
    position = 1
    for part in parts:
        part = part.strip()
        
        # Verificar si es un enlace (contiene http)
        if 'http' in part:
            # Extraer URLs del texto
            urls = re.findall(r'https?://[^\s]+', part)
            for url in urls:
                extra_links.append({
                    'text': part,
                    'url': url
                })
        else:
            # Verificar si tiene el formato artista · canción
            if ' · ' in part:
                artist_song = part.split(' · ', 1)  # Dividir solo en el primer ·
                if len(artist_song) == 2:
                    artist, song = artist_song
                    songs.append({
                        'position': position,
                        'artist': artist.strip(),
                        'song': song.strip()
                    })
                    position += 1
    
    return songs, extra_links

def extract_popcasting_data(rss_url):
    """
    Extrae todos los datos del RSS de Popcasting
    """
    try:
        # Descargar el RSS
        response = requests.get(rss_url)
        response.raise_for_status()
        
        # Parsear el XML
        root = ET.fromstring(response.content)
        
        # Encontrar todos los items (episodios)
        episodes = []
        
        for item in root.findall('.//item'):
            episode_data = {}
            
            # Título del episodio
            title_elem = item.find('title')
            title = title_elem.text if title_elem is not None else ""
            episode_data['title'] = title
            
            # Número del episodio
            episode_number = extract_episode_number(title)
            episode_data['episode_number'] = episode_number
            
            # URL del episodio en la web
            link_elem = item.find('link')
            web_url = link_elem.text if link_elem is not None else ""
            episode_data['web_url'] = web_url
            
            # URL de descarga (enclosure)
            enclosure_elem = item.find('enclosure')
            download_url = ""
            if enclosure_elem is not None:
                download_url = enclosure_elem.get('url', '')
            episode_data['download_url'] = download_url
            
            # Descripción (contiene la playlist)
            description_elem = item.find('description')
            description = description_elem.text if description_elem is not None else ""
            
            # Parsear la playlist y enlaces extra
            songs, extra_links = parse_playlist(description)
            episode_data['playlist'] = songs
            episode_data['extra_links'] = extra_links
            
            # Fecha de publicación
            pubdate_elem = item.find('pubDate')
            pub_date = pubdate_elem.text if pubdate_elem is not None else ""
            episode_data['publication_date'] = pub_date
            
            # Duración
            duration_elem = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}duration')
            duration = duration_elem.text if duration_elem is not None else ""
            episode_data['duration'] = duration
            
            # GUID
            guid_elem = item.find('guid')
            guid = guid_elem.text if guid_elem is not None else ""
            episode_data['guid'] = guid
            
            episodes.append(episode_data)
        
        return {
            'podcast_name': 'Popcasting',
            'rss_url': rss_url,
            'extraction_date': datetime.now().isoformat(),
            'total_episodes': len(episodes),
            'episodes': episodes
        }
        
    except Exception as e:
        print(f"Error al procesar el RSS: {e}")
        return None

def save_to_json(data, filename):
    """Guarda los datos en un archivo JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Datos guardados en {filename}")
        return True
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
        return False

def main():
    """Función principal"""
    rss_url = "https://feeds.feedburner.com/Popcasting"
    output_file = "popcasting_data.json"
    
    print("Extrayendo datos del podcast Popcasting...")
    print(f"RSS URL: {rss_url}")
    
    # Extraer datos
    data = extract_popcasting_data(rss_url)
    
    if data:
        print(f"Episodios encontrados: {data['total_episodes']}")
        
        # Guardar en JSON
        if save_to_json(data, output_file):
            print("Extracción completada exitosamente!")
            
            # Mostrar estadísticas
            total_songs = sum(len(ep['playlist']) for ep in data['episodes'])
            total_extra_links = sum(len(ep['extra_links']) for ep in data['episodes'])
            
            print("\nEstadísticas:")
            print(f"- Total de episodios: {data['total_episodes']}")
            print(f"- Total de canciones: {total_songs}")
            print(f"- Total de enlaces extra: {total_extra_links}")
            
            # Mostrar ejemplo del primer episodio
            if data['episodes']:
                first_ep = data['episodes'][0]
                print(f"\nEjemplo del episodio {first_ep['episode_number']}:")
                print(f"- URL web: {first_ep['web_url']}")
                print(f"- URL descarga: {first_ep['download_url']}")
                print(f"- Canciones en playlist: {len(first_ep['playlist'])}")
                if first_ep['playlist']:
                    print(f"- Primera canción: {first_ep['playlist'][0]['artist']} - {first_ep['playlist'][0]['song']}")
        else:
            print("Error al guardar los datos")
    else:
        print("Error al extraer los datos del RSS")

if __name__ == "__main__":
    main()

