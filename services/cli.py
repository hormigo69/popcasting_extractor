#!/usr/bin/env python3
"""
CLI para el extractor y buscador de Popcasting.
"""
import sys
import os
import argparse

# Añadir el directorio raíz del proyecto al sys.path
# para que los imports de módulos funcionen correctamente al ejecutar como script.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.popcasting_extractor import PopcastingExtractor
import services.database as db

def handle_run():
    """Ejecuta el proceso de extracción y guardado."""
    print("🎵 Iniciando el extractor de Popcasting 🎵")
    print("=" * 40)
    try:
        extractor = PopcastingExtractor()
        extractor.run()
        print("\n✅ Proceso completado exitosamente!")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado durante la ejecución: {e}")
        sys.exit(1)

def handle_search_songs(query: str):
    """Busca canciones y muestra los resultados."""
    print(f"🔎 Buscando canciones que contengan '{query}'...")
    results = db.search_songs(query)
    
    if not results:
        print("No se encontraron canciones con ese criterio.")
        return
        
    print(f"✨ Encontrados {len(results)} resultados:")
    for res in results:
        print("-" * 20)
        print(f"  🎵 ({res['position']}) {res['song_title']} - {res['artist']}")
        print(f"  📻 Podcast: Popcasting {res['program_number']} ({res['podcast_date']})")

def handle_search_artist(query: str):
    """Busca por artista y muestra sus canciones."""
    print(f"🔎 Buscando canciones del artista '{query}'...")
    results = db.search_by_artist(query)
    
    if not results:
        print(f"No se encontraron canciones para el artista '{query}'.")
        return
    
    # Imprimir el nombre del artista una sola vez
    artist_name = results[0]['artist']
    print(f"✨ Encontradas {len(results)} canciones de {artist_name}:")
    
    for res in results:
        print(f"  🎵 ({res['position']}) {res['song_title']} (en Popcasting {res['program_number']} - {res['podcast_date']})")

def main():
    """
    Función principal del CLI.
    """
    parser = argparse.ArgumentParser(
        description='Extractor y buscador de datos de Popcasting.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles', required=True)
    
    # --- Comando 'run' ---
    run_parser = subparsers.add_parser('run', help='Ejecuta el extractor para actualizar la base de datos.')
    run_parser.set_defaults(func=handle_run)

    # --- Comando 'search' ---
    search_parser = subparsers.add_parser('search', help='Busca en la base de datos.')
    search_subparsers = search_parser.add_subparsers(dest='search_target', help='Qué buscar', required=True)
    
    # Sub-comando 'search songs'
    search_songs_parser = search_subparsers.add_parser('songs', help='Busca canciones por título o artista.')
    search_songs_parser.add_argument('query', type=str, help='Texto a buscar en títulos de canción o artistas.')
    search_songs_parser.set_defaults(func=lambda args: handle_search_songs(args.query))

    # Sub-comando 'search artists'
    search_artists_parser = search_subparsers.add_parser('artists', help='Busca todas las canciones de un artista.')
    search_artists_parser.add_argument('query', type=str, help='Nombre del artista a buscar.')
    search_artists_parser.set_defaults(func=lambda args: handle_search_artist(args.query))

    args = parser.parse_args()
    
    # Ejecutar la función asociada al comando
    if hasattr(args, 'func'):
        # Algunos comandos tienen funciones que reciben 'args'
        if args.command == 'search':
            args.func(args)
        else:
            args.func()

if __name__ == "__main__":
    main() 