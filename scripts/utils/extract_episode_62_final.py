#!/usr/bin/env python3
"""
import json
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

        import sys
        from pathlib import Path
        from dotenv import load_dotenv
        from config import DATABASE_TYPE
        from database import get_db_connection, initialize_database
        from supabase_database import get_supabase_connection

        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

Script final para extraer la playlist del episodio #62 del archivo HTML.
"""


def extract_episode_62_playlist():
    """
    Extrae la playlist del episodio #62 del archivo HTML.
    """
    html_file = Path("data/42-63.html")

    if not html_file.exists():
        print(f"❌ Archivo {html_file} no encontrado")
        return None

    print("📄 Extrayendo playlist del episodio #62...")

    # Leer el archivo línea por línea
    with open(html_file, encoding="utf-8") as f:
        lines = f.readlines()

    # Buscar la línea con "programa #62"
    episode_line = None
    for i, line in enumerate(lines):
        if "programa #62" in line.lower():
            episode_line = i
            break

    if episode_line is None:
        print("❌ No se encontró el episodio #62")
        return None

    print(f"✅ Episodio #62 encontrado en línea {episode_line + 1}")

    # Buscar la playlist en las líneas siguientes
    playlist_text = None
    for i in range(episode_line, min(episode_line + 10, len(lines))):
        line = lines[i].strip()

        # Buscar la línea que contiene la playlist (después de la fecha)
        if "lykke li" in line.lower() and "::" in line:
            playlist_text = line
            break

    if not playlist_text:
        print("❌ No se encontró la playlist del episodio #62")
        return None

    print(f"🎵 Playlist encontrada: {playlist_text[:100]}...")

    # Extraer canciones separadas por ::
    songs = []
    parts = playlist_text.split("::")

    for i, part in enumerate(parts):
        part = part.strip()
        if part:
            # Intentar separar artista y título
            if " · " in part:
                artist, title = part.split(" · ", 1)
            elif " - " in part:
                artist, title = part.split(" - ", 1)
            else:
                artist = part
                title = ""

            songs.append(
                {"position": i + 1, "artist": artist.strip(), "title": title.strip()}
            )

    print(f"🎵 Canciones extraídas: {len(songs)}")

    # Mostrar las canciones
    print("\n📋 Playlist del episodio #62:")
    print("-" * 40)
    for song in songs:
        print(f"  {song['position']:2d}. {song['artist']} - {song['title']}")

    return songs


def update_episode_62_in_database(songs):
    """
    Actualiza el episodio #62 en la base de datos con la playlist extraída.
    """
    try:
        # Cargar variables de entorno
        load_dotenv()

        # Añadir el directorio raíz al path para importar los módulos
        sys.path.append(str(Path(__file__).parent.parent.parent))

        # Importar directamente los módulos

        if DATABASE_TYPE == "supabase":
            db = get_supabase_connection()

            # Buscar el episodio #62
            response = (
                db.client.table("podcasts")
                .select("id")
                .eq("program_number", 62)
                .execute()
            )

            if not response.data:
                print("❌ Episodio #62 no encontrado en la base de datos")
                return False

            podcast_id = response.data[0]["id"]

            # Actualizar con la playlist y el número de canciones
            db.update_web_info(
                podcast_id=podcast_id,
                web_playlist=json.dumps(songs),
                web_songs_count=len(songs),
            )

        else:
            initialize_database()
            conn = get_db_connection()
            cursor = conn.cursor()

            # Buscar el episodio #62
            cursor.execute("SELECT id FROM podcasts WHERE program_number = ?", (62,))
            result = cursor.fetchone()

            if not result:
                print("❌ Episodio #62 no encontrado en la base de datos")
                return False

            podcast_id = result[0]

            # Actualizar con la playlist y el número de canciones
            cursor.execute(
                """
                UPDATE podcasts
                SET web_playlist = ?, web_songs_count = ?
                WHERE id = ?
            """,
                (json.dumps(songs), len(songs), podcast_id),
            )

            conn.commit()
            conn.close()

        print(f"✅ Episodio #62 actualizado exitosamente con {len(songs)} canciones")
        return True

    except Exception as e:
        print(f"❌ Error actualizando episodio #62: {e}")
        return False


def main():
    """Función principal del script."""
    print("🎵 Extractor final de playlist del episodio #62")
    print("=" * 50)

    # Extraer playlist del HTML
    songs = extract_episode_62_playlist()

    if songs:
        print("\n🔄 Actualizando base de datos...")
        success = update_episode_62_in_database(songs)

        if success:
            print("\n🎉 ¡Episodio #62 completado exitosamente!")
            print(f"📊 Ahora tenemos {len(songs)} canciones para el episodio #62")
        else:
            print("\n❌ Error al actualizar la base de datos")
    else:
        print("\n❌ No se pudo extraer la playlist del episodio #62")


if __name__ == "__main__":
    main()
