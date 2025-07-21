#!/usr/bin/env python3
"""
Script para revisar y corregir episodios con pocas canciones detectadas.
Extrae las playlists reales de los HTML y actualiza la base de datos.
"""

import json
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

from supabase_database import get_supabase_connection


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


def extract_playlist_from_html(html_content):
    """
    Extrae la playlist del HTML con mejor parsing.
    """
    # Limpiar HTML tags
    html_content = re.sub(r"<[^>]+>", "", html_content)
    html_content = (
        html_content.replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#8217;", "'")
        .replace("&#8211;", "–")
    )

    # Buscar patrones de playlist

    candidates = []

    # Buscar bloques que contengan múltiples canciones separadas por ::
    blocks = re.findall(r"([^:]{20,800})", html_content)

    for block in blocks:
        # Contar separadores ::
        separators = block.count("::")
        if separators >= 2:  # Al menos 3 canciones
            candidates.append((block, separators + 1))

    if not candidates:
        return None

    # Tomar el bloque con más canciones
    best_block, song_count = max(candidates, key=lambda x: x[1])

    # Separar por ::
    songs_raw = [s.strip() for s in best_block.split("::") if s.strip()]

    playlist = []
    for _i, song_raw in enumerate(songs_raw):
        # Limpiar la canción
        song_raw = re.sub(r"http[^\s]*", "", song_raw)  # Remover URLs
        song_raw = re.sub(
            r"[^\w\s\-\'\.\,\&\*\(\)]", "", song_raw
        )  # Limpiar caracteres especiales
        song_raw = song_raw.strip()

        if len(song_raw) < 5:  # Muy corto, probablemente no es una canción
            continue

        # Intentar separar artista y título
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

        # Filtrar entradas que no parecen canciones
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
            ]
        ):
            continue

        if len(artist) > 3 and len(artist) < 100:  # Longitud razonable
            playlist.append(
                {"position": len(playlist) + 1, "artist": artist, "title": title}
            )

    return playlist if len(playlist) >= 3 else None


def fix_episode_playlist(episode):
    """
    Corrige la playlist de un episodio específico.
    """
    print(
        f"\n🔧 Corrigiendo episodio #{episode['program_number']} | {episode['title'][:50]}..."
    )

    url = episode.get("wordpress_url")
    if not url:
        print(
            f"  ❌ No hay URL de WordPress para el episodio #{episode['program_number']}"
        )
        return False

    try:
        # Obtener HTML
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            print(f"  ❌ Error HTTP {response.status_code} para {url}")
            return False

        html_content = response.text

        # Extraer playlist mejorada
        playlist = extract_playlist_from_html(html_content)

        if (
            playlist and len(playlist) >= 9
        ):  # Al menos 9 canciones para considerar válida
            # Actualizar en Supabase
            db = get_supabase_connection()
            db.update_web_info(
                podcast_id=episode["id"],
                web_playlist=json.dumps(playlist, ensure_ascii=False),
                web_songs_count=len(playlist),
            )
            print(
                f"  ✅ Corregido: {len(playlist)} canciones (antes: {episode['web_songs_count']})"
            )
            return True
        else:
            print(
                f"  ⚠️  No se pudo extraer playlist válida (extraídas: {len(playlist) if playlist else 0})"
            )
            return False

    except Exception as e:
        print(f"  ❌ Error procesando episodio #{episode['program_number']}: {e}")
        return False


def main():
    """
    Función principal para corregir episodios con pocas canciones.
    """
    print("🔧 Corregidor de episodios con pocas canciones")
    print("=" * 50)

    # Obtener episodios problemáticos
    episodes = get_low_songs_episodes()
    print(f"📊 Encontrados {len(episodes)} episodios con 8 canciones o menos")

    if not episodes:
        print("✅ No hay episodios para corregir.")
        return

    # Agrupar por número de canciones actuales
    by_count = {}
    for ep in episodes:
        count = ep["web_songs_count"]
        if count not in by_count:
            by_count[count] = []
        by_count[count].append(ep)

    print("\n📋 Distribución actual:")
    for count in sorted(by_count.keys()):
        print(f"  {count} canciones: {len(by_count[count])} episodios")

    # Corregir episodios, empezando por los que tienen menos canciones
    corrected = 0
    total_processed = 0

    for count in sorted(by_count.keys()):  # Empezar por los que tienen menos canciones
        episodes_group = by_count[count]
        print(
            f"\n🎵 Procesando episodios con {count} canciones ({len(episodes_group)} episodios)"
        )

        for episode in episodes_group:
            if fix_episode_playlist(episode):
                corrected += 1
            total_processed += 1
            time.sleep(1)  # Pausa para no sobrecargar el servidor

    print("\n🎉 Proceso completado!")
    print(f"📊 Episodios procesados: {total_processed}")
    print(f"✅ Episodios corregidos: {corrected}")

    # Verificar resultados
    remaining = get_low_songs_episodes()
    if remaining:
        print(f"\n⚠️  Aún quedan {len(remaining)} episodios con 8 canciones o menos")
        for ep in remaining[:10]:  # Mostrar los primeros 10
            print(
                f"  #{ep['program_number']} | {ep['web_songs_count']} canciones | {ep['title'][:40]}..."
            )
    else:
        print("\n✅ ¡Todos los episodios han sido corregidos!")


if __name__ == "__main__":
    main()
