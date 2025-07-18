#!/usr/bin/env python3
"""
Script para mostrar la información de los links de los episodios de Popcasting
"""

import sys

from services import database as db


def format_file_size(size_bytes):
    """Formatea el tamaño del archivo en formato legible"""
    if not size_bytes:
        return "No disponible"

    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def show_episode_links(limit=10):
    """Muestra los links de los episodios más recientes"""
    print("🎵 Links de Episodios de Popcasting")
    print("=" * 80)

    try:
        # Obtener podcasts de la base de datos
        podcasts = db.get_all_podcasts()

        if not podcasts:
            print("❌ No se encontraron episodios en la base de datos")
            return

        print(f"📊 Total de episodios en la base de datos: {len(podcasts)}")
        print(f"📋 Mostrando los últimos {limit} episodios:\n")

        # Mostrar los episodios más recientes
        for i, podcast in enumerate(podcasts[:limit]):
            print(f"🎧 Episodio {i+1}: {podcast['title']}")
            print(f"   📅 Fecha: {podcast['date']}")
            print(f"   🔢 Número: {podcast['program_number']}")

            if podcast["url"]:
                print(f"   🌐 Web: {podcast['url']}")
            else:
                print("   🌐 Web: No disponible")

            if podcast["download_url"]:
                print(f"   ⬇️  Descarga: {podcast['download_url']}")
            else:
                print("   ⬇️  Descarga: No disponible")

            if podcast["file_size"]:
                size_formatted = format_file_size(podcast["file_size"])
                print(f"   📦 Tamaño: {size_formatted}")
            else:
                print("   📦 Tamaño: No disponible")

            print("-" * 80)

    except Exception as e:
        print(f"❌ Error al obtener los episodios: {e}")


def show_episode_stats():
    """Muestra estadísticas de los episodios"""
    print("\n📈 Estadísticas de Episodios")
    print("=" * 50)

    try:
        podcasts = db.get_all_podcasts()

        if not podcasts:
            print("❌ No se encontraron episodios")
            return

        # Estadísticas básicas
        total_episodes = len(podcasts)
        episodes_with_web = sum(1 for p in podcasts if p["url"])
        episodes_with_download = sum(1 for p in podcasts if p["download_url"])
        episodes_with_size = sum(1 for p in podcasts if p["file_size"])

        print(f"📊 Total de episodios: {total_episodes}")
        print(
            f"🌐 Con URL web: {episodes_with_web} ({episodes_with_web/total_episodes*100:.1f}%)"
        )
        print(
            f"⬇️  Con URL descarga: {episodes_with_download} ({episodes_with_download/total_episodes*100:.1f}%)"
        )
        print(
            f"📦 Con tamaño de archivo: {episodes_with_size} ({episodes_with_size/total_episodes*100:.1f}%)"
        )

        # Estadísticas de tamaño
        if episodes_with_size > 0:
            sizes = [p["file_size"] for p in podcasts if p["file_size"]]
            avg_size = sum(sizes) / len(sizes)
            min_size = min(sizes)
            max_size = max(sizes)

            print("\n📦 Estadísticas de tamaño:")
            print(f"   • Promedio: {format_file_size(avg_size)}")
            print(f"   • Mínimo: {format_file_size(min_size)}")
            print(f"   • Máximo: {format_file_size(max_size)}")

    except Exception as e:
        print(f"❌ Error al calcular estadísticas: {e}")


def search_episode_by_number(program_number):
    """Busca un episodio específico por número"""
    print(f"\n🔍 Buscando episodio número: {program_number}")
    print("=" * 50)

    try:
        podcasts = db.get_all_podcasts()

        found_episodes = []
        for podcast in podcasts:
            if podcast["program_number"] == str(program_number):
                found_episodes.append(podcast)

        if not found_episodes:
            print(f"❌ No se encontró ningún episodio con el número {program_number}")
            return

        for episode in found_episodes:
            print(f"🎧 {episode['title']}")
            print(f"   📅 Fecha: {episode['date']}")
            print(f"   🌐 Web: {episode['url']}")
            print(f"   ⬇️  Descarga: {episode['download_url']}")
            if episode["file_size"]:
                print(f"   📦 Tamaño: {format_file_size(episode['file_size'])}")
            print()

    except Exception as e:
        print(f"❌ Error al buscar episodio: {e}")


def main():
    """Función principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "stats":
            show_episode_stats()
        elif command == "search" and len(sys.argv) > 2:
            program_number = sys.argv[2]
            search_episode_by_number(program_number)
        elif command == "help":
            print("Uso del script:")
            print(
                "  python show_episode_links.py          # Mostrar últimos 10 episodios"
            )
            print("  python show_episode_links.py stats    # Mostrar estadísticas")
            print("  python show_episode_links.py search N # Buscar episodio número N")
            print("  python show_episode_links.py help     # Mostrar esta ayuda")
        else:
            print("❌ Comando no válido. Usa 'help' para ver las opciones disponibles.")
    else:
        # Comportamiento por defecto: mostrar últimos episodios
        show_episode_links()
        show_episode_stats()


if __name__ == "__main__":
    main()
