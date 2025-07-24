#!/usr/bin/env python3
"""
Script para listar las URLs actuales de los episodios específicos para revisión.
"""

import logging
import os
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
        logging.FileHandler("logs/list_current_cover_urls.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CoverURLLister:
    def __init__(self):
        if not is_supabase_enabled():
            raise ValueError("Este script requiere Supabase como base de datos")
        self.db = SupabaseDatabase()

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

    def generate_url_list(self, episodes: list[dict]) -> str:
        """Genera una lista de URLs para revisión."""
        url_list = "=== LISTA DE URLs ACTUALES DE IMÁGENES DE PORTADA ===\n\n"

        for episode in episodes:
            program_number = episode["program_number"]
            title = episode["title"]
            cover_url = episode["cover_image_url"]
            wordpress_url = episode["wordpress_url"]

            url_list += f"Episodio #{program_number}: {title}\n"
            url_list += f"URL actual: {cover_url}\n"
            url_list += f"URL WordPress: {wordpress_url}\n"

            # Identificar problemas
            problems = []
            if "gravatar.com" in cover_url or "blavatar" in cover_url:
                problems.append("URL de Gravatar")
            if "gstatic.com" in cover_url:
                problems.append("URL de Google Images")
            if "pinimg.com" in cover_url:
                problems.append("URL de Pinterest")
            if "rsssmall.jpg" in cover_url:
                problems.append("Imagen RSS pequeña")
            if "download" in cover_url.lower():
                problems.append("URL de descarga")

            if problems:
                url_list += f"Problemas detectados: {', '.join(problems)}\n"
            else:
                url_list += "Problemas detectados: Ninguno\n"

            url_list += "\n" + "-" * 80 + "\n\n"

        return url_list


def main():
    """Función principal."""
    logger.info("Generando lista de URLs actuales de episodios específicos...")

    # Episodios específicos para revisar
    specific_episodes = [192, 215, 245]

    lister = CoverURLLister()
    episodes = lister.get_specific_episodes(specific_episodes)

    if episodes:
        url_list = lister.generate_url_list(episodes)
        print(url_list)

        # Guardar lista en archivo
        with open("logs/current_cover_urls_list.txt", "w", encoding="utf-8") as f:
            f.write(url_list)

        logger.info("Lista generada. Revisa logs/current_cover_urls_list.txt")
    else:
        logger.warning("No se encontraron episodios para listar")


if __name__ == "__main__":
    main()
