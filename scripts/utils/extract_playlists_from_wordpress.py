import json
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from supabase_database import get_supabase_connection

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))


#!/usr/bin/env python3
"""
Script para extraer playlists desde las URLs de WordPress de episodios con pocas canciones.
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


def extract_playlist_from_html(html_content):
    """
    Extrae playlist del contenido HTML usando múltiples patrones.
    """
    songs = []

    # Convertir a minúsculas para búsqueda
    html_content.lower()

    # Patrones para encontrar playlists
    patterns = [
        # Patrón: artista • título
        r"([a-z0-9\s&\'\-\.]+)\s*•\s*([a-z0-9\s&\'\-\.]+)",
        # Patrón: artista - título
        r"([a-z0-9\s&\'\-\.]+)\s*-\s*([a-z0-9\s&\'\-\.]+)",
        # Patrón: artista "título"
        r'([a-z0-9\s&\'\-\.]+)\s*["\']([a-z0-9\s&\'\-\.]+)["\']',
        # Patrón: artista: título
        r"([a-z0-9\s&\'\-\.]+)\s*:\s*([a-z0-9\s&\'\-\.]+)",
    ]

    # Buscar en el contenido HTML
    for pattern in patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for i, (artist, title) in enumerate(matches, 1):
            artist = artist.strip()
            title = title.strip()

            # Filtrar resultados válidos
            if (
                len(artist) > 2
                and len(title) > 2
                and not artist.startswith("http")
                and not title.startswith("http")
                and not any(
                    word in artist.lower()
                    for word in ["popcasting", "ivoox", "wordpress", "podcast"]
                )
                and not any(
                    word in title.lower()
                    for word in ["popcasting", "ivoox", "wordpress", "podcast"]
                )
            ):
                songs.append({"position": i, "artist": artist, "title": title})

    # Si no encontramos nada con patrones, buscar líneas que parezcan canciones
    if not songs:
        lines = html_content.split("\n")
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if (
                len(line) > 10
                and (" - " in line or "•" in line or ":" in line)
                and not line.startswith("http")
                and not any(
                    word in line.lower()
                    for word in [
                        "popcasting",
                        "ivoox",
                        "wordpress",
                        "podcast",
                        "html",
                        "script",
                    ]
                )
            ):
                # Intentar separar artista y título
                if " - " in line:
                    parts = line.split(" - ", 1)
                    if len(parts) == 2:
                        artist, title = parts
                        songs.append(
                            {
                                "position": i,
                                "artist": artist.strip(),
                                "title": title.strip(),
                            }
                        )
                elif "•" in line:
                    parts = line.split("•", 1)
                    if len(parts) == 2:
                        artist, title = parts
                        songs.append(
                            {
                                "position": i,
                                "artist": artist.strip(),
                                "title": title.strip(),
                            }
                        )

    return songs


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


def process_episode(episode):
    """
    Procesa un episodio para extraer su playlist desde WordPress.
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
    extracted_songs = extract_playlist_from_html(html_content)

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

    # Preguntar si actualizar
    print("   🤔 ¿Actualizar playlist? (s/n): ", end="")
    response = input().lower().strip()

    if response in ["s", "si", "sí", "y", "yes"]:
        if update_episode_playlist(episode, extracted_songs):
            print(
                f"   ✅ Playlist actualizada: {episode['web_songs_count']} → {len(extracted_songs)} canciones"
            )
            return True
        else:
            print("   ❌ Error actualizando playlist")
            return False
    else:
        print("   ⚠️  Playlist no actualizada")
        return False


def main():
    """
    Función principal.
    """
    print("🎵 Extractor de playlists desde WordPress")
    print("=" * 45)

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
        if process_episode(episode):
            updated_count += 1
        print()

    print("🎉 Resumen:")
    print(f"   Episodios procesados: {len(episodes)}")
    print(f"   Playlists actualizadas: {updated_count}")


if __name__ == "__main__":
    main()
