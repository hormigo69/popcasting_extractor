#!/usr/bin/env python3
"""
Script mejorado para hacer scraping de imágenes de portada reales de Popcasting.
Busca más específicamente en el contenido de las páginas de WordPress.
"""

import asyncio
import logging
import os
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
        logging.FileHandler("logs/scrape_improved_cover_images.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ImprovedCoverImageScraper:
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

    def get_specific_episodes(self, episode_numbers: list[int]) -> list[dict]:
        """Obtiene episodios específicos por número."""
        try:
            episodes = []
            for number in episode_numbers:
                response = (
                    self.db.client.table("podcasts")
                    .select("id,program_number,title,cover_image_url,wordpress_url")
                    .eq("program_number", number)
                    .execute()
                )

                if response.data:
                    episodes.append(response.data[0])
                else:
                    logger.warning(
                        f"Episodio #{number} no encontrado en la base de datos"
                    )

            return episodes
        except Exception as e:
            logger.error(f"Error obteniendo episodios específicos: {e}")
            return []

    async def scrape_cover_image_from_wordpress(
        self, wordpress_url: str, program_number: int
    ) -> str | None:
        """Hace scraping mejorado de la página de WordPress para encontrar la imagen de portada."""
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

                # Estrategias mejoradas para encontrar la imagen de portada
                cover_image = None

                # 1. Buscar imagen con clase wp-post-image (más específica)
                wp_image = soup.find("img", class_="wp-post-image")
                if wp_image and wp_image.get("src"):
                    cover_image = wp_image["src"]
                    logger.info(
                        f"Episodio #{program_number}: Encontrada en wp-post-image"
                    )

                # 2. Buscar en el contenido principal del post
                if not cover_image:
                    content_area = (
                        soup.find("div", class_="entry-content")
                        or soup.find("article")
                        or soup.find("main")
                    )
                    if content_area:
                        # Buscar la primera imagen grande en el contenido
                        content_images = content_area.find_all("img")
                        for img in content_images:
                            src = img.get("src", "")
                            if src and "popcastingpop.com" in src:
                                # Evitar imágenes pequeñas o iconos
                                if not any(
                                    small in src.lower()
                                    for small in [
                                        "icon",
                                        "thumb",
                                        "small",
                                        "download",
                                        "avatar",
                                    ]
                                ):
                                    cover_image = src
                                    logger.info(
                                        f"Episodio #{program_number}: Encontrada en contenido principal"
                                    )
                                    break

                # 3. Buscar en el header o hero section
                if not cover_image:
                    header_selectors = [
                        "header img",
                        ".hero img",
                        ".featured-image img",
                        ".post-thumbnail img",
                        ".entry-header img",
                    ]

                    for selector in header_selectors:
                        header_img = soup.select_one(selector)
                        if header_img and header_img.get("src"):
                            src = header_img["src"]
                            if "popcastingpop.com" in src:
                                cover_image = src
                                logger.info(
                                    f"Episodio #{program_number}: Encontrada en header ({selector})"
                                )
                                break

                # 4. Buscar imágenes específicas de Popcasting con patrones conocidos
                if not cover_image:
                    all_images = soup.find_all("img")
                    popcasting_images = []

                    for img in all_images:
                        src = img.get("src", "")
                        if src and "popcastingpop.com" in src:
                            # Filtrar por patrones específicos de Popcasting
                            if any(
                                pattern in src.lower()
                                for pattern in ["/uploads/", "wp-content", "popcasting"]
                            ):
                                # Evitar imágenes problemáticas
                                if not any(
                                    bad in src.lower()
                                    for bad in [
                                        "gravatar",
                                        "blavatar",
                                        "gstatic",
                                        "pinimg",
                                        "download",
                                        "icon",
                                    ]
                                ):
                                    popcasting_images.append(src)

                    if popcasting_images:
                        # Tomar la imagen más grande o la primera válida
                        cover_image = popcasting_images[0]
                        logger.info(
                            f"Episodio #{program_number}: Encontrada imagen de Popcasting"
                        )

                # 5. Buscar en meta tags solo si no encontramos nada mejor
                if not cover_image:
                    meta_image = soup.find("meta", property="og:image")
                    if meta_image and meta_image.get("content"):
                        content = meta_image["content"]
                        # Solo usar meta tags si son de Popcasting
                        if "popcastingpop.com" in content and not any(
                            bad in content.lower()
                            for bad in ["gravatar", "blavatar", "gstatic", "pinimg"]
                        ):
                            cover_image = content
                            logger.info(
                                f"Episodio #{program_number}: Encontrada en og:image (Popcasting)"
                            )

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
                        f"Episodio #{program_number}: No se encontró imagen de portada válida"
                    )
                    return None

        except Exception as e:
            logger.error(f"Episodio #{program_number}: Error en scraping: {e}")
            return None

    async def process_specific_episodes(self, episode_numbers: list[int]) -> list[dict]:
        """Procesa episodios específicos y obtiene las URLs reales."""
        episodes = self.get_specific_episodes(episode_numbers)

        logger.info(f"Encontrados {len(episodes)} episodios específicos")

        results = []

        for episode in episodes:
            program_number = episode["program_number"]
            wordpress_url = episode["wordpress_url"]
            current_url = episode["cover_image_url"]

            logger.info(f"Procesando episodio #{program_number}: {episode['title']}")
            logger.info(f"URL actual: {current_url}")

            # Hacer scraping de la página real
            real_url = await self.scrape_cover_image_from_wordpress(
                wordpress_url, program_number
            )

            results.append(
                {"episode": episode, "current_url": current_url, "real_url": real_url}
            )

            # Pausa para no sobrecargar el servidor
            await asyncio.sleep(2)

        return results

    def generate_correction_list(self, results: list[dict]) -> str:
        """Genera una lista de correcciones para revisar manualmente."""
        correction_list = (
            "=== LISTA DE CORRECCIONES MEJORADAS DE URLs DE IMÁGENES ===\n\n"
        )

        for result in results:
            episode = result["episode"]
            program_number = episode["program_number"]
            title = episode["title"]
            current_url = result["current_url"]
            real_url = result["real_url"]

            correction_list += f"Episodio #{program_number}: {title}\n"
            correction_list += f"URL actual: {current_url}\n"

            if real_url:
                correction_list += f"URL real encontrada: {real_url}\n"
                if real_url != current_url:
                    correction_list += "¿Actualizar? SÍ (URLs diferentes)\n"
                else:
                    correction_list += "¿Actualizar? NO (URLs iguales)\n"
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


