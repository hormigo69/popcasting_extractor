#!/usr/bin/env python3
"""
Script para verificar que todas las URLs de imágenes de portada sean válidas.
Hace una verificación exhaustiva de las URLs y reporta problemas.
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
        logging.FileHandler("logs/verify_cover_image_urls.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CoverImageURLVerifier:
    def __init__(self):
        if not is_supabase_enabled():
            raise ValueError("Este script requiere Supabase como base de datos")
        self.db = SupabaseDatabase()

    def get_episodes_with_cover_images(self) -> list[dict]:
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

    def analyze_url_patterns(self, episodes: list[dict]) -> dict:
        """Analiza los patrones de URLs para identificar problemas."""
        analysis = {
            "total_episodes": len(episodes),
            "url_patterns": {},
            "problematic_urls": [],
            "domain_distribution": {},
            "file_extension_distribution": {},
            "size_patterns": {},
        }

        for episode in episodes:
            url = episode["cover_image_url"]
            episode["program_number"]

            # Analizar dominio
            domain_match = re.search(r"https?://([^/]+)", url)
            if domain_match:
                domain = domain_match.group(1)
                analysis["domain_distribution"][domain] = (
                    analysis["domain_distribution"].get(domain, 0) + 1
                )

            # Analizar extensión de archivo
            ext_match = re.search(r"\.([a-zA-Z0-9]+)(?:\?|$)", url)
            if ext_match:
                ext = ext_match.group(1).lower()
                analysis["file_extension_distribution"][ext] = (
                    analysis["file_extension_distribution"].get(ext, 0) + 1
                )

            # Analizar patrones de tamaño en el nombre
            size_match = re.search(r"(\d+)x(\d+)", url)
            if size_match:
                width, height = int(size_match.group(1)), int(size_match.group(2))
                size_key = f"{width}x{height}"
                analysis["size_patterns"][size_key] = (
                    analysis["size_patterns"].get(size_key, 0) + 1
                )

            # Identificar URLs problemáticas
            problems = []

            # URLs de Gravatar
            if "gravatar.com" in url or "blavatar" in url:
                problems.append("Gravatar URL")

            # URLs con nombres genéricos
            if any(
                generic in url.lower()
                for generic in ["download", "descarga", "image", "images"]
            ):
                problems.append("Nombre genérico")

            # URLs sin extensión de imagen
            if not re.search(r"\.(jpg|jpeg|png|gif)(?:\?|$)", url, re.I):
                problems.append("Sin extensión de imagen")

            # URLs con dimensiones muy pequeñas
            if size_match and (
                int(size_match.group(1)) < 50 or int(size_match.group(2)) < 50
            ):
                problems.append("Dimensiones muy pequeñas")

            if problems:
                analysis["problematic_urls"].append(
                    {"episode": episode, "url": url, "problems": problems}
                )

        return analysis

    def generate_url_statistics(self, episodes: list[dict]) -> str:
        """Genera estadísticas detalladas de las URLs."""
        analysis = self.analyze_url_patterns(episodes)

        stats = f"""
=== ESTADÍSTICAS DE URLs DE IMÁGENES DE PORTADA ===

RESUMEN GENERAL:
- Total episodios: {analysis['total_episodes']}
- URLs problemáticas: {len(analysis['problematic_urls'])}
- URLs correctas: {analysis['total_episodes'] - len(analysis['problematic_urls'])}

DISTRIBUCIÓN POR DOMINIO:
"""

        for domain, count in sorted(
            analysis["domain_distribution"].items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (count / analysis["total_episodes"]) * 100
            stats += f"- {domain}: {count} ({percentage:.1f}%)\n"

        stats += "\nDISTRIBUCIÓN POR EXTENSIÓN DE ARCHIVO:\n"
        for ext, count in sorted(
            analysis["file_extension_distribution"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            percentage = (count / analysis["total_episodes"]) * 100
            stats += f"- .{ext}: {count} ({percentage:.1f}%)\n"

        if analysis["size_patterns"]:
            stats += "\nPATRONES DE DIMENSIONES EN NOMBRES:\n"
            for size, count in sorted(
                analysis["size_patterns"].items(), key=lambda x: x[1], reverse=True
            ):
                percentage = (count / analysis["total_episodes"]) * 100
                stats += f"- {size}: {count} ({percentage:.1f}%)\n"

        if analysis["problematic_urls"]:
            stats += "\nURLs PROBLEMÁTICAS DETECTADAS:\n"
            for item in analysis["problematic_urls"]:
                episode = item["episode"]
                stats += (
                    f"- Episodio #{episode['program_number']}: {episode['title']}\n"
                )
                stats += f"  URL: {item['url']}\n"
                stats += f"  Problemas: {', '.join(item['problems'])}\n\n"

        return stats

    def check_url_consistency(self, episodes: list[dict]) -> str:
        """Verifica la consistencia de las URLs con los números de episodio."""
        consistency_report = "\nVERIFICACIÓN DE CONSISTENCIA:\n"

        # Verificar que las URLs contengan el número del episodio
        inconsistent_count = 0

        for episode in episodes:
            url = episode["cover_image_url"]
            program_number = episode["program_number"]

            # Buscar el número del episodio en la URL
            number_in_url = re.search(r"(\d+)", url)
            if number_in_url:
                found_number = int(number_in_url.group(1))
                if found_number != program_number:
                    inconsistent_count += 1
                    consistency_report += f"- Episodio #{program_number}: URL contiene número {found_number}\n"
                    consistency_report += f"  URL: {url}\n"

        consistency_report += f"\nTotal inconsistencias: {inconsistent_count}\n"

        return consistency_report

    def generate_comprehensive_report(self) -> str:
        """Genera un reporte completo de verificación."""
        episodes = self.get_episodes_with_cover_images()

        if not episodes:
            return "No hay episodios con imágenes de portada para verificar."

        report = self.generate_url_statistics(episodes)
        report += self.check_url_consistency(episodes)

        # Resumen final
        analysis = self.analyze_url_patterns(episodes)
        report += f"""
RESUMEN FINAL:
- Total episodios verificados: {analysis['total_episodes']}
- URLs problemáticas: {len(analysis['problematic_urls'])}
- URLs correctas: {analysis['total_episodes'] - len(analysis['problematic_urls'])}
- Tasa de URLs correctas: {((analysis['total_episodes'] - len(analysis['problematic_urls'])) / analysis['total_episodes'] * 100):.1f}%
"""

        return report


def main():
    """Función principal."""
    logger.info("Iniciando verificación de URLs de imágenes de portada...")

    verifier = CoverImageURLVerifier()
    report = verifier.generate_comprehensive_report()

    print(report)

    # Guardar reporte en archivo
    with open("logs/verify_cover_image_urls_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(
        "Verificación completada. Reporte guardado en logs/verify_cover_image_urls_report.txt"
    )


if __name__ == "__main__":
    main()
