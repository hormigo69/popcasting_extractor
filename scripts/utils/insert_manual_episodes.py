#!/usr/bin/env python3
"""
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


import json
import sys
from pathlib import Path
from services.supabase_database import SupabaseDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para insertar episodios manuales desde el archivo JSON.
"""


# Agregar el directorio raíz al path


def load_manual_episodes(json_file):
    """
    Carga los episodios manuales desde el archivo JSON.
    """
    try:
        with open(json_file, encoding="utf-8") as f:
            episodes = json.load(f)
        print(f"✅ {len(episodes)} episodios cargados desde {json_file}")
        return episodes
    except Exception as e:
        print(f"❌ Error cargando episodios: {e}")
        return []


def insert_manual_episodes_to_database(episodes):
    """
    Inserta todos los episodios manuales en la base de datos.
    """
    try:
        db = SupabaseDatabase()
        print("✅ Conexión a Supabase establecida")

        total_inserted = 0
        total_songs = 0
        total_links = 0

        for episode in episodes:
            print(f"\n📥 Insertando episodio #{episode['program_number']}...")

            # Insertar episodio
            podcast_id = db.add_podcast_if_not_exists(
                title=episode["title"],
                date=episode["date"],
                url=episode.get("wordpress_url", ""),
                program_number=str(episode["program_number"]),
                download_url=episode.get("download_url"),
                file_size=episode.get("file_size"),
            )

            # Actualizar información web
            if episode.get("wordpress_url") or episode.get("cover_image_url"):
                db.update_web_info(
                    podcast_id=podcast_id,
                    wordpress_url=episode.get("wordpress_url"),
                    cover_image_url=episode.get("cover_image_url"),
                    web_playlist=json.dumps(episode.get("playlist", [])),
                )

            # Insertar canciones
            playlist = episode.get("playlist", [])
            songs_inserted = 0
            for song in playlist:
                db.add_song(
                    podcast_id=podcast_id,
                    title=song.get("title", ""),
                    artist=song.get("artist", ""),
                    position=song.get("position", 0),
                )
                songs_inserted += 1

            # Insertar links extras
            extra_links = episode.get("extra_links", [])
            links_inserted = 0
            for link in extra_links:
                db.add_extra_link(
                    podcast_id=podcast_id,
                    text=link.get("text", ""),
                    url=link.get("url", ""),
                )
                links_inserted += 1

            total_inserted += 1
            total_songs += songs_inserted
            total_links += links_inserted

            print(f"   ✅ {songs_inserted} canciones, {links_inserted} links")

        print("\n🎉 ¡Inserción completada!")
        print(f"   - {total_inserted} episodios insertados")
        print(f"   - {total_songs} canciones insertadas")
        print(f"   - {total_links} links extras insertados")

    except Exception as e:
        print(f"❌ Error insertando episodios: {e}")


def main():
    """
    Función principal para insertar episodios manuales.
    """
    print("📥 INSERCIÓN DE EPISODIOS MANUALES")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Cargar episodios desde JSON
    json_file = Path(__file__).parent.parent.parent / "data" / "manual_episodes.json"
    episodes = load_manual_episodes(json_file)

    if not episodes:
        print("❌ No se pudieron cargar los episodios")
        return

    # Mostrar resumen
    print(f"\n📊 EPISODIOS A INSERTAR ({len(episodes)} total):")
    for episode in episodes:
        program_number = episode.get("program_number")
        title = episode.get("title")
        date = episode.get("date")
        songs_count = len(episode.get("playlist", []))
        print(f"   #{program_number:3d}: {title} ({date}) - {songs_count:2d} canciones")

    # Confirmar inserción
    response = (
        input(
            f"\n¿Deseas insertar estos {len(episodes)} episodios en la base de datos? (s/N): "
        )
        .strip()
        .lower()
    )

    if response == "s":
        insert_manual_episodes_to_database(episodes)
        print(
            "\n💡 Ahora puedes ejecutar verify_podcasts_integrity.py para verificar la integridad"
        )
    else:
        print("❌ Operación cancelada")


if __name__ == "__main__":
    main()
