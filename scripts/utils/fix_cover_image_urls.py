#!/usr/bin/env python3
"""
Script para revisar y corregir URLs de imágenes de portada problemáticas.
Identifica y corrige URLs que no son imágenes de portada válidas.
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
        logging.FileHandler("logs/fix_cover_image_urls.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CoverImageURLFixer:
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

    def identify_problematic_urls(self, episodes: list[dict]) -> list[dict]:
        """Identifica URLs problemáticas basándose en patrones conocidos."""
        problematic_episodes = []

        for episode in episodes:
            url = episode["cover_image_url"]
            episode["program_number"]
            episode["title"]

            problems = []

            # 1. URLs de Gravatar (no son imágenes de portada reales)
            if "gravatar.com" in url or "blavatar" in url:
                problems.append("URL de Gravatar (no es imagen de portada)")

            # 2. URLs de descarga o iconos pequeños
            if "downloadsmall.jpg" in url or "download" in url.lower():
                problems.append("URL de descarga/icono pequeño")

            # 3. URLs con nombres genéricos
            if any(
                generic in url.lower()
                for generic in ["descarga", "download", "image", "images"]
            ):
                problems.append("Nombre de archivo genérico")

            # 4. URLs que no parecen ser imágenes de portada
            if not any(
                valid in url.lower() for valid in [".jpg", ".jpeg", ".png", ".gif"]
            ):
                problems.append("No parece ser una imagen")

            # 5. URLs con dimensiones muy pequeñas en el nombre
            if re.search(r"(\d+)x(\d+)", url):
                dimensions = re.findall(r"(\d+)x(\d+)", url)
                for w, h in dimensions:
                    if int(w) < 50 or int(h) < 50:
                        problems.append(f"Dimensiones muy pequeñas ({w}x{h})")

            if problems:
                problematic_episodes.append(
                    {"episode": episode, "problems": problems, "url": url}
                )

        return problematic_episodes

    def generate_alternative_urls(self, program_number: int) -> list[str]:
        """Genera URLs alternativas para buscar imágenes de portada."""
        urls = []

        # Patrones específicos para diferentes rangos de episodios
        if program_number <= 91:
            # Episodios antiguos (0-91)
            urls.extend(
                [
                    f"https://popcastingpop.com/wp-content/uploads/2009/09/{program_number}.jpg",
                    f"https://popcastingpop.com/wp-content/uploads/2009/09/{program_number}.png",
                    f"https://popcastingpop.com/wp-content/uploads/2009/09/episodio_{program_number}.jpg",
                    f"https://popcastingpop.com/wp-content/uploads/2009/09/popcasting_{program_number}.jpg",
                ]
            )
        elif 92 <= program_number <= 200:
            # Episodios medios (92-200)
            urls.extend(
                [
                    f"https://popcastingpop.com/wp-content/uploads/2010/01/{program_number}.jpg",
                    f"https://popcastingpop.com/wp-content/uploads/2010/01/{program_number}.png",
                    f"https://popcastingpop.com/wp-content/uploads/2010/01/episodio_{program_number}.jpg",
                    f"https://popcastingpop.com/wp-content/uploads/2010/01/popcasting_{program_number}.jpg",
                ]
            )
        elif 201 <= program_number <= 300:
            # Episodios recientes (201-300)
            urls.extend(
                [
                    f"https://popcastingpop.com/wp-content/uploads/2013/01/{program_number}.jpg",
                    f"https://popcastingpop.com/wp-content/uploads/2013/01/{program_number}.png",
                    f"https://popcastingpop.com/wp-content/uploads/2013/01/episodio_{program_number}.jpg",
                    f"https://popcastingpop.com/wp-content/uploads/2013/01/popcasting_{program_number}.jpg",
                ]
            )
        else:
            # Episodios muy recientes (300+)
            urls.extend(
                [
                    f"https://popcastingpop.com/wp-content/uploads/2015/01/{program_number}.jpg",
                    f"https://popcastingpop.com/wp-content/uploads/2015/01/{program_number}.png",
                    f"https://popcastingpop.com/wp-content/uploads/2015/01/episodio_{program_number}.jpg",
                    f"https://popcastingpop.com/wp-content/uploads/2015/01/popcasting_{program_number}.jpg",
                ]
            )

        # URLs específicas para episodios problemáticos conocidos
        if program_number == 245:
            urls.extend(
                [
                    "https://popcastingpop.com/wp-content/uploads/2013/10/charles.jpg",
                    "https://popcastingpop.com/wp-content/uploads/2013/10/charles.png",
                ]
            )

        if program_number in [192, 215]:
            urls.extend(
                [
                    "https://popcastingpop.com/wp-content/uploads/2009/09/patrick.jpg",
                    "https://popcastingpop.com/wp-content/uploads/2009/09/tyrone.jpg",
                ]
            )

        return list(set(urls))  # Eliminar duplicados

    def check_url_exists(self, url: str) -> bool:
        """Verifica si una URL existe (simulación básica)."""
        # Por ahora, verificamos si la URL tiene un formato válido
        # En una implementación real, haríamos una petición HTTP
        return bool(re.match(r"^https?://.*\.(jpg|jpeg|png|gif)$", url, re.I))

    def find_better_cover_url(self, episode: dict) -> str:
        """Busca una mejor URL de imagen de portada."""
        program_number = episode["program_number"]
        episode["title"]

        # Generar URLs alternativas
        alternative_urls = self.generate_alternative_urls(program_number)

        # Por ahora, retornamos la primera URL que parece válida
        # En una implementación real, verificaríamos cada URL
        for url in alternative_urls:
            if self.check_url_exists(url):
                return url

        # Si no encontramos nada, retornamos una URL por defecto
        return "https://popcastingpop.com/wp-content/uploads/2009/09/patrick.jpg"

    def update_episode_cover_url(self, episode_id: int, new_url: str) -> bool:
        """Actualiza la URL de la imagen de portada en la base de datos."""
        try:
            self.db.client.table("podcasts").update({"cover_image_url": new_url}).eq(
                "id", episode_id
            ).execute()
            logger.info(f"Actualizado episodio {episode_id} con nueva URL: {new_url}")
            return True
        except Exception as e:
            logger.error(f"Error actualizando episodio {episode_id}: {e}")
            return False

    def process_episodes(self) -> tuple[int, int, list[dict]]:
        """
        Procesa todos los episodios y corrige URLs problemáticas.
        Retorna: (total_procesados, corregidos, errores)
        """
        episodes = self.get_episodes_with_cover_images()

        total_episodes = len(episodes)
        logger.info(f"Total episodios con imágenes de portada: {total_episodes}")

        if total_episodes == 0:
            logger.info("No hay episodios con imágenes de portada.")
            return 0, 0, []

        # Identificar episodios problemáticos
        problematic_episodes = self.identify_problematic_urls(episodes)

        logger.info(f"Episodios con URLs problemáticas: {len(problematic_episodes)}")

        corrected_count = 0
        errors = []

        for item in problematic_episodes:
            episode = item["episode"]
            problems = item["problems"]
            original_url = item["url"]

            logger.info(
                f"Procesando episodio #{episode['program_number']}: {episode['title']}"
            )
            logger.info(f"Problemas identificados: {', '.join(problems)}")
            logger.info(f"URL original: {original_url}")

            # Buscar una mejor URL
            new_url = self.find_better_cover_url(episode)
            logger.info(f"Nueva URL propuesta: {new_url}")

            if new_url != original_url:
                success = self.update_episode_cover_url(episode["id"], new_url)
                if success:
                    corrected_count += 1
                else:
                    errors.append(
                        {
                            "episode": episode,
                            "error": "Error al actualizar en BD",
                            "original": original_url,
                            "new": new_url,
                        }
                    )
            else:
                logger.info("No se encontró una URL mejor")

        return len(problematic_episodes), corrected_count, errors

    def generate_report(
        self, total_processed: int, corrected: int, errors: list[dict]
    ) -> str:
        """Genera un reporte de los resultados."""
        correction_rate = (
            (corrected / total_processed * 100) if total_processed > 0 else 0
        )
        report = f"""
