#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a Supabase y contar episodios con MP3.
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.config import get_database_module


def test_supabase_connection():
    """Prueba la conexión a Supabase y cuenta episodios con MP3."""
    print("🔍 Probando conexión a Supabase...")
    
    try:
        db_module = get_database_module()
        db = db_module.SupabaseDatabase()
        
        # Obtener todos los podcasts
        podcasts = db.get_all_podcasts()
        
        if podcasts:
            total_episodes = len(podcasts)
            episodes_with_mp3 = sum(1 for p in podcasts if p.get('download_url'))
            
            print(f"✅ Conexión exitosa a Supabase")
            print(f"📊 Total de episodios: {total_episodes}")
            print(f"🎵 Episodios con MP3: {episodes_with_mp3}")
            print(f"📈 Porcentaje con MP3: {(episodes_with_mp3/total_episodes)*100:.1f}%")
            
            # Mostrar algunos ejemplos de URLs de descarga
            print("\n📋 Ejemplos de URLs de descarga:")
            for i, podcast in enumerate(podcasts[:5]):
                if podcast.get('download_url'):
                    print(f"  Episodio #{podcast['program_number']}: {podcast['download_url']}")
            
            return True
        else:
            print("❌ No se pudo obtener datos de Supabase")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        return False


if __name__ == "__main__":
    test_supabase_connection() 