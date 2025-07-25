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
Script para corregir episodios con 2 canciones que tienen canciones concatenadas.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def extract_songs_from_concatenated_text(text):
    """
    Extrae canciones individuales de texto concatenado.
    """
    # Limpiar el texto
    text = text.strip()

    # Patrones de separación
    separators = ["::", "•", " - "]

    for separator in separators:
        if separator in text:
            parts = text.split(separator)
            songs = []

            for i, part in enumerate(parts, 1):
                part = part.strip()
                if part and not part.startswith("http"):
                    # Intentar extraer artista y título
                    if " - " in part:
                        artist_title = part.split(" - ", 1)
                        if len(artist_title) == 2:
                            artist, title = artist_title
                            songs.append(
                                {
                                    "position": i,
                                    "artist": artist.strip(),
                                    "title": title.strip(),
                                }
                            )
                        else:
                            songs.append(
                                {"position": i, "artist": "N/A", "title": part}
                            )
                    else:
                        songs.append({"position": i, "artist": "N/A", "title": part})

            return songs

    return None


def fix_two_song_episode(episode):
    """
    Corrige un episodio con 2 canciones.
    """
    print(f"🔧 Corrigiendo episodio #{episode['program_number']}...")

    playlist = episode.get("web_playlist")
    if not playlist:
        print("   ❌ Sin playlist")
        return False

    try:
        songs = json.loads(playlist)
        if len(songs) != 2:
            print("   ❌ No tiene exactamente 2 canciones")
            return False

        # Verificar si alguna canción está concatenada
        fixed_songs = []
        total_extracted = 0

        for song in songs:
            title = song.get("title", "")
            song.get("artist", "")

            # Si es una URL, saltarla
            if title.startswith("http"):
                continue

            # Si tiene separadores, extraer canciones
            if "::" in title or "•" in title or " - " in title:
                extracted = extract_songs_from_concatenated_text(title)
                if extracted:
                    fixed_songs.extend(extracted)
                    total_extracted += len(extracted)
                    print(
                        f"   ✅ Extraídas {len(extracted)} canciones de: {title[:50]}..."
                    )
                else:
                    fixed_songs.append(song)
            else:
                fixed_songs.append(song)

        if total_extracted > 0:
            # Actualizar la base de datos
            db = get_supabase_connection()
            db.update_web_info(
                podcast_id=episode["id"],
                web_playlist=json.dumps(fixed_songs, ensure_ascii=False),
                web_songs_count=len(fixed_songs),
            )

            print(
                f"   ✅ Corregido: {len(songs)} → {len(fixed_songs)} canciones (+{total_extracted})"
            )
            return True
        else:
            print("   ⚠️  No se encontraron canciones concatenadas")
            return False

    except json.JSONDecodeError:
        print("   ❌ JSON inválido")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


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


def main():
    """
    Función principal.
    """
    print("🎵 Corregidor de episodios con 2 canciones")
    print("=" * 45)

    episodes = get_two_song_episodes()

    if not episodes:
        print("✅ No hay episodios con solo 2 canciones.")
        return

    print(f"🔍 Encontrados {len(episodes)} episodios con 2 canciones")
    print()

    corrected_count = 0
    total_songs_recovered = 0

    for episode in episodes:
        print(f"📋 Episodio #{episode['program_number']} | {episode['title']}")

        # Verificar si necesita corrección
        playlist = episode.get("web_playlist")
        if playlist:
            try:
                songs = json.loads(playlist)
                needs_fix = any(
                    "::" in song.get("title", "")
                    or "•" in song.get("title", "")
                    or " - " in song.get("title", "")
                    for song in songs
                )

                if needs_fix:
                    if fix_two_song_episode(episode):
                        corrected_count += 1
                        # Calcular canciones recuperadas
                        len(songs)
                        # Esto se calculará mejor después de la corrección
                        total_songs_recovered += 5  # Estimación
                else:
                    print("   ⚠️  No necesita corrección")

            except json.JSONDecodeError:
                print("   ❌ JSON inválido")

        print("-" * 40)

    print("\n🎉 Resumen:")
    print(f"   Episodios corregidos: {corrected_count}")
    print(f"   Canciones recuperadas estimadas: {total_songs_recovered}")


if __name__ == "__main__":
    main()