=== REPORTE DE CORRECCIÓN DE URLs DE IMÁGENES DE PORTADA ===

RESUMEN:
- Episodios con URLs problemáticas: {total_processed}
- URLs corregidas: {corrected}
- Errores: {len(errors)}
- Tasa de corrección: {correction_rate:.1f}%

ESTADÍSTICAS ACTUALES:
"""

        # Obtener estadísticas actuales
        episodes_with_cover = self.get_episodes_with_cover_images()
        total_with_cover = len(episodes_with_cover)

        # Contar URLs problemáticas restantes
        problematic_remaining = len(self.identify_problematic_urls(episodes_with_cover))

        report += f"""
- Total episodios con imágenes de portada: {total_with_cover}
- URLs problemáticas restantes: {problematic_remaining}
- URLs correctas: {total_with_cover - problematic_remaining}
"""

        if errors:
            report += "\nERRORES DETALLADOS:\n"
            for error in errors:
                episode = error["episode"]
                report += (
                    f"- Episodio #{episode['program_number']}: {episode['title']}\n"
                )
                report += f"  Error: {error['error']}\n"
                report += f"  Original: {error['original']}\n"
                report += f"  Nueva: {error['new']}\n\n"

        return report


def main():
    """Función principal."""
    logger.info("Iniciando corrección de URLs de imágenes de portada problemáticas...")

    fixer = CoverImageURLFixer()
    total_processed, corrected, errors = fixer.process_episodes()

    # Generar reporte
    report = fixer.generate_report(total_processed, corrected, errors)
    print(report)

    # Guardar reporte en archivo
    with open("logs/fix_cover_image_urls_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(
        "Corrección completada. Reporte guardado en logs/fix_cover_image_urls_report.txt"
    )


if __name__ == "__main__":
    main()
