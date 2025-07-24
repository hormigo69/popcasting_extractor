#!/usr/bin/env python3
"""
Script para analizar la coherencia de las URLs en la tabla podcasts.
Analiza los campos url y wordpress_url para identificar inconsistencias.
"""

import os
import sys
from datetime import datetime
from urllib.parse import urlparse

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase


def analyze_url_coherence():
    """Analiza la coherencia de las URLs en la tabla podcasts."""

    print("🔍 ANÁLISIS DE COHERENCIA DE URLs EN LA BASE DE DATOS")
    print("=" * 60)

    # Conectar a Supabase
    db = SupabaseDatabase()

    # Obtener todos los episodios con sus URLs
    response = (
        db.client.table("podcasts")
        .select("program_number,title,url,wordpress_url,download_url,date")
        .order("program_number")
        .execute()
    )

    result = response.data

    if not result:
        print("❌ No se pudieron obtener datos de la base de datos")
        return

    episodes = result

    print(f"📊 Total de episodios analizados: {len(episodes)}")
    print()

    # Análisis por rangos de episodios
    episodes_0_91 = [ep for ep in episodes if ep["program_number"] <= 91]
    episodes_92_plus = [ep for ep in episodes if ep["program_number"] >= 92]

    print("📈 DISTRIBUCIÓN POR RANGOS:")
    print(f"   Episodios 0-91: {len(episodes_0_91)}")
    print(f"   Episodios 92+: {len(episodes_92_plus)}")
    print()

    # Análisis del campo 'url'
    print("🔗 ANÁLISIS DEL CAMPO 'url':")
    print("-" * 40)

    url_domains = {}
    url_ivoox_count = 0
    url_wordpress_count = 0
    url_other_count = 0
    url_empty_count = 0

    for ep in episodes:
        url = ep["url"]
        if not url:
            url_empty_count += 1
            continue

        domain = urlparse(url).netloc
        url_domains[domain] = url_domains.get(domain, 0) + 1

        if "ivoox.com" in domain:
            url_ivoox_count += 1
        elif "popcastingpop.com" in domain:
            url_wordpress_count += 1
        else:
            url_other_count += 1

    print(f"   URLs vacías: {url_empty_count}")
    print(f"   URLs iVoox: {url_ivoox_count}")
    print(f"   URLs WordPress: {url_wordpress_count}")
    print(f"   URLs otros dominios: {url_other_count}")
    print()

    print("   Dominios encontrados en 'url':")
    for domain, count in sorted(url_domains.items(), key=lambda x: x[1], reverse=True):
        print(f"     {domain}: {count}")
    print()

    # Análisis del campo 'wordpress_url'
    print("🌐 ANÁLISIS DEL CAMPO 'wordpress_url':")
    print("-" * 40)

    wordpress_domains = {}
    wordpress_popcasting_count = 0
    wordpress_other_count = 0
    wordpress_empty_count = 0

    for ep in episodes:
        wordpress_url = ep["wordpress_url"]
        if not wordpress_url:
            wordpress_empty_count += 1
            continue

        domain = urlparse(wordpress_url).netloc
        wordpress_domains[domain] = wordpress_domains.get(domain, 0) + 1

        if "popcastingpop.com" in domain:
            wordpress_popcasting_count += 1
        else:
            wordpress_other_count += 1

    print(f"   URLs vacías: {wordpress_empty_count}")
    print(f"   URLs popcastingpop.com: {wordpress_popcasting_count}")
    print(f"   URLs otros dominios: {wordpress_other_count}")
    print()

    print("   Dominios encontrados en 'wordpress_url':")
    for domain, count in sorted(
        wordpress_domains.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"     {domain}: {count}")
    print()

    # Análisis de inconsistencias específicas
    print("⚠️  INCONSISTENCIAS DETECTADAS:")
    print("-" * 40)

    # 1. URLs que deberían ser iVoox pero son WordPress
    print("1. URLs que deberían ser iVoox pero son WordPress:")
    inconsistent_ivoox = []
    for ep in episodes:
        if ep["url"] and "popcastingpop.com" in ep["url"]:
            inconsistent_ivoox.append(ep)

    if inconsistent_ivoox:
        for ep in inconsistent_ivoox:
            print(f"   Episodio #{ep['program_number']}: {ep['url']}")
    else:
        print("   ✅ No se encontraron inconsistencias")
    print()

    # 2. WordPress URLs que no son de popcastingpop.com
    print("2. WordPress URLs que no son de popcastingpop.com:")
    inconsistent_wordpress = []
    for ep in episodes:
        if ep["wordpress_url"] and "popcastingpop.com" not in ep["wordpress_url"]:
            inconsistent_wordpress.append(ep)

    if inconsistent_wordpress:
        for ep in inconsistent_wordpress:
            print(f"   Episodio #{ep['program_number']}: {ep['wordpress_url']}")
    else:
        print("   ✅ No se encontraron inconsistencias")
    print()

    # 3. Análisis por rangos de episodios
    print("📊 ANÁLISIS POR RANGOS DE EPISODIOS:")
    print("-" * 40)

    # Episodios 0-91
    print("Episodios 0-91:")
    ivoox_0_91 = sum(
        1 for ep in episodes_0_91 if ep["url"] and "ivoox.com" in ep["url"]
    )
    wordpress_0_91 = sum(
        1
        for ep in episodes_0_91
        if ep["wordpress_url"] and "popcastingpop.com" in ep["wordpress_url"]
    )
    print(
        f"   URLs iVoox: {ivoox_0_91}/{len(episodes_0_91)} ({ivoox_0_91/len(episodes_0_91)*100:.1f}%)"
    )
    print(
        f"   URLs WordPress: {wordpress_0_91}/{len(episodes_0_91)} ({wordpress_0_91/len(episodes_0_91)*100:.1f}%)"
    )

    # Episodios 92+
    print("Episodios 92+:")
    ivoox_92_plus = sum(
        1 for ep in episodes_92_plus if ep["url"] and "ivoox.com" in ep["url"]
    )
    wordpress_92_plus = sum(
        1
        for ep in episodes_92_plus
        if ep["wordpress_url"] and "popcastingpop.com" in ep["wordpress_url"]
    )
    print(
        f"   URLs iVoox: {ivoox_92_plus}/{len(episodes_92_plus)} ({ivoox_92_plus/len(episodes_92_plus)*100:.1f}%)"
    )
    print(
        f"   URLs WordPress: {wordpress_92_plus}/{len(episodes_92_plus)} ({wordpress_92_plus/len(episodes_92_plus)*100:.1f}%)"
    )
    print()

    # 4. Episodios con ambos campos vacíos
    print("4. Episodios con ambos campos URL vacíos:")
    both_empty = [ep for ep in episodes if not ep["url"] and not ep["wordpress_url"]]
    if both_empty:
        for ep in both_empty:
            print(f"   Episodio #{ep['program_number']}: {ep['title']}")
    else:
        print("   ✅ No hay episodios con ambos campos vacíos")
    print()

    # 5. Episodios con URLs duplicadas entre campos
    print("5. Episodios con URLs duplicadas entre campos:")
    duplicates = []
    for ep in episodes:
        if ep["url"] and ep["wordpress_url"] and ep["url"] == ep["wordpress_url"]:
            duplicates.append(ep)

    if duplicates:
        for ep in duplicates:
            print(f"   Episodio #{ep['program_number']}: {ep['url']}")
    else:
        print("   ✅ No hay URLs duplicadas entre campos")
    print()

    # Resumen y recomendaciones
    print("📋 RESUMEN Y RECOMENDACIONES:")
    print("-" * 40)

    total_inconsistencies = (
        len(inconsistent_ivoox) + len(inconsistent_wordpress) + len(duplicates)
    )

    print(f"Total de inconsistencias encontradas: {total_inconsistencies}")
    print()

    if total_inconsistencies > 0:
        print("🔧 ACCIONES RECOMENDADAS:")
        print(
            "1. Corregir URLs del campo 'url' que apuntan a WordPress en lugar de iVoox"
        )
        print(
            "2. Verificar y corregir URLs del campo 'wordpress_url' que no son de popcastingpop.com"
        )
        print("3. Eliminar duplicados entre campos url y wordpress_url")
        print(
            "4. Asegurar que los episodios 92+ tengan URLs WordPress en wordpress_url"
        )
    else:
        print("✅ La base de datos tiene URLs coherentes")

    # Guardar reporte detallado
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = f"logs/url_coherence_analysis_{timestamp}.txt"

    os.makedirs("logs", exist_ok=True)

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("ANÁLISIS DE COHERENCIA DE URLs\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total episodios: {len(episodes)}\n\n")

        f.write("INCONSISTENCIAS DETECTADAS:\n")
        f.write("-" * 30 + "\n")

        if inconsistent_ivoox:
            f.write("URLs que deberían ser iVoox pero son WordPress:\n")
            for ep in inconsistent_ivoox:
                f.write(f"  Episodio #{ep['program_number']}: {ep['url']}\n")
            f.write("\n")

        if inconsistent_wordpress:
            f.write("WordPress URLs que no son de popcastingpop.com:\n")
            for ep in inconsistent_wordpress:
                f.write(f"  Episodio #{ep['program_number']}: {ep['wordpress_url']}\n")
            f.write("\n")

        if duplicates:
            f.write("URLs duplicadas entre campos:\n")
            for ep in duplicates:
                f.write(f"  Episodio #{ep['program_number']}: {ep['url']}\n")
            f.write("\n")

    print(f"📄 Reporte detallado guardado en: {report_file}")


if __name__ == "__main__":
    analyze_url_coherence()
