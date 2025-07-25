import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from dotenv import load_dotenv
from supabase_database import get_supabase_connection

from services.web_extractor import WebExtractor

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))


#!/usr/bin/env python3
"""
Script para buscar y actualizar los episodios faltantes en Supabase usando el extractor web.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def get_missing_episodes():
    db = get_supabase_connection()
    response = (
        db.client.table("podcasts")
        .select(
            "id, program_number, title, date, wordpress_url, web_playlist, web_songs_count"
        )
        .is_("web_songs_count", "null")
        .execute()
    )
    return response.data


def update_episode_web_info(podcast_id, playlist_json, web_songs_count):
    db = get_supabase_connection()
    db.update_web_info(
        podcast_id=podcast_id,
        web_playlist=playlist_json,
        web_songs_count=web_songs_count,
    )


def main():
    print("🔍 Buscando y actualizando episodios faltantes desde la web...")
    missing = get_missing_episodes()
    print(f"Episodios a procesar: {len(missing)}")
    if not missing:
        print("No hay episodios pendientes.")
        return

    extractor = WebExtractor()
    completados = 0
    for ep in missing:
        print(
            f"\n➡️  Procesando #{ep['program_number']} | {ep['date']} | {ep['title'][:40]}..."
        )
        wordpress_url = ep.get("wordpress_url")
        if not wordpress_url:
            print("  ⚠️  No hay wordpress_url, saltando...")
            continue
        web_info = extractor._extract_episode_page_info(wordpress_url)
        playlist_json = web_info.get("playlist_json")
        web_songs_count = None
        if playlist_json:
            try:
                playlist = json.loads(playlist_json)
                web_songs_count = len(playlist) if isinstance(playlist, list) else 0
            except json.JSONDecodeError:
                web_songs_count = 0
        if playlist_json and web_songs_count:
            update_episode_web_info(ep["id"], playlist_json, web_songs_count)
            print(f"  ✅ Actualizado: {web_songs_count} canciones")
            completados += 1
        else:
            print("  ❌ No se pudo extraer la playlist")
    print(
        f"\n🎉 Proceso completado. Episodios actualizados: {completados}/{len(missing)}"
    )

    # Comprobar si quedan episodios sin web_songs_count
    left = get_missing_episodes()
    if not left:
        print("\n✅ ¡Todos los episodios tienen web_songs_count!")
    else:
        print(f"\n❌ Aún quedan {len(left)} episodios sin web_songs_count:")
        for ep in left:
            print(f"  #{ep['program_number']} | {ep['date']} | {ep['title'][:40]}...")


if __name__ == "__main__":
    main()
