#!/usr/bin/env python3
"""
Script para actualizar manualmente la playlist y el número de canciones de un episodio en Supabase.
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

from supabase_database import get_supabase_connection


def update_playlist(program_number, playlist):
    db = get_supabase_connection()
    # Buscar el episodio por program_number
    response = (
        db.client.table("podcasts")
        .select("id")
        .eq("program_number", program_number)
        .execute()
    )
    if not response.data:
        print(f"❌ Episodio #{program_number} no encontrado en la base de datos")
        return False
    podcast_id = response.data[0]["id"]
    db.update_web_info(
        podcast_id=podcast_id,
        web_playlist=json.dumps(playlist, ensure_ascii=False),
        web_songs_count=len(playlist),
    )
    print(f"✅ Episodio #{program_number} actualizado con {len(playlist)} canciones.")
    return True


def main():
    # Playlist del episodio 109
    playlist_109 = [
        {"position": 1, "artist": "bob dylan", "title": "must be santa"},
        {
            "position": 2,
            "artist": "the paris sisters",
            "title": "christmas in my hometown",
        },
        {
            "position": 3,
            "artist": "the leisure society",
            "title": "the last of the melting snow",
        },
        {"position": 4, "artist": "jacques dutronc", "title": "la fille du père noël"},
        {
            "position": 5,
            "artist": "julian casablancas",
            "title": "i wish it was christmas today",
        },
        {
            "position": 6,
            "artist": "the free design",
            "title": "close your mouth (it’s christmas)",
        },
        {"position": 7, "artist": "the hit parade", "title": "i love christmas"},
        {"position": 8, "artist": "electric jungle", "title": "funky funky christmas"},
        {"position": 9, "artist": "jimmy butler", "title": "trim your tree"},
        {"position": 10, "artist": "the trashmen", "title": "dancin’ with santa"},
        {"position": 11, "artist": "valerie masters", "title": "christmas calling"},
        {
            "position": 12,
            "artist": "vashti & twice as much",
            "title": "the coldest night of the year",
        },
        {
            "position": 13,
            "artist": "rufus wainwright",
            "title": "spotlight on christmas",
        },
        {"position": 14, "artist": "the waitresses", "title": "christmas wrappin’"},
    ]
    update_playlist(109, playlist_109)


if __name__ == "__main__":
    main()
