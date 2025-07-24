#!/usr/bin/env python3
"""
Script para hacer scraping real de las páginas de WordPress y obtener las URLs correctas
de las imágenes de portada de los episodios problemáticos.
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
        logging.FileHandler("logs/scrape_real_cover_images.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RealCoverImageScraper:
    def __init__(self):
        if not is_supabase_enabled():
            raise ValueError("Este script requiere Supabase como base de datos")
        self.db = SupabaseDatabase()
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def get_problematic_episodes(self) -> list[dict]:
        """Obtiene episodios con URLs problemáticas conocidas."""
        try:
            response = (
                self.db.client.table("podcasts")
                .select("id,program_number,title,cover_image_url,wordpress_url")
                .not_.is_("cover_image_url", "null")
                .neq("cover_image_url", "")
                .order("program_number")
                .execute()
            )

            episodes = response.data
            problematic = []

            for episode in episodes:
                url = episode["cover_image_url"]
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

                # URLs que no parecen ser imágenes de portada
                if not re.search(r"\.(jpg|jpeg|png|gif)(?:\?|$)", url, re.I):
                    problems.append("Sin extensión de imagen")

                if problems:
                    problematic.append(
                        {"episode": episode, "problems": problems, "current_url": url}
                    )

            return problematic
        except Exception as e:
            logger.error(f"Error obteniendo episodios problemáticos: {e}")
            return []

    async def scrape_cover_image_from_wordpress(
        self, wordpress_url: str, program_number: int
    ) -> str | None:
        """Hace scraping real de la página de WordPress para encontrar la imagen de portada."""
        if not wordpress_url:
            logger.warning(f"Episodio #{program_number}: No hay URL de WordPress")
            return None

        try:
            logger.info(f"Scraping episodio #{program_number}: {wordpress_url}")

            async with self.session.get(wordpress_url, timeout=30) as response:
                if response.status != 200:
                    logger.error(
                        f"Episodio #{program_number}: Error HTTP {response.status}"
                    )
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                # Estrategias para encontrar la imagen de portada
                cover_image = None

                # 1. Buscar en meta tags (og:image, twitter:image)
                meta_image = soup.find("meta", property="og:image")
                if meta_image and meta_image.get("content"):
                    cover_image = meta_image["content"]
                    logger.info(f"Episodio #{program_number}: Encontrada en og:image")

                if not cover_image:
                    meta_image = soup.find("meta", attrs={"name": "twitter:image"})
                    if meta_image and meta_image.get("content"):
                        cover_image = meta_image["content"]
                        logger.info(
                            f"Episodio #{program_number}: Encontrada en twitter:image"
                        )

                # 2. Buscar imagen con clase wp-post-image
                if not cover_image:
                    wp_image = soup.find("img", class_="wp-post-image")
                    if wp_image and wp_image.get("src"):
                        cover_image = wp_image["src"]
                        logger.info(
                            f"Episodio #{program_number}: Encontrada en wp-post-image"
                        )

                # 3. Buscar imagen en el header o hero section
                if not cover_image:
                    header_image = soup.find(
                        "img", class_=re.compile(r"header|hero|featured")
                    )
                    if header_image and header_image.get("src"):
                        cover_image = header_image["src"]
                        logger.info(
                            f"Episodio #{program_number}: Encontrada en header/hero"
                        )

                # 4. Buscar imagen grande en el contenido principal
                if not cover_image:
                    content_images = soup.find_all("img")
                    largest_image = None
                    max_size = 0

                    for img in content_images:
                        src = img.get("src", "")
                        if src and "popcastingpop.com" in src:
                            # Buscar dimensiones en el nombre o atributos
                            width = img.get("width", 0)
                            height = img.get("height", 0)

                            if width and height:
                                size = int(width) * int(height)
                                if size > max_size:
                                    max_size = size
                                    largest_image = src
                            else:
                                # Si no hay dimensiones, verificar si es una imagen grande por el nombre
                                if any(
                                    size in src.lower()
                                    for size in ["large", "full", "original"]
                                ):
                                    largest_image = src
                                    break

                    if largest_image:
                        cover_image = largest_image
                        logger.info(
                            f"Episodio #{program_number}: Encontrada imagen grande en contenido"
                        )

                # 5. Buscar imagen específica de Popcasting
                if not cover_image:
                    popcasting_images = soup.find_all(
                        "img",
                        src=re.compile(r"popcastingpop\.com.*\.(jpg|jpeg|png|gif)"),
                    )
                    if popcasting_images:
                        # Tomar la primera imagen que no sea un icono pequeño
                        for img in popcasting_images:
                            src = img.get("src", "")
                            if src and not any(
                                small in src.lower()
                                for small in ["icon", "thumb", "small", "download"]
                            ):
                                cover_image = src
                                logger.info(
                                    f"Episodio #{program_number}: Encontrada imagen de Popcasting"
                                )
                                break

                if cover_image:
                    # Asegurar que la URL sea absoluta
                    if cover_image.startswith("//"):
                        cover_image = "https:" + cover_image
                    elif cover_image.startswith("/"):
                        cover_image = "https://popcastingpop.com" + cover_image

                    logger.info(
                        f"Episodio #{program_number}: URL encontrada: {cover_image}"
                    )
                    return cover_image
                else:
                    logger.warning(
                        f"Episodio #{program_number}: No se encontró imagen de portada"
                    )
                    return None

        except Exception as e:
            logger.error(f"Episodio #{program_number}: Error en scraping: {e}")
            return None

    async def process_episodes(self) -> list[dict]:
        """Procesa todos los episodios problemáticos y obtiene las URLs reales."""
        problematic_episodes = self.get_problematic_episodes()

        logger.info(f"Encontrados {len(problematic_episodes)} episodios problemáticos")

        results = []

        for item in problematic_episodes:
            episode = item["episode"]
            program_number = episode["program_number"]
            wordpress_url = episode["wordpress_url"]
            current_url = item["current_url"]

            logger.info(f"Procesando episodio #{program_number}: {episode['title']}")
            logger.info(f"Problemas: {', '.join(item['problems'])}")
            logger.info(f"URL actual: {current_url}")

            # Hacer scraping de la página real
            real_url = await self.scrape_cover_image_from_wordpress(
                wordpress_url, program_number
            )

            results.append(
                {
                    "episode": episode,
                    "current_url": current_url,
                    "real_url": real_url,
                    "problems": item["problems"],
                }
            )

            # Pausa para no sobrecargar el servidor
            await asyncio.sleep(2)

        return results

    def generate_correction_list(self, results: list[dict]) -> str:
        """Genera una lista de correcciones para revisar manualmente."""
        correction_list = "=== LISTA DE CORRECCIONES DE URLs DE IMÁGENES ===\n\n"

        for result in results:
            episode = result["episode"]
            program_number = episode["program_number"]
            title = episode["title"]
            current_url = result["current_url"]
            real_url = result["real_url"]
            problems = result["problems"]

            correction_list += f"Episodio #{program_number}: {title}\n"
            correction_list += f"Problemas: {', '.join(problems)}\n"
            correction_list += f"URL actual: {current_url}\n"

            if real_url:
                correction_list += f"URL real encontrada: {real_url}\n"
                correction_list += "¿Actualizar? SÍ\n"
            else:
                correction_list += "URL real encontrada: NO ENCONTRADA\n"
                correction_list += "¿Actualizar? NO\n"

            correction_list += "\n" + "-" * 80 + "\n\n"

        return correction_list

    async def update_episode_cover_url(self, episode_id: int, new_url: str) -> bool:
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

    async def apply_corrections(self, results: list[dict]) -> dict:
        """Aplica las correcciones a la base de datos."""
        applied = 0
        errors = 0

        for result in results:
            episode = result["episode"]
            real_url = result["real_url"]

            if real_url:
                success = await self.update_episode_cover_url(episode["id"], real_url)
                if success:
                    applied += 1
                else:
                    errors += 1

        return {"applied": applied, "errors": errors, "total": len(results)}


async def main():
    """Función principal."""
    logger.info("Iniciando scraping real de imágenes de portada...")

    async with RealCoverImageScraper() as scraper:
        # Obtener URLs reales
        results = await scraper.process_episodes()

        # Generar lista de correcciones
        correction_list = scraper.generate_correction_list(results)
        print(correction_list)

        # Guardar lista de correcciones
        with open("logs/real_cover_image_corrections.txt", "w", encoding="utf-8") as f:
            f.write(correction_list)

        # Preguntar si aplicar correcciones
        print(f"\nSe encontraron {len(results)} episodios problemáticos.")
        print("¿Deseas aplicar las correcciones automáticamente? (s/n): ", end="")

        # Por ahora, no aplicamos automáticamente para revisar primero
        logger.info(
            "Correcciones no aplicadas automáticamente. Revisa logs/real_cover_image_corrections.txt"
        )

        # Mostrar resumen
        found_urls = sum(1 for r in results if r["real_url"])
        logger.info(f"URLs reales encontradas: {found_urls}/{len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
