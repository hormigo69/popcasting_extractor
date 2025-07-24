#!/usr/bin/env python3
"""
Script para revisar todos los episodios que fueron corregidos anteriormente
y verificar que las URLs sean realmente correctas.
"""

import logging
import os
import re
import sys

# Añadir el directorio raíz al path para importar los servicios
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.config import is_supabase_enabled
from services.supabase_database import SupabaseDatabase

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/review_all_corrected_episodes.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CorrectedEpisodesReviewer:
    def __init__(self):
        if not is_supabase_enabled():
            raise ValueError("Este script requiere Supabase como base de datos")
        self.db = SupabaseDatabase()

    def get_all_episodes_with_cover_images(self) -> list[dict]:
        """Obtiene todos los episodios que tienen cover_image_url."""
        try:
            response = (
                self.db.client.table("podcasts")
                .select("id,program_number,title,cover_image_url,wordpress_url")
                .not_.is_("cover_image_url", "null")
                .neq("cover_image_url", "")
                .order("program_number")
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error obteniendo episodios con cover: {e}")
            return []

    def identify_problematic_urls(self, episodes: list[dict]) -> list[dict]:
        """Identifica URLs problemáticas basándose en patrones conocidos."""
        problematic_episodes = []

        for episode in episodes:
            url = episode["cover_image_url"]
            episode["program_number"]
            episode["title"]

            problems = []

            # URLs de Gravatar (no son imágenes de portada reales)
            if "gravatar.com" in url or "blavatar" in url:
                problems.append("URL de Gravatar")

            # URLs de Google Images
            if "gstatic.com" in url or "encrypted-tbn" in url:
                problems.append("URL de Google Images")

            # URLs de Pinterest
            if "pinimg.com" in url or "media-cache-ak0.pinimg.com" in url:
                problems.append("URL de Pinterest")

            # URLs de descarga o iconos pequeños
            if "downloadsmall.jpg" in url or "download" in url.lower():
                problems.append("URL de descarga/icono pequeño")

            # URLs con nombres genéricos
            if any(
                generic in url.lower() for generic in ["descarga", "image", "images"]
            ):
                problems.append("Nombre de archivo genérico")

            # URLs con dimensiones muy pequeñas en el nombre
            if re.search(r"(\d+)x(\d+)", url):
                dimensions = re.findall(r"(\d+)x(\d+)", url)
                for w, h in dimensions:
                    if int(w) < 50 or int(h) < 50:
                        problems.append(f"Dimensiones muy pequeñas ({w}x{h})")

            # URLs de RSS pequeñas
            if "rsssmall.jpg" in url:
                problems.append("Imagen RSS pequeña")

            # URLs que no parecen ser imágenes de portada
            if not re.search(r"\.(jpg|jpeg|png|gif)(?:\?|$)", url, re.I):
                problems.append("Sin extensión de imagen")

            # URLs con parámetros de query (ya deberían estar limpias)
            if "?" in url and any(param in url for param in ["w=", "h=", "s=", "ts="]):
                problems.append("Parámetros de query")

            if problems:
                problematic_episodes.append(
                    {"episode": episode, "problems": problems, "url": url}
                )

        return problematic_episodes

    def generate_review_report(self, episodes: list[dict]) -> str:
        """Genera un reporte completo de revisión."""
        problematic_episodes = self.identify_problematic_urls(episodes)

        report = f"""
=== REPORTE DE REVISIÓN DE EPISODIOS CORREGIDOS ===

RESUMEN GENERAL:
- Total episodios con imágenes de portada: {len(episodes)}
- Episodios con URLs problemáticas: {len(problematic_episodes)}
- Episodios con URLs correctas: {len(episodes) - len(problematic_episodes)}
- Tasa de URLs correctas: {((len(episodes) - len(problematic_episodes)) / len(episodes) * 100):.1f}%

DISTRIBUCIÓN POR DOMINIO:
"""

        # Analizar dominios
        domain_distribution = {}
        for episode in episodes:
            url = episode["cover_image_url"]
            domain_match = re.search(r"https?://([^/]+)", url)
            if domain_match:
                domain = domain_match.group(1)
                domain_distribution[domain] = domain_distribution.get(domain, 0) + 1

        for domain, count in sorted(
            domain_distribution.items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / len(episodes)) * 100
            report += f"- {domain}: {count} ({percentage:.1f}%)\n"

        if problematic_episodes:
            report += "\nEPISODIOS CON URLs PROBLEMÁTICAS:\n"
            report += "=" * 80 + "\n\n"

            for item in problematic_episodes:
                episode = item["episode"]
                problems = item["problems"]
                url = item["url"]

                report += f"Episodio #{episode['program_number']}: {episode['title']}\n"
                report += f"URL actual: {url}\n"
                report += f"URL WordPress: {episode['wordpress_url']}\n"
                report += f"Problemas: {', '.join(problems)}\n"
                report += "\n" + "-" * 80 + "\n\n"

        # Análisis por tipo de problema
        problem_types = {}
        for item in problematic_episodes:
            for problem in item["problems"]:
                problem_types[problem] = problem_types.get(problem, 0) + 1

        if problem_types:
            report += "\nANÁLISIS POR TIPO DE PROBLEMA:\n"
            for problem, count in sorted(
                problem_types.items(), key=lambda x: x[1], reverse=True
            ):
                report += f"- {problem}: {count} episodios\n"

        return report


def main():
    """Función principal."""
    logger.info("Iniciando revisión de todos los episodios corregidos...")

    reviewer = CorrectedEpisodesReviewer()
    episodes = reviewer.get_all_episodes_with_cover_images()

    if not episodes:
        logger.warning("No hay episodios con imágenes de portada para revisar.")
        return

    # Generar reporte de revisión
    report = reviewer.generate_review_report(episodes)
    print(report)

    # Guardar reporte en archivo
    with open(
        "logs/review_all_corrected_episodes_report.txt", "w", encoding="utf-8"
    ) as f:
        f.write(report)

    logger.info(
        "Revisión completada. Reporte guardado en logs/review_all_corrected_episodes_report.txt"
    )


if __name__ == "__main__":
    main()
