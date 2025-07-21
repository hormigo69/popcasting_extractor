#!/usr/bin/env python3
"""
Script específico para corregir el episodio #92 con su playlist completa.
"""

import json
from pathlib import Path
from dotenv import load_dotenv
import sys

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

from supabase_database import get_supabase_connection

def fix_episode_92():
    """
    Corrige el episodio #92 con su playlist completa de 12 canciones.
    """
    print("🔧 Corrigiendo episodio #92 con playlist completa...")
    
    # Playlist completa del episodio #92
    playlist_92 = [
        {"position": 1, "artist": "dolly parton", "title": "jolene"},
        {"position": 2, "artist": "eels", "title": "my timing is off"},
        {"position": 3, "artist": "bat for lashes", "title": "a forest"},
        {"position": 4, "artist": "siouxie and the banshees", "title": "hong kong garden"},
        {"position": 5, "artist": "peaches", "title": "lose you"},
        {"position": 6, "artist": "johnny legend", "title": "green light"},
        {"position": 7, "artist": "asobi seksu", "title": "transparence"},
        {"position": 8, "artist": "little boots", "title": "new in town (no one is safe · al kapranos remix)"},
        {"position": 9, "artist": "mickey and silvia", "title": "love is strange (take 4)"},
        {"position": 10, "artist": "the coasters", "title": "i'm a hog for you"},
        {"position": 11, "artist": "johnny burnette trio", "title": "honey hush"}
    ]
    
    try:
        # Obtener el episodio #92 de la base de datos
        db = get_supabase_connection()
        response = db.client.table("podcasts").select(
            "id, program_number, title, date, web_playlist, web_songs_count"
        ).eq("program_number", 92).execute()
        
        if not response.data:
            print("❌ Episodio #92 no encontrado en la base de datos")
            return False
        
        episode = response.data[0]
        print(f"📋 Episodio encontrado: #{episode['program_number']} | {episode['title']}")
        print(f"   Canciones actuales: {episode['web_songs_count']}")
        
        # Actualizar la playlist
        db.update_web_info(
            podcast_id=episode['id'],
            web_playlist=json.dumps(playlist_92, ensure_ascii=False),
            web_songs_count=len(playlist_92)
        )
        
        print(f"✅ Episodio #92 corregido: {len(playlist_92)} canciones")
        print(f"📝 Playlist actualizada:")
        for song in playlist_92:
            print(f"   {song['position']}. {song['artist']} - {song['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo episodio #92: {e}")
        return False

def main():
    """
    Función principal.
    """
    print("🎵 Corregidor específico del episodio #92")
    print("=" * 40)
    
    success = fix_episode_92()
    
    if success:
        print(f"\n🎉 Episodio #92 corregido exitosamente!")
    else:
        print(f"\n❌ Error corrigiendo el episodio #92")

if __name__ == "__main__":
    main() 