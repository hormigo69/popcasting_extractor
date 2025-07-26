#!/usr/bin/env python3
"""
Extractor corregido de datos del podcast Popcasting
Maneja correctamente los separadores de canciones
"""

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime

import requests


def clean_text(text):
    """Limpia texto de caracteres especiales y espacios extra"""
    if not text:
        return ""

    # Reemplazar caracteres especiales comunes
    text = text.replace("Â·", "·")
    text = text.replace("Â", "")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')

    # Limpiar espacios extra
    text = " ".join(text.split())

    return text.strip()


def parse_playlist_improved(description):
    """
    Parser mejorado que maneja correctamente los separadores
    """
    if not description:
        return []

    # Limpiar el texto
    description = clean_text(description)

    # Remover enlaces y texto extra al final
    # Buscar patrones de enlaces
    link_patterns = [
        r"https?://[^\s]+",
        r"::::+.*$",  # Múltiples dos puntos seguidos
        r"invita a Popcasting.*$",
        r"flor de pasión.*$",
        r"mu favourite.*$",
        r"las felindras.*$",
        r"revisionist history.*$",
    ]

    for pattern in link_patterns:
        description = re.sub(pattern, "", description, flags=re.IGNORECASE)

    # Dividir por el separador principal ::
    parts = description.split(" :: ")

    playlist = []
    position = 1

    for part in parts:
        part = clean_text(part)
        if not part:
            continue

        # Verificar si la parte contiene el separador artista-canción
        if " · " in part:
            # Dividir en artista y canción
            try:
                artist, song = part.split(" · ", 1)
                artist = clean_text(artist)
                song = clean_text(song)

                # Verificar que tanto artista como canción no estén vacíos
                if artist and song:
                    # Verificar que no sean enlaces o texto extraño
                    if not any(
                        x in artist.lower() for x in ["http", "www", ".com", "::::"]
                    ):
                        if not any(
                            x in song.lower() for x in ["http", "www", ".com", "::::"]
                        ):
                            playlist.append(
                                {"position": position, "artist": artist, "song": song}
                            )
                            position += 1
            except ValueError:
                # Si hay múltiples ' · ' en la parte, tomar solo la primera división
                parts_split = part.split(" · ")
                if len(parts_split) >= 2:
                    artist = clean_text(parts_split[0])
                    song = clean_text(" · ".join(parts_split[1:]))

                    if artist and song:
                        if not any(
                            x in artist.lower() for x in ["http", "www", ".com", "::::"]
                        ):
                            if not any(
                                x in song.lower()
                                for x in ["http", "www", ".com", "::::"]
                            ):
                                playlist.append(
                                    {
                                        "position": position,
                                        "artist": artist,
                                        "song": song,
                                    }
                                )
                                position += 1
        else:
            # Si no tiene separador artista-canción, podría ser texto extra
            # Solo incluir si parece ser una canción válida (no enlaces ni texto extraño)
            if not any(
                x in part.lower() for x in ["http", "www", ".com", "::::", "invita a"]
            ):
                if len(part) > 3 and len(part) < 200:  # Longitud razonable
                    # Intentar detectar si es "artista canción" sin separador
                    words = part.split()
                    if len(words) >= 2:
                        # Asumir que las primeras palabras son el artista
                        mid_point = len(words) // 2
                        artist = " ".join(words[:mid_point])
                        song = " ".join(words[mid_point:])

                        playlist.append(
                            {"position": position, "artist": artist, "song": song}
                        )
                        position += 1

    return playlist


def extract_extra_links(description):
    """Extrae enlaces extra de la descripción"""
    if not description:
        return []

    links = []

    # Patrones para diferentes tipos de enlaces
    patterns = [
        r"https://ko-fi\.com/[^\s]+",
        r"https://youtu\.be/[^\s]+",
        r"http://[^\s]+",
        r"https://[^\s]+",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, description)
        for match in matches:
            # Limpiar el enlace
            link = match.rstrip(".,;:)]")
            if link not in links:
                links.append(link)

    return links


