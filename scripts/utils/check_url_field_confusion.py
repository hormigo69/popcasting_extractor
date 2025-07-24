#!/usr/bin/env python3
"""
Script para verificar si hay URLs confundidas entre los campos url y wordpress_url.
"""

import os
import sys
from urllib.parse import urlparse

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase


def check_url_field_confusion():
    """Verifica si hay URLs confundidas entre campos."""

    print("🔍 VERIFICACIÓN DE CONFUSIÓN DE URLs ENTRE CAMPOS")
    print("=" * 60)

    # Conectar a Supabase
    db = SupabaseDatabase()

    # Obtener todos los episodios con sus URLs
    response = (
        db.client.table("podcasts")
        .select("program_number,title,url,wordpress_url")
        .order("program_number")
        .execute()
    )

    episodes = response.data

    print(f"📊 Total de episodios analizados: {len(episodes)}")
    print()

    # Verificar confusión de URLs
    print("⚠️  EPISODIOS CON URLs CONFUNDIDAS:")
    print("-" * 40)

    confused_episodes = []

    for ep in episodes:
        url = ep["url"]
        wordpress_url = ep["wordpress_url"]

        if not url or not wordpress_url:
            continue

        # Verificar si hay confusión
        url_domain = urlparse(url).netloc
        wordpress_domain = urlparse(wordpress_url).netloc

        # Confusión: iVoox en wordpress_url Y WordPress en url
        if "ivoox.com" in wordpress_domain and "popcastingpop.com" in url_domain:
            confused_episodes.append(
                {
                    "episode": ep,
                    "type": "confusion",
                    "description": "iVoox en wordpress_url, WordPress en url",
                }
            )

    if confused_episodes:
        print(
            f"Se encontraron {len(confused_episodes)} episodios con URLs confundidas:"
        )
        print()
        for item in confused_episodes:
            ep = item["episode"]
            print(f"Episodio #{ep['program_number']}: {ep['title']}")
            print(f"  url: {ep['url']}")
            print(f"  wordpress_url: {ep['wordpress_url']}")
            print(f"  → {item['description']}")
            print()
    else:
        print("✅ No se encontraron URLs confundidas entre campos")
        print()

    # Verificar duplicados exactos
    print("🔄 EPISODIOS CON URLs DUPLICADAS:")
    print("-" * 40)

    duplicates = []
    for ep in episodes:
        if ep["url"] and ep["wordpress_url"] and ep["url"] == ep["wordpress_url"]:
            duplicates.append(ep)

    if duplicates:
        print(f"Se encontraron {len(duplicates)} episodios con URLs duplicadas:")
        print()
        for ep in duplicates[:10]:  # Mostrar solo los primeros 10
            print(f"Episodio #{ep['program_number']}: {ep['url']}")

        if len(duplicates) > 10:
            print(f"... y {len(duplicates) - 10} más")
        print()
    else:
        print("✅ No se encontraron URLs duplicadas")
        print()

    # Análisis por rangos
    print("📊 ANÁLISIS POR RANGOS:")
    print("-" * 40)

    episodes_0_91 = [ep for ep in episodes if ep["program_number"] <= 91]
    episodes_92_plus = [ep for ep in episodes if ep["program_number"] >= 92]

    # Episodios 0-91
    print("Episodios 0-91:")
    ivoox_in_url = sum(
        1 for ep in episodes_0_91 if ep["url"] and "ivoox.com" in ep["url"]
    )
    ivoox_in_wordpress = sum(
        1
        for ep in episodes_0_91
        if ep["wordpress_url"] and "ivoox.com" in ep["wordpress_url"]
    )
    wordpress_in_url = sum(
        1 for ep in episodes_0_91 if ep["url"] and "popcastingpop.com" in ep["url"]
    )
    wordpress_in_wordpress = sum(
        1
        for ep in episodes_0_91
        if ep["wordpress_url"] and "popcastingpop.com" in ep["wordpress_url"]
    )

    print(f"  iVoox en 'url': {ivoox_in_url}/{len(episodes_0_91)}")
    print(f"  iVoox en 'wordpress_url': {ivoox_in_wordpress}/{len(episodes_0_91)}")
    print(f"  WordPress en 'url': {wordpress_in_url}/{len(episodes_0_91)}")
    print(
        f"  WordPress en 'wordpress_url': {wordpress_in_wordpress}/{len(episodes_0_91)}"
    )
    print()

    # Episodios 92+
    print("Episodios 92+:")
    ivoox_in_url = sum(
        1 for ep in episodes_92_plus if ep["url"] and "ivoox.com" in ep["url"]
    )
    ivoox_in_wordpress = sum(
        1
        for ep in episodes_92_plus
        if ep["wordpress_url"] and "ivoox.com" in ep["wordpress_url"]
    )
    wordpress_in_url = sum(
        1 for ep in episodes_92_plus if ep["url"] and "popcastingpop.com" in ep["url"]
    )
    wordpress_in_wordpress = sum(
        1
        for ep in episodes_92_plus
        if ep["wordpress_url"] and "popcastingpop.com" in ep["wordpress_url"]
    )

    print(f"  iVoox en 'url': {ivoox_in_url}/{len(episodes_92_plus)}")
    print(f"  iVoox en 'wordpress_url': {ivoox_in_wordpress}/{len(episodes_92_plus)}")
    print(f"  WordPress en 'url': {wordpress_in_url}/{len(episodes_92_plus)}")
    print(
        f"  WordPress en 'wordpress_url': {wordpress_in_wordpress}/{len(episodes_92_plus)}"
    )
    print()

    # Resumen
    print("📋 RESUMEN:")
    print("-" * 40)
    print(f"Episodios con URLs confundidas: {len(confused_episodes)}")
    print(f"Episodios con URLs duplicadas: {len(duplicates)}")

    if confused_episodes:
        print("\n🔧 ACCIÓN NECESARIA:")
        print("Hay URLs confundidas que necesitan ser intercambiadas")
    else:
        print("\n✅ No hay URLs confundidas")


if __name__ == "__main__":
    check_url_field_confusion()
