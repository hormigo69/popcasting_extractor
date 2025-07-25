import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from dotenv import load_dotenv
from supabase_database import get_supabase_connection

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))


#!/usr/bin/env python3
"""
Script para corregir el episodio #92 con la playlist CORRECTA.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def fix_episode_92_correct():
    """
    Corrige el episodio #92 con la playlist CORRECTA de 12 canciones.
    """
    print("🔧 Corrigiendo episodio #92 con la playlist CORRECTA...")

    # Playlist CORRECTA del episodio #92 (proporcionada por el usuario)
    playlist_92_correct = [
        {"position": 1, "artist": "j.j. cale", "title": "city girls"},
        {"position": 2, "artist": "j.j. cale", "title": "drifters wife"},
        {"position": 3, "artist": "the tornadoes", "title": "the ice cream man"},
        {
            "position": 4,
            "artist": "hank williams",
            "title": "my bucket's got a hole in it",
        },
        {
            "position": 5,
            "artist": "cliff richard and the shadows",
            "title": "i'm gonna get you",
        },
        {"position": 6, "artist": "abc", "title": "poison arrow"},
        {
            "position": 7,
            "artist": "gabinete caligari",
            "title": "me tengo que concentrar",
        },
        {"position": 8, "artist": "the morning benders", "title": "waiting for a war"},
        {"position": 9, "artist": "cheap trick", "title": "the dream police"},
        {"position": 10, "artist": "larry wallis", "title": "police car"},
        {"position": 11, "artist": "the ronettes", "title": "walking in the rain"},
        {"position": 12, "artist": "snooks eaglin", "title": "funky malagueña"},
    ]

    try:
        # Obtener el episodio #92 de la base de datos
        db = get_supabase_connection()
        response = (
            db.client.table("podcasts")
            .select("id, program_number, title, date, web_playlist, web_songs_count")
            .eq("program_number", 92)
            .execute()
        )

        if not response.data:
            print("❌ Episodio #92 no encontrado en la base de datos")
            return False

        episode = response.data[0]
        print(
            f"📋 Episodio encontrado: #{episode['program_number']} | {episode['title']}"
        )
        print(f"   Canciones actuales: {episode['web_songs_count']}")

        # Mostrar la playlist actual para comparar
        current_playlist = episode.get("web_playlist")
        if current_playlist:
            try:
                current = json.loads(current_playlist)
                print("   Playlist actual (primeras 3 canciones):")
                for i, song in enumerate(current[:3]):
                    print(
                        f"     {i+1}. {song.get('artist', 'N/A')} - {song.get('title', 'N/A')}"
                    )
            except Exception:
                print(f"   Playlist actual: {current_playlist[:100]}...")

        # Actualizar la playlist con la CORRECTA
        db.update_web_info(
            podcast_id=episode["id"],
            web_playlist=json.dumps(playlist_92_correct, ensure_ascii=False),
            web_songs_count=len(playlist_92_correct),
        )

        print(
            f"✅ Episodio #92 corregido con la playlist CORRECTA: {len(playlist_92_correct)} canciones"
        )
        print("📝 Playlist CORRECTA:")
        for song in playlist_92_correct:
            print(f"   {song['position']}. {song['artist']} - {song['title']}")

        return True

    except Exception as e:
        print(f"❌ Error corrigiendo episodio #92: {e}")
        return False


def main():
    """
    Función principal.
    """
    print("🎵 Corregidor del episodio #92 con playlist CORRECTA")
    print("=" * 50)

    success = fix_episode_92_correct()

    if success:
        print("\n🎉 Episodio #92 corregido con la playlist CORRECTA!")
    else:
        print("\n❌ Error corrigiendo el episodio #92")


if __name__ == "__main__":
    main()