def extract_episode_number(title):
    """Extrae el número de episodio del título"""
    if not title:
        return None

    # Buscar patrón "Popcasting" seguido de números
    match = re.search(r"Popcasting(\d+)", title, re.IGNORECASE)
    if match:
        return int(match.group(1))

    return None


def main():
    print("Extrayendo datos del RSS de Popcasting (versión corregida)...")

    # Descargar el RSS
    rss_url = "https://feeds.feedburner.com/Popcasting"

    try:
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error al descargar el RSS: {e}")
        return

    # Parsear el XML
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"Error al parsear el XML: {e}")
        return

    # Extraer información del canal
    channel = root.find("channel")
    if channel is None:
        print("No se encontró el elemento 'channel' en el RSS")
        return

    podcast_name = (
        channel.find("title").text
        if channel.find("title") is not None
        else "Popcasting"
    )

    # Extraer episodios
    episodes = []
    items = channel.findall("item")

    print(f"Procesando {len(items)} episodios...")

    for item in items:
        title_elem = item.find("title")
        title = title_elem.text if title_elem is not None else ""

        episode_number = extract_episode_number(title)
        if episode_number is None:
            continue

        # Enlaces
        link_elem = item.find("link")
        web_url = link_elem.text if link_elem is not None else ""

        enclosure_elem = item.find("enclosure")
        download_url = enclosure_elem.get("url") if enclosure_elem is not None else ""

        # Descripción
        description_elem = item.find("description")
        description = description_elem.text if description_elem is not None else ""

        # Parsear playlist
        playlist = parse_playlist_improved(description)

        # Enlaces extra
        extra_links = extract_extra_links(description)

        # Fecha de publicación
        pub_date_elem = item.find("pubDate")
        pub_date = pub_date_elem.text if pub_date_elem is not None else ""

        # Duración
        duration_elem = item.find(
            "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration"
        )
        duration = duration_elem.text if duration_elem is not None else ""

        # GUID
        guid_elem = item.find("guid")
        guid = guid_elem.text if guid_elem is not None else ""

        episode_data = {
            "title": title,
            "episode_number": episode_number,
            "web_url": web_url,
            "download_url": download_url,
            "playlist": playlist,
            "extra_links": extra_links,
            "publication_date": pub_date,
            "duration": duration,
            "guid": guid,
        }

        episodes.append(episode_data)

        if len(episodes) % 50 == 0:
            print(f"Procesados {len(episodes)} episodios...")

    # Ordenar episodios por número (descendente)
    episodes.sort(key=lambda x: x["episode_number"], reverse=True)

    # Calcular estadísticas
    total_songs = sum(len(ep["playlist"]) for ep in episodes)
    total_extra_links = sum(len(ep["extra_links"]) for ep in episodes)

    # Crear estructura final
    data = {
        "podcast_name": podcast_name,
        "rss_url": rss_url,
        "extraction_date": datetime.now().isoformat(),
        "total_episodes": len(episodes),
        "total_songs": total_songs,
        "total_extra_links": total_extra_links,
        "episodes": episodes,
    }

    # Guardar en JSON
    output_file = "popcasting_data_fixed.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n✅ Extracción completada!")
    print(f"📁 Archivo guardado: {output_file}")
    print("📊 Estadísticas:")
    print(f"   - Episodios: {len(episodes)}")
    print(f"   - Canciones: {total_songs}")
    print(f"   - Enlaces extra: {total_extra_links}")

    # Mostrar ejemplo del episodio 317 corregido
    ep_317 = next((ep for ep in episodes if ep["episode_number"] == 317), None)
    if ep_317:
        print("\n🔍 Ejemplo del episodio 317 corregido:")
        print(f"   - Canciones encontradas: {len(ep_317['playlist'])}")
        for i, song in enumerate(ep_317["playlist"][:5]):
            print(f"   {i+1}. {song['artist']} · {song['song']}")
        if len(ep_317["playlist"]) > 5:
            print(f"   ... y {len(ep_317['playlist']) - 5} más")


if __name__ == "__main__":
    main()
