import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase_database import get_supabase_connection

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))


#!/usr/bin/env python3
"""
Script mejorado para corregir el parsing de playlists.
Analiza el contenido actual y separa correctamente las canciones concatenadas.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def get_low_songs_episodes():
    """
    Obtiene episodios con 8 canciones o menos para corregir.
    """
    db = get_supabase_connection()
    response = (
        db.client.table("podcasts")
        .select(
            "id, program_number, title, date, web_playlist, web_songs_count, wordpress_url"
        )
        .not_.is_("web_songs_count", "null")
        .lte("web_songs_count", 8)
        .order("web_songs_count", desc=True)
        .execute()
    )

    return response.data


def fix_playlist_parsing(playlist_json):
    """
    Corrige el parsing de una playlist que tiene canciones concatenadas.
    """
    try:
        playlist = json.loads(playlist_json)
        if len(playlist) <= 3:  # Solo procesar playlists cortas
            return None

        # Buscar el elemento que contiene múltiples canciones
        for _i, song in enumerate(playlist):
            artist = song.get("artist", "")
            song.get("title", "")

            # Si el artista contiene múltiples canciones separadas por ::
            if "::" in artist:
                songs_raw = artist.split("::")
                new_songs = []

                for _j, song_raw in enumerate(songs_raw):
                    song_raw = song_raw.strip()
                    if len(song_raw) < 5:
                        continue

                    # Separar artista y título
                    if " • " in song_raw:
                        parts = song_raw.split(" • ", 1)
                        new_artist = parts[0].strip()
                        new_title = parts[1].strip() if len(parts) > 1 else ""
                    elif " - " in song_raw:
                        parts = song_raw.split(" - ", 1)
                        new_artist = parts[0].strip()
                        new_title = parts[1].strip() if len(parts) > 1 else ""
                    else:
                        new_artist = song_raw
                        new_title = ""

                    # Filtrar entradas no válidas
                    if any(
                        keyword in new_artist.lower()
                        for keyword in [
                            "http",
                            "comparte",
                            "haz clic",
                            "facebook",
                            "twitter",
                            "ivoox",
                            "blip.tv",
                        ]
                    ):
                        continue

                    if len(new_artist) > 3 and len(new_artist) < 100:
                        new_songs.append(
                            {
                                "position": len(new_songs) + 1,
                                "artist": new_artist,
                                "title": new_title,
                            }
                        )

                if len(new_songs) >= 5:  # Al menos 5 canciones para considerar válido
                    return new_songs

        return None

    except Exception as e:
        print(f"Error parseando playlist: {e}")
        return None


def fix_episode_playlist(episode):
    """
    Corrige la playlist de un episodio específico.
    """
    print(
        f"\n🔧 Corrigiendo episodio #{episode['program_number']} | {episode['title'][:50]}..."
    )

    playlist_json = episode.get("web_playlist")
    if not playlist_json:
        print(f"  ❌ No hay playlist para el episodio #{episode['program_number']}")
        return False

    # Intentar corregir el parsing
    fixed_playlist = fix_playlist_parsing(playlist_json)

    if fixed_playlist and len(fixed_playlist) >= 9:
        # Actualizar en Supabase
        db = get_supabase_connection()
        db.update_web_info(
            podcast_id=episode["id"],
            web_playlist=json.dumps(fixed_playlist, ensure_ascii=False),
            web_songs_count=len(fixed_playlist),
        )
        print(
            f"  ✅ Corregido: {len(fixed_playlist)} canciones (antes: {episode['web_songs_count']})"
        )

        # Mostrar algunas canciones como ejemplo
        print("  📝 Ejemplos de canciones extraídas:")
        for _i, song in enumerate(fixed_playlist[:3]):
            print(f"     {song['position']}. {song['artist']} - {song['title']}")
        if len(fixed_playlist) > 3:
            print(f"     ... y {len(fixed_playlist) - 3} más")

        return True
    else:
        print(
            f"  ⚠️  No se pudo corregir la playlist (canciones actuales: {episode['web_songs_count']})"
        )
        return False


def analyze_problematic_playlist(episode):
    """
    Analiza una playlist problemática para entender su estructura.
    """
    playlist_json = episode.get("web_playlist")
    if not playlist_json:
        return

    try:
        playlist = json.loads(playlist_json)
        print(f"\n🔍 Análisis de episodio #{episode['program_number']}:")
        print(f"   Canciones detectadas: {len(playlist)}")

        for i, song in enumerate(playlist):
            artist = song.get("artist", "")
            title = song.get("title", "")
            print(f"   {i+1}. Artista: '{artist[:100]}...'")
            print(f"      Título: '{title[:100]}...'")

            # Verificar si contiene múltiples canciones
            if "::" in artist:
                songs_count = artist.count("::") + 1
                print(f"      ⚠️  Contiene {songs_count} canciones concatenadas!")

                # Mostrar las primeras canciones separadas
                songs_raw = artist.split("::")[:3]
                for j, song_raw in enumerate(songs_raw):
                    print(f"         {j+1}. {song_raw.strip()[:80]}...")
                if songs_count > 3:
                    print(f"         ... y {songs_count - 3} más")

    except Exception as e:
        print(f"Error analizando playlist: {e}")


def main():
    """
    Función principal para corregir playlists con problemas de parsing.
    """
    print("🔧 Corregidor de parsing de playlists")
    print("=" * 50)

    # Obtener episodios problemáticos
    episodes = get_low_songs_episodes()
    print(f"📊 Encontrados {len(episodes)} episodios con 8 canciones o menos")

    if not episodes:
        print("✅ No hay episodios para corregir.")
        return

    # Analizar algunos episodios problemáticos primero
    print("\n🔍 Analizando estructura de playlists problemáticas...")
    for episode in episodes[:5]:  # Analizar los primeros 5
        analyze_problematic_playlist(episode)

    # Preguntar si continuar
    print("\n¿Quieres continuar corrigiendo todos los episodios? (s/n): ", end="")
    response = input().lower()

    if response != "s":
        print("Proceso cancelado.")
        return

    # Corregir episodios
    corrected = 0
    total_processed = 0

    for episode in episodes:
        if fix_episode_playlist(episode):
            corrected += 1
        total_processed += 1

    print("\n🎉 Proceso completado!")
    print(f"📊 Episodios procesados: {total_processed}")
    print(f"✅ Episodios corregidos: {corrected}")

    # Verificar resultados
    remaining = get_low_songs_episodes()
    if remaining:
        print(f"\n⚠️  Aún quedan {len(remaining)} episodios con 8 canciones o menos")
        for ep in remaining[:10]:
            print(
                f"  #{ep['program_number']} | {ep['web_songs_count']} canciones | {ep['title'][:40]}..."
            )
    else:
        print("\n✅ ¡Todos los episodios han sido corregidos!")


if __name__ == "__main__":
    main()
