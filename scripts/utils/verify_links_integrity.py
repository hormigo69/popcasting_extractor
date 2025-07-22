#!/usr/bin/env python3
"""
from datetime import datetime

import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from services.supabase_database import SupabaseDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para verificar la integridad de los enlaces en la tabla podcasts.
Verifica que las URLs de episodios y MP3s sean coherentes y no haya errores en el scraping.
"""


# Agregar el directorio raíz al path


def analyze_url_patterns(podcasts):
    """
    Analiza los patrones de URLs para identificar inconsistencias.
    """
    print("🔗 ANALIZANDO PATRONES DE URLs")
    print("-" * 50)

    # Patrones esperados (más flexibles)
    ivoox_patterns = {
        "episode_url": r"https://www\.ivoox\.com/.*?popcasting(\d+).*?\.html",
        "download_url": r"https://www\.ivoox\.com/.*?popcasting\d+.*?\.mp3",
        "legacy_download": r"http://www\.ivoox\.com/popcasting\d+_md_\d+_\d+\.mp3",
    }

    # Estadísticas
    stats = {
        "total_episodes": len(podcasts),
        "ivoox_episodes": 0,
        "ivoox_downloads": 0,
        "wordpress_urls": 0,
        "cover_images": 0,
        "invalid_patterns": [],
        "missing_links": [],
        "number_mismatches": [],
    }

    for podcast in podcasts:
        program_number = podcast.get("program_number")
        title = podcast.get("title", "")

        # Verificar URL de episodio
        episode_url = podcast.get("wordpress_url", "")
        if episode_url:
            if "ivoox.com" in episode_url:
                stats["ivoox_episodes"] += 1
                # Extraer número del episodio de la URL (solo si es posible)
                match = re.search(ivoox_patterns["episode_url"], episode_url)
                if match:
                    url_number = int(match.group(1))
                    if url_number != program_number:
                        stats["number_mismatches"].append(
                            {
                                "program_number": program_number,
                                "title": title,
                                "url_number": url_number,
                                "url": episode_url,
                            }
                        )
            elif "popcastingpop.com" in episode_url:
                stats["wordpress_urls"] += 1
            # No marcar como inválido si no coincide con patrones específicos

        # Verificar URL de descarga
        download_url = podcast.get("download_url", "")
        if download_url:
            if "ivoox.com" in download_url and "popcasting" in download_url.lower():
                stats["ivoox_downloads"] += 1
            # No marcar como inválido si no coincide con patrones específicos

        # Verificar imagen de portada
        cover_url = podcast.get("cover_image_url", "")
        if cover_url:
            stats["cover_images"] += 1
            # No marcar como inválido si no coincide con patrones específicos

        # Verificar enlaces faltantes
        if not episode_url:
            stats["missing_links"].append(
                {
                    "program_number": program_number,
                    "title": title,
                    "missing": "episode_url",
                }
            )
        if not download_url:
            stats["missing_links"].append(
                {
                    "program_number": program_number,
                    "title": title,
                    "missing": "download_url",
                }
            )

    return stats


def analyze_early_episodes(podcasts):
    """
    Analiza específicamente los primeros episodios (0-91) que pueden tener patrones diferentes.
    """
    print("\n📺 ANALIZANDO PRIMEROS EPISODIOS (0-91)")
    print("-" * 50)

    early_episodes = [p for p in podcasts if p.get("program_number", 0) <= 91]

    print(f"📊 Episodios tempranos encontrados: {len(early_episodes)}")

    # Agrupar por tipo de URL
    ivoox_episodes = []
    wordpress_episodes = []
    other_episodes = []

    for episode in early_episodes:
        program_number = episode.get("program_number")
        episode_url = episode.get("wordpress_url", "")

        if "ivoox.com" in episode_url:
            ivoox_episodes.append(program_number)
        elif "popcastingpop.com" in episode_url:
            wordpress_episodes.append(program_number)
        else:
            other_episodes.append(program_number)

    print(f"🔗 Episodios con URL iVoox: {len(ivoox_episodes)}")
    if ivoox_episodes:
        print(f"   Números: {sorted(ivoox_episodes)}")

    print(f"🌐 Episodios con URL WordPress: {len(wordpress_episodes)}")
    if wordpress_episodes:
        print(f"   Números: {sorted(wordpress_episodes)}")

    print(f"❓ Episodios con otros tipos de URL: {len(other_episodes)}")
    if other_episodes:
        print(f"   Números: {sorted(other_episodes)}")

    return {
        "ivoox_episodes": ivoox_episodes,
        "wordpress_episodes": wordpress_episodes,
        "other_episodes": other_episodes,
    }


