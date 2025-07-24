#!/usr/bin/env python3
"""
Script para corregir URLs específicas de episodios con las URLs correctas proporcionadas por el usuario.
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
        logging.FileHandler("logs/fix_specific_episode_urls.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SpecificEpisodeURLFixer:
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

    def get_correct_urls(self) -> dict[int, str]:
        """Define las URLs correctas para episodios específicos."""
        return {
            245: "https://popcastingpop.com/wp-content/uploads/2015/09/img_2868.jpg",
            # Para los episodios 192 y 215, necesitamos encontrar las URLs correctas
            # Por ahora, las dejamos vacías para que el usuario las proporcione
        }

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

    def process_episodes(self) -> list[dict]:
        """Procesa los episodios específicos y aplica las correcciones."""
        correct_urls = self.get_correct_urls()
        episode_numbers = list(correct_urls.keys())

        episodes = self.get_specific_episodes(episode_numbers)
        logger.info(f"Encontrados {len(episodes)} episodios específicos")

        results = []

        for episode in episodes:
            program_number = episode["program_number"]
            current_url = episode["cover_image_url"]
            correct_url = correct_urls.get(program_number)

            logger.info(f"Procesando episodio #{program_number}: {episode['title']}")
            logger.info(f"URL actual: {current_url}")
            logger.info(f"URL correcta: {correct_url}")

            if correct_url and correct_url != current_url:
                success = self.update_episode_cover_url(episode["id"], correct_url)
                results.append(
                    {
                        "episode": episode,
                        "current_url": current_url,
                        "correct_url": correct_url,
                        "updated": success,
                    }
                )
            else:
                results.append(
                    {
                        "episode": episode,
                        "current_url": current_url,
                        "correct_url": correct_url,
                        "updated": False,
                    }
                )

        return results

    def generate_report(self, results: list[dict]) -> str:
        """Genera un reporte de las correcciones aplicadas."""
        report = "=== REPORTE DE CORRECCIONES DE URLs ESPECÍFICAS ===\n\n"

        updated_count = 0

        for result in results:
            episode = result["episode"]
            program_number = episode["program_number"]
            title = episode["title"]
            current_url = result["current_url"]
            correct_url = result["correct_url"]
            updated = result["updated"]

            report += f"Episodio #{program_number}: {title}\n"
            report += f"URL actual: {current_url}\n"
            report += f"URL correcta: {correct_url}\n"

            if updated:
                report += "Estado: ✅ ACTUALIZADO\n"
                updated_count += 1
            elif correct_url == current_url:
                report += "Estado: ℹ️ YA CORRECTO\n"
            else:
                report += "Estado: ❌ NO ACTUALIZADO\n"

            report += "\n" + "-" * 80 + "\n\n"

        report += "RESUMEN:\n"
        report += f"- Total episodios procesados: {len(results)}\n"
        report += f"- Episodios actualizados: {updated_count}\n"
        report += f"- Episodios ya correctos: {sum(1 for r in results if r['correct_url'] == r['current_url'])}\n"

        return report


def main():
    """Función principal."""
    logger.info("Iniciando corrección de URLs específicas de episodios...")

    fixer = SpecificEpisodeURLFixer()
    results = fixer.process_episodes()

    # Generar reporte
    report = fixer.generate_report(results)
    print(report)

    # Guardar reporte en archivo
    with open("logs/specific_episode_urls_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(
        "Corrección completada. Reporte guardado en logs/specific_episode_urls_report.txt"
    )


if __name__ == "__main__":
    main()
