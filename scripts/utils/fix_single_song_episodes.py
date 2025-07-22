import json
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from supabase_database import get_supabase_connection

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))


#!/usr/bin/env python3
"""
Script específico para corregir episodios con 1-2 canciones que tienen toda la playlist concatenada.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def get_single_song_episodes():
    """
    Obtiene episodios con 1-2 canciones para corregir.
    """
    db = get_supabase_connection()
    response = (
        db.client.table("podcasts")
        .select(
            "id, program_number, title, date, web_playlist, web_songs_count, wordpress_url"
        )
        .not_.is_("web_songs_count", "null")
        .lte("web_songs_count", 2)
        .order("web_songs_count", desc=True)
        .execute()
    )

    return response.data


def extract_songs_from_concatenated_text(text):
    """
    Extrae canciones de un texto que contiene múltiples canciones concatenadas.
    """
    # Limpiar el texto
    text = re.sub(r"http[^\s]*", "", text)  # Remover URLs
    text = re.sub(r"<[^>]+>", "", text)  # Remover HTML tags
    text = (
        text.replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#8217;", "'")
        .replace("&#8211;", "–")
    )

    # Buscar patrones de canciones separadas por ::
    if "::" in text:
        songs_raw = [s.strip() for s in text.split("::") if s.strip()]
    else:
        # Si no hay ::, buscar por otros separadores
        songs_raw = [s.strip() for s in re.split(r"[•\-–]", text) if s.strip()]

    playlist = []
    for _i, song_raw in enumerate(songs_raw):
        song_raw = song_raw.strip()
        if len(song_raw) < 5:
            continue

        # Limpiar caracteres especiales
        song_raw = re.sub(r"[^\w\s\-\'\.\,\&\*\(\)]", "", song_raw)

        # Separar artista y título
        if " • " in song_raw:
            parts = song_raw.split(" • ", 1)
            artist = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else ""
        elif " - " in song_raw:
            parts = song_raw.split(" - ", 1)
            artist = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else ""
        else:
            artist = song_raw
            title = ""

        # Filtrar entradas no válidas
        if any(
            keyword in artist.lower()
            for keyword in [
                "http",
                "comparte",
                "haz clic",
                "facebook",
                "twitter",
                "ivoox",
                "blip.tv",
                "meta name",
            ]
        ):
            continue

        if len(artist) > 3 and len(artist) < 100:
            playlist.append(
                {"position": len(playlist) + 1, "artist": artist, "title": title}
            )

    return playlist


def fix_single_song_episode(episode):
    """
    Corrige un episodio que tiene solo 1-2 canciones.
    """
    print(
        f"\n🔧 Corrigiendo episodio #{episode['program_number']} | {episode['title'][:50]}..."
    )

    playlist_json = episode.get("web_playlist")
    if not playlist_json:
        print(f"  ❌ No hay playlist para el episodio #{episode['program_number']}")
        return False

    try:
        playlist = json.loads(playlist_json)

        # Buscar el elemento que contiene múltiples canciones
        for i, song in enumerate(playlist):
            artist = song.get("artist", "")
            title = song.get("title", "")

            # Si el artista o título contiene múltiples canciones
            if "::" in artist or "::" in title:
                print(f"  🔍 Encontradas canciones concatenadas en elemento {i+1}")

                # Extraer canciones del artista
                if "::" in artist:
                    extracted_songs = extract_songs_from_concatenated_text(artist)
                else:
                    extracted_songs = extract_songs_from_concatenated_text(title)

                if extracted_songs and len(extracted_songs) >= 5:
                    # Actualizar en Supabase
                    db = get_supabase_connection()
                    db.update_web_info(
                        podcast_id=episode["id"],
                        web_playlist=json.dumps(extracted_songs, ensure_ascii=False),
                        web_songs_count=len(extracted_songs),
                    )
                    print(
                        f"  ✅ Corregido: {len(extracted_songs)} canciones (antes: {episode['web_songs_count']})"
                    )

                    # Mostrar algunas canciones como ejemplo
                    print("  📝 Ejemplos de canciones extraídas:")
                    for _j, song in enumerate(extracted_songs[:3]):
                        print(
                            f"     {song['position']}. {song['artist']} - {song['title']}"
                        )
                    if len(extracted_songs) > 3:
                        print(f"     ... y {len(extracted_songs) - 3} más")

                    return True

        print("  ⚠️  No se encontraron canciones concatenadas")
        return False

    except Exception as e:
        print(f"  ❌ Error procesando episodio #{episode['program_number']}: {e}")
        return False


def analyze_single_song_episode(episode):
    """
    Analiza un episodio con 1-2 canciones para entender su estructura.
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
            print(f"   {i+1}. Artista: '{artist[:150]}...'")
            print(f"      Título: '{title[:150]}...'")

            # Verificar si contiene múltiples canciones
            if "::" in artist or "::" in title:
                songs_count = max(artist.count("::"), title.count("::")) + 1
                print(f"      ⚠️  Contiene {songs_count} canciones concatenadas!")

                # Mostrar las primeras canciones separadas
                if "::" in artist:
                    songs_raw = artist.split("::")[:3]
                else:
                    songs_raw = title.split("::")[:3]

                for j, song_raw in enumerate(songs_raw):
                    print(f"         {j+1}. {song_raw.strip()[:80]}...")
                if songs_count > 3:
                    print(f"         ... y {songs_count - 3} más")

    except Exception as e:
        print(f"Error analizando playlist: {e}")


def main():
    """
    Función principal para corregir episodios con 1-2 canciones.
    """
    print("🔧 Corregidor de episodios con 1-2 canciones")
    print("=" * 50)

    # Obtener episodios con 1-2 canciones
    episodes = get_single_song_episodes()
    print(f"📊 Encontrados {len(episodes)} episodios con 1-2 canciones")

    if not episodes:
        print("✅ No hay episodios para corregir.")
        return

    # Analizar algunos episodios problemáticos primero
    print("\n🔍 Analizando estructura de episodios con 1-2 canciones...")
    for episode in episodes[:3]:  # Analizar los primeros 3
        analyze_single_song_episode(episode)

    # Corregir episodios
    corrected = 0
    total_processed = 0

    for episode in episodes:
        if fix_single_song_episode(episode):
            corrected += 1
        total_processed += 1

    print("\n🎉 Proceso completado!")
    print(f"📊 Episodios procesados: {total_processed}")
    print(f"✅ Episodios corregidos: {corrected}")

    # Verificar resultados
    remaining = get_single_song_episodes()
    if remaining:
        print(f"\n⚠️  Aún quedan {len(remaining)} episodios con 1-2 canciones")
        for ep in remaining[:10]:
            print(
                f"  #{ep['program_number']} | {ep['web_songs_count']} canciones | {ep['title'][:40]}..."
            )
    else:
        print("\n✅ ¡Todos los episodios con 1-2 canciones han sido corregidos!")


if __name__ == "__main__":
    main()
