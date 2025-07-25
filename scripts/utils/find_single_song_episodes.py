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
Script para encontrar episodios con solo 1 canción.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def find_single_song_episodes():
    """
    Encuentra todos los episodios con solo 1 canción.
    """
    print("🔍 Buscando episodios con solo 1 canción...")

    try:
        db = get_supabase_connection()
        response = (
            db.client.table("podcasts")
            .select(
                "id, program_number, title, date, web_playlist, web_songs_count, wordpress_url"
            )
            .eq("web_songs_count", 1)
            .order("program_number")
            .execute()
        )

        episodes = response.data

        if not episodes:
            print("✅ No hay episodios con solo 1 canción.")
            return []

        print(f"\n📊 Encontrados {len(episodes)} episodios con solo 1 canción:")
        print("=" * 60)

        for episode in episodes:
            print(
                f"\n🎵 #{episode['program_number']} | {episode['date']} | {episode['title']}"
            )

            # Mostrar la canción
            playlist_json = episode.get("web_playlist")
            if playlist_json:
                try:
                    playlist = json.loads(playlist_json)
                    if playlist:
                        song = playlist[0]
                        artist = song.get("artist", "N/A")
                        title = song.get("title", "N/A")
                        print(f"   🎶 {artist} - {title}")

                        # Verificar si contiene múltiples canciones concatenadas
                        if "::" in artist or "::" in title:
                            print(
                                "   ⚠️  POSIBLE ERROR: Contiene múltiples canciones concatenadas"
                            )
                            if "::" in artist:
                                songs_count = artist.count("::") + 1
                                print(
                                    f"      Canciones detectadas en artista: {songs_count}"
                                )
                            if "::" in title:
                                songs_count = title.count("::") + 1
                                print(
                                    f"      Canciones detectadas en título: {songs_count}"
                                )
                except Exception:
                    print(f"   ❌ Error parseando playlist: {playlist_json[:100]}...")
            else:
                print("   ❌ No tiene playlist")

            if episode.get("wordpress_url"):
                print(f"   🔗 {episode['wordpress_url']}")

        return episodes

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def main():
    """
    Función principal.
    """
    print("🎵 Buscador de episodios con solo 1 canción")
    print("=" * 50)

    episodes = find_single_song_episodes()

    if episodes:
        print("\n📋 Resumen:")
        print(f"   Total de episodios con 1 canción: {len(episodes)}")
        print(
            f"   Episodios: {', '.join([f'#{ep['program_number']}' for ep in episodes])}"
        )


if __name__ == "__main__":
    main()
