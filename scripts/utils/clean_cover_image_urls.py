#!/usr/bin/env python3
"""
Script para limpiar las URLs de las imágenes de portada en la base de datos.
Elimina parámetros de query como ?w=81&h=100 de las URLs.
"""

import logging
import os
import sys
from urllib.parse import urlparse, urlunparse

# Añadir el directorio raíz al path para importar los servicios
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.config import is_supabase_enabled
from services.supabase_database import SupabaseDatabase

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/clean_cover_image_urls.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CoverImageURLCleaner:
    def __init__(self):
        if not is_supabase_enabled():
            raise ValueError("Este script requiere Supabase como base de datos")
        self.db = SupabaseDatabase()

    def clean_image_url(self, url: str) -> str:
        """
        Limpia una URL de imagen eliminando parámetros de query.
        Ejemplo: https://example.com/image.jpg?w=81&h=100 -> https://example.com/image.jpg
        """
        if not url:
            return url

        try:
            # Parsear la URL
            parsed = urlparse(url)

            # Reconstruir la URL sin parámetros de query
            cleaned_url = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    "",  # query vacío
                    parsed.fragment,
                )
            )

            return cleaned_url
        except Exception as e:
            logger.error(f"Error limpiando URL {url}: {e}")
            return url

    def get_episodes_with_cover_images(self) -> list[dict]:
        """Obtiene todos los episodios que tienen cover_image_url."""
        try:
            response = (
                self.db.client.table("podcasts")
                .select("id,program_number,title,cover_image_url")
                .not_.is_("cover_image_url", "null")
                .neq("cover_image_url", "")
                .order("program_number")
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error obteniendo episodios con cover: {e}")
            return []

    def needs_cleaning(self, url: str) -> bool:
        """Verifica si una URL necesita ser limpiada (tiene parámetros de query)."""
        if not url:
            return False
        return "?" in url

    def update_episode_cover_url(self, episode_id: int, cleaned_url: str) -> bool:
        """Actualiza la URL de la imagen de portada en la base de datos."""
        try:
            self.db.client.table("podcasts").update(
                {"cover_image_url": cleaned_url}
            ).eq("id", episode_id).execute()
            logger.info(
                f"Actualizado episodio {episode_id} con URL limpia: {cleaned_url}"
            )
            return True
        except Exception as e:
            logger.error(f"Error actualizando episodio {episode_id}: {e}")
            return False

    def process_episodes(self) -> tuple[int, int, list[dict]]:
        """
        Procesa todos los episodios con imágenes de portada y limpia las URLs.
        Retorna: (total_procesados, actualizados, errores)
        """
        episodes = self.get_episodes_with_cover_images()

        total_episodes = len(episodes)
        logger.info(f"Total episodios con imágenes de portada: {total_episodes}")

        if total_episodes == 0:
            logger.info("No hay episodios con imágenes de portada.")
            return 0, 0, []

        updated_count = 0
        errors = []
        urls_that_needed_cleaning = []

        for episode in episodes:
            episode_id = episode["id"]
            program_number = episode["program_number"]
            title = episode["title"]
            original_url = episode["cover_image_url"]

            logger.info(f"Procesando episodio #{program_number}: {title}")
            logger.info(f"URL original: {original_url}")

            if self.needs_cleaning(original_url):
                cleaned_url = self.clean_image_url(original_url)
                logger.info(f"URL limpia: {cleaned_url}")

                if cleaned_url != original_url:
                    urls_that_needed_cleaning.append(
                        {
                            "episode": episode,
                            "original": original_url,
                            "cleaned": cleaned_url,
                        }
                    )

                    success = self.update_episode_cover_url(episode_id, cleaned_url)
                    if success:
                        updated_count += 1
                    else:
                        errors.append(
                            {
                                "episode": episode,
                                "error": "Error al actualizar en BD",
                                "original": original_url,
                                "cleaned": cleaned_url,
                            }
                        )
                else:
                    logger.info("URL no cambió después de la limpieza")
            else:
                logger.info("URL no necesita limpieza")

        logger.info(f"URLs que necesitaban limpieza: {len(urls_that_needed_cleaning)}")
        logger.info(f"Episodios actualizados: {updated_count}")
        logger.info(f"Errores: {len(errors)}")

        return total_episodes, updated_count, errors, urls_that_needed_cleaning

    def generate_report(
        self,
        total_processed: int,
        updated: int,
        errors: list[dict],
        cleaned_urls: list[dict],
    ) -> str:
        """Genera un reporte de los resultados."""
        cleaning_rate = (
            (len(cleaned_urls) / total_processed * 100) if total_processed > 0 else 0
        )
        report = f"""
=== REPORTE DE LIMPIEZA DE URLs DE IMÁGENES DE PORTADA ===

RESUMEN:
- Episodios procesados: {total_processed}
- URLs actualizadas: {updated}
- Errores: {len(errors)}
- URLs que necesitaban limpieza: {len(cleaned_urls)}
- Tasa de limpieza: {cleaning_rate:.1f}%

ESTADÍSTICAS ACTUALES:
"""

        # Obtener estadísticas actuales
        episodes_with_cover = self.get_episodes_with_cover_images()
        total_with_cover = len(episodes_with_cover)

        # Contar URLs que aún tienen parámetros
        urls_with_params = 0
        for episode in episodes_with_cover:
            if self.needs_cleaning(episode["cover_image_url"]):
                urls_with_params += 1

        report += f"""
- Total episodios con imágenes de portada: {total_with_cover}
- URLs con parámetros restantes: {urls_with_params}
- URLs limpias: {total_with_cover - urls_with_params}
"""

        if cleaned_urls:
            report += "\nURLs LIMPIADAS:\n"
            for item in cleaned_urls:
                episode = item["episode"]
                report += (
                    f"- Episodio #{episode['program_number']}: {episode['title']}\n"
                )
                report += f"  Original: {item['original']}\n"
                report += f"  Limpia:   {item['cleaned']}\n\n"

        if errors:
            report += "\nERRORES DETALLADOS:\n"
            for error in errors:
                episode = error["episode"]
                report += (
                    f"- Episodio #{episode['program_number']}: {episode['title']}\n"
                )
                report += f"  Error: {error['error']}\n"
                report += f"  Original: {error['original']}\n"
                report += f"  Limpia: {error['cleaned']}\n\n"

        return report


def main():
    """Función principal."""
    logger.info("Iniciando limpieza de URLs de imágenes de portada...")

    cleaner = CoverImageURLCleaner()
    total_processed, updated, errors, cleaned_urls = cleaner.process_episodes()

    # Generar reporte
    report = cleaner.generate_report(total_processed, updated, errors, cleaned_urls)
    print(report)

    # Guardar reporte en archivo
    with open("logs/clean_cover_image_urls_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(
        "Limpieza completada. Reporte guardado en logs/clean_cover_image_urls_report.txt"
    )


if __name__ == "__main__":
    main()