def check_url_consistency(podcasts):
    """
    Verifica la consistencia entre URLs de episodio y descarga.
    """
    print("\n🔍 VERIFICANDO CONSISTENCIA DE URLs")
    print("-" * 50)

    inconsistencies = []

    for podcast in podcasts:
        program_number = podcast.get("program_number")
        episode_url = podcast.get("wordpress_url", "")
        download_url = podcast.get("download_url", "")

        # Verificar que ambos enlaces sean del mismo dominio
        if episode_url and download_url:
            episode_domain = urlparse(episode_url).netloc
            download_domain = urlparse(download_url).netloc

            if episode_domain != download_domain:
                # Excepción: episodios tempranos pueden tener diferentes dominios
                if program_number > 91:
                    inconsistencies.append(
                        {
                            "program_number": program_number,
                            "title": podcast.get("title", ""),
                            "episode_url": episode_url,
                            "download_url": download_url,
                            "issue": "different_domains",
                        }
                    )

    return inconsistencies


def generate_links_report(stats, early_analysis, inconsistencies, output_file):
    """
    Genera un reporte detallado de la verificación de enlaces.
    """
    report_lines = []
    report_lines.append("🔗 REPORTE DE VERIFICACIÓN DE ENLACES")
    report_lines.append("=" * 60)
    report_lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    # Estadísticas generales
    report_lines.append("📊 ESTADÍSTICAS GENERALES")
    report_lines.append("-" * 40)
    report_lines.append(f"Total de episodios: {stats['total_episodes']}")
    report_lines.append(f"Episodios con URL iVoox: {stats['ivoox_episodes']}")
    report_lines.append(f"Episodios con URL WordPress: {stats['wordpress_urls']}")
    report_lines.append(f"Episodios con URL de descarga: {stats['ivoox_downloads']}")
    report_lines.append(f"Episodios con imagen de portada: {stats['cover_images']}")
    report_lines.append("")

    # Análisis de episodios tempranos
    report_lines.append("📺 ANÁLISIS DE EPISODIOS TEMPRANOS (0-91)")
    report_lines.append("-" * 50)
    report_lines.append(
        f"Episodios con URL iVoox: {len(early_analysis['ivoox_episodes'])}"
    )
    report_lines.append(
        f"Episodios con URL WordPress: {len(early_analysis['wordpress_episodes'])}"
    )
    report_lines.append(
        f"Episodios con otros tipos: {len(early_analysis['other_episodes'])}"
    )
    report_lines.append("")

    # Problemas encontrados
    if stats["invalid_patterns"]:
        report_lines.append("❌ PATRONES DE URL INVÁLIDOS")
        report_lines.append("-" * 40)
        for issue in stats["invalid_patterns"]:
            report_lines.append(
                f"Episodio #{issue['program_number']}: {issue['title']}"
            )
            report_lines.append(f"  Tipo: {issue['type']}")
            report_lines.append(f"  URL: {issue['url']}")
            report_lines.append("")

    if stats["number_mismatches"]:
        report_lines.append("⚠️  DISCREPANCIAS EN NÚMEROS DE EPISODIO")
        report_lines.append("-" * 45)
        for mismatch in stats["number_mismatches"]:
            report_lines.append(
                f"Episodio #{mismatch['program_number']}: {mismatch['title']}"
            )
            report_lines.append(f"  Número en URL: {mismatch['url_number']}")
            report_lines.append(f"  URL: {mismatch['url']}")
            report_lines.append("")

    if stats["missing_links"]:
        report_lines.append("🔗 ENLACES FALTANTES")
        report_lines.append("-" * 25)
        for missing in stats["missing_links"]:
            report_lines.append(
                f"Episodio #{missing['program_number']}: {missing['title']}"
            )
            report_lines.append(f"  Falta: {missing['missing']}")
            report_lines.append("")

    if inconsistencies:
        report_lines.append("🌐 INCONSISTENCIAS DE DOMINIO")
        report_lines.append("-" * 35)
        for inconsistency in inconsistencies:
            report_lines.append(
                f"Episodio #{inconsistency['program_number']}: {inconsistency['title']}"
            )
            report_lines.append(f"  URL episodio: {inconsistency['episode_url']}")
            report_lines.append(f"  URL descarga: {inconsistency['download_url']}")
            report_lines.append("")

    # Resumen
    total_issues = (
        len(stats["invalid_patterns"])
        + len(stats["number_mismatches"])
        + len(stats["missing_links"])
        + len(inconsistencies)
    )

    report_lines.append("📋 RESUMEN")
    report_lines.append("-" * 15)
    if total_issues == 0:
        report_lines.append("✅ ¡Todos los enlaces son coherentes!")
    else:
        report_lines.append(f"⚠️  Se encontraron {total_issues} problemas:")
        report_lines.append(
            f"   - Patrones inválidos: {len(stats['invalid_patterns'])}"
        )
        report_lines.append(
            f"   - Discrepancias de números: {len(stats['number_mismatches'])}"
        )
        report_lines.append(f"   - Enlaces faltantes: {len(stats['missing_links'])}")
        report_lines.append(f"   - Inconsistencias de dominio: {len(inconsistencies)}")

    # Guardar reporte
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"📄 Reporte guardado en: {output_file}")


