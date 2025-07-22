import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase_database import get_supabase_connection

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))


#!/usr/bin/env python3
"""
Script de prueba para extraer playlist de un episodio específico desde WordPress.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def get_episode_by_number(program_number):
    """
    Obtiene un episodio específico por número.
    """
    try:
        db = get_supabase_connection()
        response = (
            db.client.table("podcasts")
            .select(
                "id, program_number, title, date, web_playlist, web_songs_count, wordpress_url"
            )
            .eq("program_number", program_number)
            .execute()
        )

        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error obteniendo episodio: {e}")
        return None


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
        print(f"❌ Error obteniendo contenido: {e}")
        return None


def extract_playlist_from_html_v3(html_content):
    """
    Extrae playlist del contenido HTML usando el formato específico de Popcasting.
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
            if "::" in line and "·" in line:
                # Dividir por ::
                parts = line.split("::")
                for i, part in enumerate(parts, 1):
                    part = part.strip()
                    if "·" in part:
                        artist_title = part.split("·", 1)
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

        # Si no encontramos nada con el método anterior, usar regex
        if not songs:
            # Buscar el patrón específico: artista · título :: artista · título :: ...
            pattern = r"([a-zA-Z0-9\s&\'\-\.]+)\s*·\s*([a-zA-Z0-9\s&\'\-\.\(\)]+)(?:\s*::\s*|$)"

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
        print(f"❌ Error procesando HTML: {e}")
        return []


def main():
    """
    Función principal.
    """
    print("🎵 Extractor de playlist desde WordPress (Prueba v3)")
    print("=" * 55)

    # Probar con el episodio #143 que sabemos que tiene playlist
    program_number = 143

    episode = get_episode_by_number(program_number)
    if not episode:
        print(f"❌ Episodio #{program_number} no encontrado")
        return

    print(f"📋 Episodio #{episode['program_number']} | {episode['title']}")
    print(f"   Canciones actuales: {episode['web_songs_count']}")
    print(f"   URL: {episode['wordpress_url']}")

    # Obtener contenido HTML
    html_content = fetch_wordpress_content(episode["wordpress_url"])
    if not html_content:
        print("❌ No se pudo obtener contenido")
        return

    print(f"✅ Contenido HTML obtenido ({len(html_content)} caracteres)")

    # Extraer playlist
    extracted_songs = extract_playlist_from_html_v3(html_content)

    if not extracted_songs:
        print("❌ No se encontraron canciones en el HTML")
        return

    print(f"✅ Extraídas {len(extracted_songs)} canciones")
    print()
    print("📝 Canciones encontradas:")
    for i, song in enumerate(extracted_songs, 1):
        print(f"   {i:2d}. {song['artist']} - {song['title']}")


if __name__ == "__main__":
    main()
