#!/usr/bin/env python3
"""
Script para verificar que los links extras se guardaron correctamente en la base de datos
"""

import os
import sys

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import database as db


def check_extra_links():
    """Verifica los links extras en la base de datos"""

    # Obtener todos los podcasts
    podcasts = db.get_all_podcasts()

    print(f"Total de podcasts en la base de datos: {len(podcasts)}")

    # Contar podcasts con links extras
    podcasts_with_links = 0
    total_extra_links = 0

    for podcast in podcasts:
        extra_links = db.get_extra_links_by_podcast_id(podcast["id"])
        if extra_links:
            podcasts_with_links += 1
            total_extra_links += len(extra_links)

            print(f"\n📻 Podcast: {podcast['title']} ({podcast['date']})")
            print(f"   Links extras encontrados: {len(extra_links)}")
            for i, link in enumerate(extra_links, 1):
                print(f"   {i}. {link['text']} -> {link['url']}")

    print("\n📊 RESUMEN:")
    print(f"   - Podcasts con links extras: {podcasts_with_links}")
    print(f"   - Total de links extras: {total_extra_links}")
    print(
        f"   - Porcentaje de podcasts con links: {(podcasts_with_links/len(podcasts)*100):.1f}%"
    )


if __name__ == "__main__":
    check_extra_links()
