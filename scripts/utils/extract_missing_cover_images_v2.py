#!/usr/bin/env python3
"""
Script mejorado para extraer imágenes de portada faltantes de las URLs de WordPress.
Versión 2.0 que maneja casos especiales y URLs alternativas.
"""

import asyncio
import logging
import os
import re
import sys

import aiohttp
from bs4 import BeautifulSoup

# Añadir el directorio raíz al path para importar los servicios
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.config import is_supabase_enabled
from services.supabase_database import SupabaseDatabase

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/cover_image_extraction_v2.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CoverImageExtractorV2:
    def __init__(self):
        if not is_supabase_enabled():
            raise ValueError("Este script requiere Supabase como base de datos")
        self.db = SupabaseDatabase()
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get_episodes_without_cover(self) -> list[dict]:
        """Obtiene episodios que no tienen cover_image_url."""
        try:
            response = (
                self.db.client.table("podcasts")
                .select("id,program_number,title,wordpress_url,cover_image_url")
                .is_("cover_image_url", "null")
                .not_.is_("wordpress_url", "null")
                .neq("wordpress_url", "")
                .order("program_number")
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error obteniendo episodios sin cover: {e}")
            return []

    def get_episodes_with_cover(self) -> list[dict]:
        """Obtiene episodios que sí tienen cover_image_url para estadísticas."""
        try:
            response = (
                self.db.client.table("podcasts")
                .select("id,program_number,title,wordpress_url,cover_image_url")
                .not_.is_("cover_image_url", "null")
                .neq("cover_image_url", "")
                .order("program_number")
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error obteniendo episodios con cover: {e}")
            return []

    def generate_alternative_urls(
        self, wordpress_url: str, program_number: int
    ) -> list[str]:
        """Genera URLs alternativas para buscar imágenes de portada."""
        urls = []

        # URL original
        urls.append(wordpress_url)

        # Patrones alternativos para Popcasting

        # Añadir patrones específicos para episodios antiguos (0-91)
        if program_number <= 91:
            urls.extend(
                [
                    "https://popcastingpop.com/archivo-popcasting/",
                    "https://popcastingpop.com/archivo-popcasting-21-40/",
                    "https://popcastingpop.com/archivo-popcasting-42-62/",
                    "https://popcastingpop.com/programas-anteriores-64-91/",
                ]
            )

        # Añadir patrones específicos para episodios 65-68
        if 65 <= program_number <= 68:
            urls.extend(
                [
                    "https://popcastingpop.com/programas-anteriores-64-91/",
                ]
            )

        # Añadir patrones específicos para episodio 82
        if program_number == 82:
            urls.extend(
                [
                    "https://popcastingpop.com/2025/07/18/popcasting-082/",
                    "https://popcastingpop.com/2025/07/18/episodio-082/",
                ]
            )

        return list(set(urls))  # Eliminar duplicados

    async def extract_cover_image_from_wordpress(
        self, wordpress_url: str, program_number: int
    ) -> str | None:
        """
        Extrae la URL de la imagen de portada de una página de WordPress.
        Versión mejorada que maneja casos especiales.
        """
        alternative_urls = self.generate_alternative_urls(wordpress_url, program_number)

        for url in alternative_urls:
            try:
                logger.info(f"Intentando URL: {url}")
                async with self.session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"Error HTTP {response.status} para {url}")
                        continue

                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Patrones específicos para Popcasting
                    cover_image = None

                    # 1. Buscar en meta tags (og:image, twitter:image)
                    meta_image = soup.find("meta", property="og:image")
                    if meta_image and meta_image.get("content"):
                        cover_image = meta_image["content"]

                    # 2. Buscar imágenes con clases específicas de WordPress
                    if not cover_image:
                        wp_image = soup.find("img", class_="wp-post-image")
                        if wp_image and wp_image.get("src"):
                            cover_image = wp_image["src"]

                    # 3. Buscar imágenes en el header o hero section
                    if not cover_image:
                        header_img = soup.find(
                            "img",
                            {
                                "src": re.compile(
                                    r"wp-content/uploads.*\\.(jpg|jpeg|png|gif)", re.I
                                )
                            },
                        )
                        if header_img and header_img.get("src"):
                            cover_image = header_img["src"]

                    # 4. Buscar imágenes con patrones específicos de Popcasting
                    if not cover_image:
                        popcasting_img = soup.find(
                            "img",
                            {
                                "src": re.compile(
                                    r"popcastingpop\\.com.*\\.(jpg|jpeg|png|gif)", re.I
                                )
                            },
                        )
                        if popcasting_img and popcasting_img.get("src"):
                            cover_image = popcasting_img["src"]

                    # 5. Buscar cualquier imagen que contenga el número del episodio en la URL
                    if not cover_image:
                        episode_img = soup.find(
                            "img",
                            {
                                "src": re.compile(
                                    f".*{program_number}.*\\.(jpg|jpeg|png|gif)", re.I
                                )
                            },
                        )
                        if episode_img and episode_img.get("src"):
                            cover_image = episode_img["src"]

                    # 6. Para episodios antiguos, buscar en el contenido específico
                    if not cover_image and program_number <= 91:
                        # Buscar imágenes en el contenido de episodios antiguos
                        content_img = soup.find(
                            "img",
                            {
                                "src": re.compile(
                                    r"wp-content/uploads/2009/09/.*\\.(jpg|jpeg|png|gif)",
                                    re.I,
                                )
                            },
                        )
                        if content_img and content_img.get("src"):
                            cover_image = content_img["src"]

                    # 7. Buscar cualquier imagen que parezca ser una portada
                    if not cover_image:
                        # Buscar imágenes grandes que podrían ser portadas
                        all_images = soup.find_all("img")
                        for img in all_images:
                            src = img.get("src", "")
                            if src and any(
                                ext in src.lower()
                                for ext in [".jpg", ".jpeg", ".png", ".gif"]
                            ):
                                # Verificar que no sea un avatar o icono pequeño
                                if not any(
                                    skip in src.lower()
                                    for skip in ["avatar", "icon", "gravatar", "emoji"]
                                ):
                                    if (
                                        "popcastingpop.com" in src
                                        or "wp-content" in src
                                    ):
                                        cover_image = src
                                        break

                    # Normalizar URL si se encontró
                    if cover_image:
                        if cover_image.startswith("//"):
                            cover_image = "https:" + cover_image
                        elif cover_image.startswith("/"):
                            cover_image = "https://popcastingpop.com" + cover_image

                        logger.info(f"Imagen encontrada en {url}: {cover_image}")
                        return cover_image

                    logger.warning(f"No se encontró imagen de portada en {url}")

            except Exception as e:
                logger.error(f"Error extrayendo imagen de {url}: {e}")
                continue

        logger.warning(
            f"No se encontró imagen de portada en ninguna URL para episodio #{program_number}"
        )
        return None

    async def update_episode_cover(self, episode_id: int, cover_image_url: str) -> bool:
        """Actualiza la URL de la imagen de portada en la base de datos."""
        try:
            self.db.client.table("podcasts").update(
                {"cover_image_url": cover_image_url}
            ).eq("id", episode_id).execute()
            logger.info(
                f"Actualizado episodio {episode_id} con cover: {cover_image_url}"
            )
            return True
        except Exception as e:
            logger.error(f"Error actualizando episodio {episode_id}: {e}")
            return False

    async def process_episodes(self) -> tuple[int, int, list[dict]]:
        """
        Procesa todos los episodios sin imagen de portada.
        Retorna: (total_procesados, exitosos, errores)
        """
        episodes_without_cover = self.get_episodes_without_cover()
        episodes_with_cover = self.get_episodes_with_cover()

        total_without = len(episodes_without_cover)
        total_with = len(episodes_with_cover)

        logger.info(f"Episodios sin imagen de portada: {total_without}")
        logger.info(f"Episodios con imagen de portada: {total_with}")
        logger.info(f"Total episodios: {total_without + total_with}")

        if total_without == 0:
            logger.info("No hay episodios sin imagen de portada.")
            return 0, 0, []

        successful_updates = 0
        errors = []

        for episode in episodes_without_cover:
            logger.info(
                f"Procesando episodio #{episode['program_number']}: {episode['title']}"
            )

            cover_image = await self.extract_cover_image_from_wordpress(
                episode["wordpress_url"], episode["program_number"]
            )

            if cover_image:
                success = await self.update_episode_cover(episode["id"], cover_image)
                if success:
                    successful_updates += 1
                else:
                    errors.append(
                        {
                            "episode": episode,
                            "error": "Error al actualizar en BD",
                            "cover_found": cover_image,
                        }
                    )
            else:
                errors.append(
                    {
                        "episode": episode,
                        "error": "No se encontró imagen de portada",
                        "cover_found": None,
                    }
                )

            # Pequeña pausa para no sobrecargar el servidor
            await asyncio.sleep(2)

        return total_without, successful_updates, errors

    def generate_report(
        self, total_processed: int, successful: int, errors: list[dict]
    ) -> str:
        """Genera un reporte de los resultados."""
        success_rate = (
            (successful / total_processed * 100) if total_processed > 0 else 0
        )
        report = f"""
=== REPORTE DE EXTRACCIÓN DE IMÁGENES DE PORTADA V2 ===

RESUMEN:
- Episodios procesados: {total_processed}
- Actualizaciones exitosas: {successful}
- Errores: {len(errors)}
- Tasa de éxito: {success_rate:.1f}%

ESTADÍSTICAS ACTUALES:
"""

        # Obtener estadísticas actuales
        episodes_without_cover = self.get_episodes_without_cover()
        episodes_with_cover = self.get_episodes_with_cover()

        total_without = len(episodes_without_cover)
        total_with = len(episodes_with_cover)
        total_episodes = total_without + total_with

        if total_episodes > 0:
            with_percentage = total_with / total_episodes * 100
            without_percentage = total_without / total_episodes * 100
        else:
            with_percentage = 0
            without_percentage = 0

        report += f"""
- Total episodios en BD: {total_episodes}
- Episodios con imagen de portada: {total_with} ({with_percentage:.1f}%)
- Episodios sin imagen de portada: {total_without} ({without_percentage:.1f}%)
"""

        if errors:
            report += "\nERRORES DETALLADOS:\n"
            for error in errors:
                episode = error["episode"]
                report += (
                    f"- Episodio #{episode['program_number']}: {episode['title']}\n"
                )
                report += f"  Error: {error['error']}\n"
                if error["cover_found"]:
                    report += f"  Imagen encontrada pero no guardada: {error['cover_found']}\n"
                report += "\n"

        return report


async def main():
    """Función principal."""
    logger.info("Iniciando extracción de imágenes de portada faltantes (V2)...")

    async with CoverImageExtractorV2() as extractor:
        total_processed, successful, errors = await extractor.process_episodes()

        # Generar reporte
        report = extractor.generate_report(total_processed, successful, errors)
        print(report)

        # Guardar reporte en archivo
        with open(
            "logs/cover_image_extraction_v2_report.txt", "w", encoding="utf-8"
        ) as f:
            f.write(report)

        logger.info(
            "Extracción completada. Reporte guardado en logs/cover_image_extraction_v2_report.txt"
        )


if __name__ == "__main__":
    asyncio.run(main())
