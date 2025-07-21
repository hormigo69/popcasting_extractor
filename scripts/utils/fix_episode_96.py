#!/usr/bin/env python3
"""
Script para corregir el episodio #96 con su playlist completa.
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

def fix_episode_96():
    """
    Corrige el episodio #96 con su playlist completa.
    """
    print("🔧 Corrigiendo episodio #96 con playlist completa...")
    
    # Playlist completa del episodio #96 (similar al #92)
    playlist_96 = [
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
        # Obtener el episodio #96 de la base de datos
        db = get_supabase_connection()
        response = db.client.table("podcasts").select(
            "id, program_number, title, date, web_playlist, web_songs_count"
        ).eq("program_number", 96).execute()
        
        if not response.data:
            print("❌ Episodio #96 no encontrado en la base de datos")
            return False
        
        episode = response.data[0]
        print(f"📋 Episodio encontrado: #{episode['program_number']} | {episode['title']}")
        print(f"   Canciones actuales: {episode['web_songs_count']}")
        
        # Mostrar la playlist actual para comparar
        current_playlist = episode.get('web_playlist')
        if current_playlist:
            try:
                current = json.loads(current_playlist)
                print(f"   Playlist actual (primeras 3 canciones):")
                for i, song in enumerate(current[:3]):
                    print(f"     {i+1}. {song.get('artist', 'N/A')} - {song.get('title', 'N/A')}")
            except:
                print(f"   Playlist actual: {current_playlist[:100]}...")
        
        # Actualizar la playlist
        db.update_web_info(
            podcast_id=episode['id'],
            web_playlist=json.dumps(playlist_96, ensure_ascii=False),
            web_songs_count=len(playlist_96)
        )
        
        print(f"✅ Episodio #96 corregido: {len(playlist_96)} canciones")
        print(f"📝 Playlist actualizada:")
        for song in playlist_96:
            print(f"   {song['position']}. {song['artist']} - {song['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo episodio #96: {e}")
        return False

def main():
    """
    Función principal.
    """
    print("🎵 Corregidor específico del episodio #96")
    print("=" * 40)
    
    success = fix_episode_96()
    
    if success:
        print(f"\n🎉 Episodio #96 corregido exitosamente!")
    else:
        print(f"\n❌ Error corrigiendo el episodio #96")

if __name__ == "__main__":
    main() 