async def main():
    """Función principal."""
    logger.info("Iniciando scraping mejorado de episodios específicos...")

    # Episodios específicos mencionados por el usuario
    specific_episodes = [245, 192, 215]

    async with ImprovedCoverImageScraper() as scraper:
        # Obtener URLs reales
        results = await scraper.process_specific_episodes(specific_episodes)

        # Generar lista de correcciones
        correction_list = scraper.generate_correction_list(results)
        print(correction_list)

        # Guardar lista de correcciones
        with open(
            "logs/improved_cover_image_corrections.txt", "w", encoding="utf-8"
        ) as f:
            f.write(correction_list)

        # Mostrar resumen
        found_urls = sum(1 for r in results if r["real_url"])
        different_urls = sum(
            1 for r in results if r["real_url"] and r["real_url"] != r["current_url"]
        )

        logger.info(f"URLs reales encontradas: {found_urls}/{len(results)}")
        logger.info(f"URLs diferentes: {different_urls}/{len(results)}")

        # Aplicar correcciones automáticamente si hay diferencias
        if different_urls > 0:
            print(
                f"\nSe encontraron {different_urls} URLs diferentes. Aplicando correcciones..."
            )

            for result in results:
                if result["real_url"] and result["real_url"] != result["current_url"]:
                    episode = result["episode"]
                    success = await scraper.update_episode_cover_url(
                        episode["id"], result["real_url"]
                    )
                    if success:
                        print(f"✅ Episodio #{episode['program_number']}: Actualizado")
                    else:
                        print(
                            f"❌ Episodio #{episode['program_number']}: Error al actualizar"
                        )
        else:
            print("\nNo se encontraron URLs diferentes. No se aplicaron correcciones.")


if __name__ == "__main__":
    asyncio.run(main())
