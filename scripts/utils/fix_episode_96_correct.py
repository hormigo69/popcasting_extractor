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
Script para corregir el episodio #96 con la playlist CORRECTA.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def fix_episode_96_correct():
    """
    Corrige el episodio #96 con la playlist CORRECTA de 11 canciones.
    """
    print("🔧 Corrigiendo episodio #96 con la playlist CORRECTA...")

    # Playlist CORRECTA del episodio #96 (proporcionada por el usuario)
    playlist_96_correct = [
        {"position": 1, "artist": "dolly parton", "title": "jolene"},
        {"position": 2, "artist": "eels", "title": "my timing is off"},
        {"position": 3, "artist": "bat for lashes", "title": "a forest"},
        {
            "position": 4,
            "artist": "siouxie and the banshees",
            "title": "hong kong garden",
        },
        {"position": 5, "artist": "peaches", "title": "lose you"},
        {"position": 6, "artist": "johnny legend", "title": "green light"},
        {"position": 7, "artist": "asobi seksu", "title": "transparence"},
        {
            "position": 8,
            "artist": "little boots",
            "title": "new in town (no one is safe · al kapranos remix)",
        },
        {
            "position": 9,
            "artist": "mickey and silvia",
            "title": "love is strange (take 4)",
        },
        {"position": 10, "artist": "the coasters", "title": "i'm a hog for you"},
        {"position": 11, "artist": "johnny burnette trio", "title": "honey hush"},
    ]

    try:
        # Obtener el episodio #96 de la base de datos
        db = get_supabase_connection()
        response = (
            db.client.table("podcasts")
            .select("id, program_number, title, date, web_playlist, web_songs_count")
            .eq("program_number", 96)
            .execute()
        )

        if not response.data:
            print("❌ Episodio #96 no encontrado en la base de datos")
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
            web_playlist=json.dumps(playlist_96_correct, ensure_ascii=False),
            web_songs_count=len(playlist_96_correct),
        )

        print(
            f"✅ Episodio #96 corregido con la playlist CORRECTA: {len(playlist_96_correct)} canciones"
        )
        print("📝 Playlist CORRECTA:")
        for song in playlist_96_correct:
            print(f"   {song['position']}. {song['artist']} - {song['title']}")

        return True

    except Exception as e:
        print(f"❌ Error corrigiendo episodio #96: {e}")
        return False


def main():
    """
    Función principal.
    """
    print("🎵 Corregidor del episodio #96 con playlist CORRECTA")
    print("=" * 50)

    success = fix_episode_96_correct()

    if success:
        print("\n🎉 Episodio #96 corregido con la playlist CORRECTA!")
    else:
        print("\n❌ Error corrigiendo el episodio #96")


if __name__ == "__main__":
    main()
