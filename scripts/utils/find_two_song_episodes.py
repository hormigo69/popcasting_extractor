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
Script para encontrar episodios con solo 2 canciones.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def get_two_song_episodes():
    """
    Obtiene episodios con solo 2 canciones.
    """
    try:
        db = get_supabase_connection()
        response = (
            db.client.table("podcasts")
            .select("id, program_number, title, date, web_playlist, web_songs_count")
            .eq("web_songs_count", 2)
            .order("program_number")
            .execute()
        )

        return response.data
    except Exception as e:
        print(f"❌ Error obteniendo episodios: {e}")
        return []


def analyze_two_song_episodes():
    """
    Analiza episodios con solo 2 canciones.
    """
    print("🎵 Buscador de episodios con solo 2 canciones")
    print("=" * 50)

    episodes = get_two_song_episodes()

    if not episodes:
        print("✅ No hay episodios con solo 2 canciones.")
        return

    print(f"🔍 Encontrados {len(episodes)} episodios con solo 2 canciones:")
    print()

    for episode in episodes:
        print(f"📋 Episodio #{episode['program_number']} | {episode['title']}")
        print(f"   Fecha: {episode['date']}")
        print(f"   Canciones: {episode['web_songs_count']}")

        # Mostrar las canciones actuales
        playlist = episode.get("web_playlist")
        if playlist:
            try:
                songs = json.loads(playlist)
                print("   Playlist actual:")
                for i, song in enumerate(songs, 1):
                    artist = song.get("artist", "N/A")
                    title = song.get("title", "N/A")
                    print(f"     {i}. {artist} - {title}")

                    # Verificar si hay canciones concatenadas
                    if "::" in title or "•" in title or " - " in title:
                        print("       ⚠️  POSIBLE CANCIÓN CONCATENADA")

            except json.JSONDecodeError:
                print(f"   Playlist (JSON inválido): {playlist[:100]}...")
        else:
            print("   Sin playlist")

        print("-" * 40)


def main():
    """
    Función principal.
    """
    analyze_two_song_episodes()


if __name__ == "__main__":
    main()
