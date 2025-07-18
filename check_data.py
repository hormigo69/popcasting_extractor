#!/usr/bin/env python3
"""
Script para verificar los datos extraídos
"""

from services.database import get_all_podcasts, get_songs_by_podcast_id

def check_data():
    """Verifica los datos extraídos"""
    print("🔍 Verificando datos extraídos...\n")
    
    # Obtener todos los podcasts
    podcasts = get_all_podcasts()
    print(f"📊 Total de podcasts en la base de datos: {len(podcasts)}")
    
    if not podcasts:
        print("❌ No hay podcasts en la base de datos")
        return
    
    # Mostrar información del último podcast
    latest_podcast = podcasts[-1]
    print("\n📻 Último podcast:")
    print(f"   ID: {latest_podcast[0]}")
    print(f"   Título: {latest_podcast[1]}")
    print(f"   Fecha: {latest_podcast[2]}")
    print(f"   Número: {latest_podcast[4]}")
    
    # Obtener canciones del último podcast
    songs = get_songs_by_podcast_id(latest_podcast[0])
    print(f"\n🎵 Canciones del último podcast: {len(songs)}")
    
    if songs:
        print("   Primeras 5 canciones:")
        for i, song in enumerate(songs[:5], 1):
            print(f"   {i}. {song[2]} · {song[3]}")
        
        if len(songs) > 5:
            print(f"   ... y {len(songs) - 5} más")
    
    # Mostrar estadísticas generales
    total_songs = 0
    for podcast in podcasts:
        songs = get_songs_by_podcast_id(podcast[0])
        total_songs += len(songs)
    
    print("\n📈 Estadísticas generales:")
    print(f"   Total de podcasts: {len(podcasts)}")
    print(f"   Total de canciones: {total_songs}")
    print(f"   Promedio de canciones por podcast: {total_songs / len(podcasts):.1f}")

if __name__ == "__main__":
    check_data() 