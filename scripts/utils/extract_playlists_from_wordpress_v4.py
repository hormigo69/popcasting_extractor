import json
import os
import re
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase_database import get_supabase_connection

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))


#!/usr/bin/env python3
"""
Script mejorado para extraer playlists desde WordPress que detecta ambos formatos de separadores.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def get_low_songs_episodes():
    """
    Obtiene episodios con 8 canciones o menos que tienen wordpress_url.
    """
    try:
        db = get_supabase_connection()
        response = (
            db.client.table("podcasts")
            .select(
                "id, program_number, title, date, web_playlist, web_songs_count, wordpress_url"
            )
            .lte("web_songs_count", 8)
            .not_.is_("wordpress_url", "null")
            .order("program_number")
            .execute()
        )

        return response.data
    except Exception as e:
        print(f"❌ Error obteniendo episodios: {e}")
        return []


def extract_playlist_from_html_v4(html_content):
    """
    Extrae playlist del contenido HTML usando ambos formatos de separadores (• y ·).
    """
    songs = []

    try:
        # Usar BeautifulSoup para parsear HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Obtener todo el texto
        text_content = soup.get_text()

        # Buscar líneas que contengan múltiples canciones separadas por ::
        lines = text_content.split("\n")
        for line in lines:
            line = line.strip()

            # Buscar líneas que contengan múltiples canciones separadas por ::
            if "::" in line and ("•" in line or "·" in line):
                # Dividir por ::
                parts = line.split("::")
                for i, part in enumerate(parts, 1):
                    part = part.strip()

                    # Buscar ambos formatos de separadores
                    if "•" in part:
                        artist_title = part.split("•", 1)
                    elif "·" in part:
                        artist_title = part.split("·", 1)
                    else:
                        continue

                    if len(artist_title) == 2:
                        artist, title = artist_title
                        artist = artist.strip()
                        title = title.strip()

                        # Filtrar resultados válidos
                        if (
                            len(artist) > 2
                            and len(title) > 2
                            and len(artist) < 100
                            and len(title) < 100
                            and not artist.isdigit()
                            and not title.isdigit()
                            and not any(
                                word in artist.lower()
                                for word in [
                                    "popcasting",
                                    "ivoox",
                                    "wordpress",
                                    "podcast",
                                    "download",
                                    "rss",
                                ]
                            )
                            and not any(
                                word in title.lower()
                                for word in [
                                    "popcasting",
                                    "ivoox",
                                    "wordpress",
                                    "podcast",
                                    "download",
                                    "rss",
                                ]
                            )
                        ):
                            songs.append(
                                {"position": i, "artist": artist, "title": title}
                            )

        # Si no encontramos nada con el método anterior, usar regex para ambos formatos
        if not songs:
            # Buscar el patrón específico: artista • título :: artista · título :: ...
            patterns = [
                r"([a-zA-Z0-9\s&\'\-\.]+)\s*•\s*([a-zA-Z0-9\s&\'\-\.\(\)]+)(?:\s*::\s*|$)",
                r"([a-zA-Z0-9\s&\'\-\.]+)\s*·\s*([a-zA-Z0-9\s&\'\-\.\(\)]+)(?:\s*::\s*|$)",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text_content)

                for i, (artist, title) in enumerate(matches, 1):
                    artist = artist.strip()
                    title = title.strip()

                    # Filtrar resultados válidos
                    if (
                        len(artist) > 2
                        and len(title) > 2
                        and len(artist) < 100
                        and len(title) < 100
                        and not artist.isdigit()
                        and not title.isdigit()
                        and not any(
                            word in artist.lower()
                            for word in [
                                "popcasting",
                                "ivoox",
                                "wordpress",
                                "podcast",
                                "download",
                                "rss",
                            ]
                        )
                        and not any(
                            word in title.lower()
                            for word in [
                                "popcasting",
                                "ivoox",
                                "wordpress",
                                "podcast",
                                "download",
                                "rss",
                            ]
                        )
                    ):
                        songs.append({"position": i, "artist": artist, "title": title})

        # Filtrar duplicados
        unique_songs = []
        seen = set()
        for song in songs:
            key = f"{song['artist'].lower()}-{song['title'].lower()}"
            if key not in seen:
                seen.add(key)
                unique_songs.append(song)

        return unique_songs[:50]  # Limitar a 50 canciones máximo

    except Exception as e:
        print(f"   ❌ Error procesando HTML: {e}")
        return []


def fetch_wordpress_content(wordpress_url):
    """
    Obtiene el contenido HTML de una URL de WordPress.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(wordpress_url, headers=headers, timeout=10)
        response.raise_for_status()

        return response.text
    except Exception as e:
        print(f"   ❌ Error obteniendo contenido: {e}")
        return None


def update_episode_playlist(episode, new_playlist):
    """
    Actualiza la playlist de un episodio en la base de datos.
    """
    try:
        db = get_supabase_connection()
        db.update_web_info(
            podcast_id=episode["id"],
            web_playlist=json.dumps(new_playlist, ensure_ascii=False),
            web_songs_count=len(new_playlist),
        )
        return True
    except Exception as e:
        print(f"   ❌ Error actualizando base de datos: {e}")
        return False


def process_episode_auto(episode):
    """
    Procesa un episodio para extraer su playlist desde WordPress (automático).
    """
    print(f"📋 Episodio #{episode['program_number']} | {episode['title']}")
    print(f"   Canciones actuales: {episode['web_songs_count']}")
    print(f"   URL: {episode['wordpress_url']}")

    # Obtener contenido HTML
    html_content = fetch_wordpress_content(episode["wordpress_url"])
    if not html_content:
        print("   ❌ No se pudo obtener contenido")
        return False

    # Extraer playlist
    extracted_songs = extract_playlist_from_html_v4(html_content)

    if not extracted_songs:
        print("   ❌ No se encontraron canciones en el HTML")
        return False

    print(f"   ✅ Extraídas {len(extracted_songs)} canciones")

    # Mostrar primeras canciones
    print("   📝 Primeras canciones:")
    for i, song in enumerate(extracted_songs[:5], 1):
        print(f"     {i}. {song['artist']} - {song['title']}")

    if len(extracted_songs) > 5:
        print(f"     ... y {len(extracted_songs) - 5} más")

    # Solo actualizar si encontramos más canciones que las actuales
    if len(extracted_songs) > episode["web_songs_count"]:
        if update_episode_playlist(episode, extracted_songs):
            print(
                f"   ✅ Playlist actualizada: {episode['web_songs_count']} → {len(extracted_songs)} canciones (+{len(extracted_songs) - episode['web_songs_count']})"
            )
            return True
        else:
            print("   ❌ Error actualizando playlist")
            return False
    else:
        print("   ⚠️  No se encontraron más canciones que las actuales")
        return False


def main():
    """
    Función principal.
    """
    print("🎵 Extractor mejorado de playlists desde WordPress (v4)")
    print("=" * 60)

    episodes = get_low_songs_episodes()

    if not episodes:
        print("✅ No hay episodios con pocas canciones que tengan wordpress_url.")
        return

    print(
        f"🔍 Encontrados {len(episodes)} episodios con pocas canciones y wordpress_url"
    )
    print()

    updated_count = 0

    for episode in episodes:
        print("-" * 50)
        if process_episode_auto(episode):
            updated_count += 1
        print()

    print("🎉 Resumen:")
    print(f"   Episodios procesados: {len(episodes)}")
    print(f"   Playlists actualizadas: {updated_count}")


if __name__ == "__main__":
    main()
