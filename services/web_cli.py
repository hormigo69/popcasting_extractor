#!/usr/bin/env python3
"""
CLI para el servicio de extracción web de Popcasting.
"""

import argparse
import json

from . import database as db
from .web_extractor import WebExtractor


def main():
    parser = argparse.ArgumentParser(description="Extractor web de Popcasting")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando para extraer información de la web
    extract_parser = subparsers.add_parser(
        "extract", help="Extraer información de la web"
    )
    extract_parser.add_argument(
        "--max-episodes", type=int, help="Número máximo de episodios a procesar"
    )
    extract_parser.add_argument(
        "--episode-id", type=int, help="ID específico del episodio a procesar"
    )

    # Comando para comparar RSS vs Web
    compare_parser = subparsers.add_parser("compare", help="Comparar RSS vs Web")
    compare_parser.add_argument(
        "episode_id", type=int, help="ID del episodio a comparar"
    )
    compare_parser.add_argument(
        "--json", action="store_true", help="Salida en formato JSON"
    )

    # Comando para listar episodios sin información web
    list_parser = subparsers.add_parser(
        "list", help="Listar episodios sin información web"
    )
    list_parser.add_argument(
        "--limit", type=int, default=20, help="Número máximo de episodios a mostrar"
    )

    # Comando para mostrar información de un episodio
    info_parser = subparsers.add_parser(
        "info", help="Mostrar información de un episodio"
    )
    info_parser.add_argument("episode_id", type=int, help="ID del episodio")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Inicializar base de datos
    db.initialize_database()

    if args.command == "extract":
        extract_web_info(args)
    elif args.command == "compare":
        compare_rss_vs_web(args)
    elif args.command == "list":
        list_episodes_without_web_info(args)
    elif args.command == "info":
        show_episode_info(args)


def extract_web_info(args):
    """Extrae información de la web."""
    extractor = WebExtractor()

    if args.episode_id:
        # Procesar un episodio específico
        podcast = db.get_podcast_by_id(args.episode_id)
        if not podcast:
            print(f"❌ No se encontró el episodio con ID {args.episode_id}")
            return

        print(f"📄 Procesando episodio específico: {podcast['title']}")

        # Convertir a formato esperado por el extractor
        podcast_dict = {
            "id": podcast["id"],
            "program_number": podcast["program_number"],
            "date": podcast["date"],
        }

        wordpress_url = extractor._find_wordpress_url(podcast_dict)
        if wordpress_url:
            web_info = extractor._extract_episode_page_info(wordpress_url)
            db.update_web_info(
                podcast_id=podcast["id"],
                wordpress_url=wordpress_url,
                cover_image_url=web_info.get("cover_image_url"),
                web_extra_links=web_info.get("extra_links_json"),
                web_playlist=web_info.get("playlist_json"),
            )
            print(f"✅ Episodio {podcast['program_number']} procesado correctamente")
        else:
            print("⚠️  No se encontró URL de WordPress para el episodio")
    else:
        # Procesar todos los episodios sin información web
        extractor.extract_all_web_info(max_episodes=args.max_episodes)


def compare_rss_vs_web(args):
    """Compara la información del RSS con la de la web."""
    extractor = WebExtractor()
    discrepancies = extractor.compare_rss_vs_web(args.episode_id)

    if args.json:
        print(json.dumps(discrepancies, indent=2, ensure_ascii=False))
    else:
        print(f"🔍 Comparación RSS vs Web para episodio {args.episode_id}")
        print("=" * 50)

        if "error" in discrepancies:
            print(f"❌ {discrepancies['error']}")
            return

        summary = discrepancies["summary"]
        print("📊 Resumen:")
        print(f"   Canciones RSS: {summary['rss_songs_count']}")
        print(f"   Canciones Web: {summary['web_songs_count']}")
        print(f"   Enlaces RSS: {summary['rss_links_count']}")
        print(f"   Enlaces Web: {summary['web_links_count']}")
        print(
            f"   Tiene discrepancias: {'Sí' if summary['has_discrepancies'] else 'No'}"
        )

        if discrepancies["songs_differences"]:
            print("\n🎵 Diferencias en canciones:")
            for diff in discrepancies["songs_differences"]:
                print(f"   • {diff}")

        if discrepancies["links_differences"]:
            print("\n🔗 Diferencias en enlaces:")
            for diff in discrepancies["links_differences"]:
                print(f"   • {diff}")


def list_episodes_without_web_info(args):
    """Lista episodios sin información web."""
    podcasts = db.get_podcasts_without_web_info()

    print(
        f"📋 Episodios sin información web (mostrando {min(args.limit, len(podcasts))}):"
    )
    print("=" * 60)

    for i, podcast in enumerate(podcasts[: args.limit]):
        print(
            f"{i+1:2d}. ID: {podcast['id']:3d} | #{podcast['program_number']:3s} | {podcast['date']} | {podcast['title'][:50]}..."
        )

    if len(podcasts) > args.limit:
        print(f"\n... y {len(podcasts) - args.limit} más")


def show_episode_info(args):
    """Muestra información detallada de un episodio."""
    podcast = db.get_podcast_by_id(args.episode_id)
    if not podcast:
        print(f"❌ No se encontró el episodio con ID {args.episode_id}")
        return

    print(f"📄 Información del episodio {args.episode_id}")
    print("=" * 50)
    print(f"Título: {podcast['title']}")
    print(f"Fecha: {podcast['date']}")
    print(f"Número: {podcast['program_number']}")
    print(f"URL iVoox: {podcast['url']}")

    # Información de la web
    web_info = db.get_podcast_web_info(args.episode_id)
    if web_info:
        print("\n🌐 Información de la web:")
        print(f"   URL WordPress: {web_info.get('wordpress_url', 'No disponible')}")
        print(f"   Imagen portada: {web_info.get('cover_image_url', 'No disponible')}")
        print(f"   Último check: {web_info.get('last_web_check', 'No disponible')}")

        if web_info.get("web_extra_links"):
            try:
                links = json.loads(web_info["web_extra_links"])
                print(f"   Enlaces extras: {len(links)} encontrados")
            except json.JSONDecodeError:
                print("   Enlaces extras: Error parseando")

        if web_info.get("web_playlist"):
            try:
                songs = json.loads(web_info["web_playlist"])
                print(f"   Canciones web: {len(songs)} encontradas")
            except json.JSONDecodeError:
                print("   Canciones web: Error parseando")
    else:
        print("\n🌐 Información de la web: No disponible")

    # Canciones del RSS
    rss_songs = db.get_songs_by_podcast_id(args.episode_id)
    print(f"\n🎵 Canciones del RSS: {len(rss_songs)}")

    # Enlaces extras del RSS
    rss_links = db.get_extra_links_by_podcast_id(args.episode_id)
    print(f"🔗 Enlaces extras del RSS: {len(rss_links)}")


if __name__ == "__main__":
    main()
