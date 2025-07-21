#!/usr/bin/env python3
"""
Script para completar automáticamente los episodios pendientes extrayendo la playlist de los posts de WordPress.
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


def get_missing_episodes():
    db = get_supabase_connection()
    response = (
        db.client.table("podcasts")
        .select("id, program_number, title, date, wordpress_url")
        .is_("web_songs_count", "null")
        .execute()
    )
    return response.data


def extract_playlist_from_html(html):
    # Buscar bloques de canciones típicos (separados por :: o por salto de línea)
    # Buscamos el bloque más largo con varios " · " o " - " y ::
    candidates = re.findall(r"([\w\W]{50,600})", html)
    best = None
    max_canciones = 0
    for block in candidates:
        # Contar posibles canciones
        canciones = re.split(r"::|\n|<br ?/?>", block)
        canciones = [c.strip() for c in canciones if (" · " in c or " - " in c)]
        if len(canciones) > max_canciones:
            max_canciones = len(canciones)
            best = canciones
    if not best or max_canciones < 2:
        return None
    # Formatear playlist
    playlist = []
    for i, c in enumerate(best):
        c = re.sub(r"<.*?>", "", c)  # Quitar HTML
        c = c.replace("&amp;", "&")
        c = c.replace("&quot;", '"')
        c = c.replace("&#8217;", "’")
        c = c.replace("&#8211;", "–")
        c = c.strip()
        if " · " in c:
            artist, title = c.split(" · ", 1)
        elif " - " in c:
            artist, title = c.split(" - ", 1)
        else:
            artist, title = c, ""
        playlist.append(
            {"position": i + 1, "artist": artist.strip(), "title": title.strip()}
        )
    return playlist


def update_playlist_in_supabase(podcast_id, playlist):
    db = get_supabase_connection()
    db.update_web_info(
        podcast_id=podcast_id,
        web_playlist=json.dumps(playlist, ensure_ascii=False),
        web_songs_count=len(playlist),
    )


def main():
    print("🔍 Buscando y completando episodios pendientes desde WordPress...")
    missing = get_missing_episodes()
    print(f"Episodios a procesar: {len(missing)}")
    if not missing:
        print("No hay episodios pendientes.")
        return
    completados = 0
    for ep in missing:
        print(
            f"\n➡️  Procesando #{ep['program_number']} | {ep['date']} | {ep['title'][:40]}..."
        )
        url = ep.get("wordpress_url")
        if not url:
            print("  ⚠️  No hay wordpress_url, saltando...")
            continue
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"  ❌ Error HTTP {resp.status_code}")
                continue
            html = resp.text
            playlist = extract_playlist_from_html(html)
            if playlist and len(playlist) > 1:
                update_playlist_in_supabase(ep["id"], playlist)
                print(f"  ✅ Actualizado: {len(playlist)} canciones")
                completados += 1
            else:
                print("  ❌ No se pudo extraer la playlist")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        time.sleep(2)  # Pausa para no saturar el servidor
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