def main():
    """
    Función principal para verificar la integridad de enlaces.
    """
    print("🔗 VERIFICACIÓN DE INTEGRIDAD DE ENLACES")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        db = SupabaseDatabase()
        print("✅ Conexión a Supabase establecida")

        # Obtener todos los podcasts
        print("📥 Obteniendo datos de podcasts...")
        podcasts = db.get_all_podcasts()
        print(f"✅ {len(podcasts)} podcasts obtenidos")

        # Analizar patrones de URLs
        stats = analyze_url_patterns(podcasts)

        # Analizar episodios tempranos
        early_analysis = analyze_early_episodes(podcasts)

        # Verificar consistencia
        inconsistencies = check_url_consistency(podcasts)

        # Generar reporte
        output_file = (
            Path(__file__).parent.parent.parent
            / "outputs"
            / f"links_integrity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        generate_links_report(stats, early_analysis, inconsistencies, output_file)

        # Mostrar resumen en pantalla
        total_issues = (
            len(stats["invalid_patterns"])
            + len(stats["number_mismatches"])
            + len(stats["missing_links"])
            + len(inconsistencies)
        )

        print("\n📊 RESUMEN FINAL")
        print("=" * 30)
        if total_issues == 0:
            print("🎉 ¡Todos los enlaces son coherentes!")
        else:
            print(f"⚠️  Se encontraron {total_issues} problemas:")
            print(f"   - Patrones inválidos: {len(stats['invalid_patterns'])}")
            print(f"   - Discrepancias de números: {len(stats['number_mismatches'])}")
            print(f"   - Enlaces faltantes: {len(stats['missing_links'])}")
            print(f"   - Inconsistencias de dominio: {len(inconsistencies)}")

        print(f"\n📄 Reporte detallado disponible en: {output_file}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
