#!/usr/bin/env python3
"""
CLI avanzado para el extractor de Popcasting
"""

import argparse
import json
import sys
import os
from datetime import datetime
from popcasting_extractor import PopcastingExtractor


def format_stats(episodes):
    """Formatea estadísticas de los episodios"""
    total_episodes = len(episodes)
    total_songs = sum(len(ep.get('playlist', [])) for ep in episodes)
    
    # Estadísticas por año
    years = {}
    for ep in episodes:
        if ep.get('published'):
            try:
                year = datetime.strptime(ep['published'], '%a, %d %b %Y %H:%M:%S %z').year
                years[year] = years.get(year, 0) + 1
            except (ValueError, TypeError):
                pass
    
    # Episodios con más canciones
    top_episodes = sorted(
        episodes, 
        key=lambda x: len(x.get('playlist', [])), 
        reverse=True
    )[:5]
    
    stats = {
        'total_episodes': total_episodes,
        'total_songs': total_songs,
        'episodes_by_year': years,
        'top_episodes_by_songs': [
            {
                'title': ep['title'],
                'program_number': ep.get('program_number'),
                'song_count': len(ep.get('playlist', []))
            }
            for ep in top_episodes
        ]
    }
    
    return stats


def filter_episodes(episodes, filters):
    """Filtra episodios según criterios"""
    filtered = episodes
    
    if filters.get('program_number'):
        filtered = [ep for ep in filtered if ep.get('program_number') == filters['program_number']]
    
    if filters.get('year'):
        filtered = [
            ep for ep in filtered 
            if ep.get('published') and filters['year'] in ep['published']
        ]
    
    if filters.get('min_songs'):
        filtered = [
            ep for ep in filtered 
            if len(ep.get('playlist', [])) >= filters['min_songs']
        ]
    
    return filtered


def export_playlist_only(episodes, filename):
    """Exporta solo las playlists en formato simplificado"""
    playlists = []
    
    for ep in episodes:
        if ep.get('playlist'):
            episode_playlist = {
                'program_number': ep.get('program_number'),
                'title': ep.get('title'),
                'published': ep.get('published'),
                'songs': ep['playlist']
            }
            playlists.append(episode_playlist)
    
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(playlists, f, ensure_ascii=False, indent=2)
    
    print(f"Playlists exportadas a: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Extractor avanzado de datos de Popcasting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos de uso:
  python cli.py                                    # Extracción completa
  python cli.py --stats                           # Solo mostrar estadísticas
  python cli.py --program-number 483             # Solo programa específico
  python cli.py --year 2024                      # Solo episodios de 2024
  python cli.py --min-songs 10                   # Solo episodios con 10+ canciones
  python cli.py --playlist-only                  # Solo exportar playlists
  python cli.py --output mi_archivo.json         # Archivo de salida personalizado
        '''
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Nombre del archivo de salida (por defecto: timestamp)'
    )
    
    parser.add_argument(
        '--stats', '-s',
        action='store_true',
        help='Mostrar estadísticas detalladas'
    )
    
    parser.add_argument(
        '--program-number', '-p',
        help='Filtrar por número de programa específico'
    )
    
    parser.add_argument(
        '--year', '-y',
        help='Filtrar por año (ej: 2024)'
    )
    
    parser.add_argument(
        '--min-songs', '-m',
        type=int,
        help='Filtrar episodios con mínimo N canciones'
    )
    
    parser.add_argument(
        '--playlist-only',
        action='store_true',
        help='Exportar solo playlists en formato simplificado'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar información detallada durante el proceso'
    )
    
    args = parser.parse_args()
    
    print("🎵 Extractor avanzado de Popcasting 🎵")
    print("=" * 50)
    
    # Crear extractor
    extractor = PopcastingExtractor()
    
    # Extraer episodios
    if args.verbose:
        print("Descargando y procesando RSS...")
    
    episodes = extractor.extract_episodes()
    
    if not episodes:
        print("❌ No se pudieron extraer episodios")
        sys.exit(1)
    
    # Aplicar filtros
    filters = {
        'program_number': args.program_number,
        'year': args.year,
        'min_songs': args.min_songs
    }
    
    filtered_episodes = filter_episodes(episodes, filters)
    
    if args.verbose:
        print(f"Episodios encontrados: {len(episodes)}")
        print(f"Episodios después de filtros: {len(filtered_episodes)}")
    
    # Mostrar estadísticas
    if args.stats:
        stats = format_stats(filtered_episodes)
        print("\n📊 Estadísticas:")
        print(f"Total de episodios: {stats['total_episodes']}")
        print(f"Total de canciones: {stats['total_songs']}")
        
        if stats['episodes_by_year']:
            print("\nEpisodios por año:")
            for year, count in sorted(stats['episodes_by_year'].items()):
                print(f"  {year}: {count} episodios")
        
        if stats['top_episodes_by_songs']:
            print("\nTop 5 episodios con más canciones:")
            for i, ep in enumerate(stats['top_episodes_by_songs'], 1):
                print(f"  {i}. {ep['title']} - {ep['song_count']} canciones")
    
    # Exportar datos
    if filtered_episodes:
        # Determinar directorio de salida
        if os.path.basename(os.getcwd()) == 'services':
            output_dir = "../outputs"
        else:
            output_dir = "outputs"
        
        if args.playlist_only:
            filename = args.output or f"{output_dir}/playlists_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            export_playlist_only(filtered_episodes, filename)
        else:
            filename = args.output or f"{output_dir}/popcasting_episodes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            extractor.save_to_json(filtered_episodes, filename)
        
        print("\n✅ Proceso completado exitosamente!")
        print(f"Episodios procesados: {len(filtered_episodes)}")
        total_songs = sum(len(ep.get('playlist', [])) for ep in filtered_episodes)
        print(f"Canciones extraídas: {total_songs}")
    else:
        print("❌ No se encontraron episodios que cumplan los criterios")


if __name__ == "__main__":
    main() 