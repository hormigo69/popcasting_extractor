#!/usr/bin/env python3
"""
Generador de reportes para analizar discrepancias entre RSS y web.
"""

import json
from datetime import datetime

from . import database as db
from .web_extractor import WebExtractor


class WebReportGenerator:
    def __init__(self):
        self.extractor = WebExtractor()

    def generate_discrepancy_report(self, max_episodes: int = 50) -> dict:
        """
        Genera un reporte completo de discrepancias entre RSS y web.
        """
        print("🔍 Generando reporte de discrepancias...")

        # Obtener episodios con información web
        podcasts = self._get_episodes_with_web_info(max_episodes)

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_episodes_analyzed": len(podcasts),
            "episodes_with_discrepancies": 0,
            "episodes_without_discrepancies": 0,
            "total_song_discrepancies": 0,
            "total_link_discrepancies": 0,
            "episode_details": [],
            "summary": {},
        }

        for podcast in podcasts:
            print(f"📄 Analizando episodio {podcast['program_number']}...")

            discrepancies = self.extractor.compare_rss_vs_web(podcast["id"])

            episode_detail = {
                "episode_id": podcast["id"],
                "program_number": podcast["program_number"],
                "date": podcast["date"],
                "title": podcast["title"],
                "has_discrepancies": discrepancies.get("summary", {}).get(
                    "has_discrepancies", False
                ),
                "song_discrepancies": len(discrepancies.get("songs_differences", [])),
                "link_discrepancies": len(discrepancies.get("links_differences", [])),
                "rss_songs_count": discrepancies.get("summary", {}).get(
                    "rss_songs_count", 0
                ),
                "web_songs_count": discrepancies.get("summary", {}).get(
                    "web_songs_count", 0
                ),
                "rss_links_count": discrepancies.get("summary", {}).get(
                    "rss_links_count", 0
                ),
                "web_links_count": discrepancies.get("summary", {}).get(
                    "web_links_count", 0
                ),
                "song_differences": discrepancies.get("songs_differences", []),
                "link_differences": discrepancies.get("links_differences", []),
            }

            report["episode_details"].append(episode_detail)

            if episode_detail["has_discrepancies"]:
                report["episodes_with_discrepancies"] += 1
                report["total_song_discrepancies"] += episode_detail[
                    "song_discrepancies"
                ]
                report["total_link_discrepancies"] += episode_detail[
                    "link_discrepancies"
                ]
            else:
                report["episodes_without_discrepancies"] += 1

        # Generar resumen
        report["summary"] = self._generate_summary(report)

        return report

    def _get_episodes_with_web_info(self, max_episodes: int) -> list[dict]:
        """
        Obtiene episodios que tienen información web disponible.
        """
        conn = db.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, title, date, program_number, wordpress_url, last_web_check
            FROM podcasts
            WHERE wordpress_url IS NOT NULL AND last_web_check IS NOT NULL
            ORDER BY date DESC
            LIMIT ?
        """,
            (max_episodes,),
        )

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def _generate_summary(self, report: dict) -> dict:
        """
        Genera un resumen estadístico del reporte.
        """
        total_episodes = report["total_episodes_analyzed"]

        if total_episodes == 0:
            return {}

        summary = {
            "discrepancy_rate": (report["episodes_with_discrepancies"] / total_episodes)
            * 100,
            "average_song_discrepancies_per_episode": report["total_song_discrepancies"]
            / total_episodes,
            "average_link_discrepancies_per_episode": report["total_link_discrepancies"]
            / total_episodes,
            "episodes_with_song_discrepancies": len(
                [e for e in report["episode_details"] if e["song_discrepancies"] > 0]
            ),
            "episodes_with_link_discrepancies": len(
                [e for e in report["episode_details"] if e["link_discrepancies"] > 0]
            ),
            "most_common_song_issues": self._analyze_common_issues(
                report["episode_details"], "song_differences"
            ),
            "most_common_link_issues": self._analyze_common_issues(
                report["episode_details"], "link_differences"
            ),
        }

        return summary

    def _analyze_common_issues(
        self, episode_details: list[dict], issue_type: str
    ) -> list[dict]:
        """
        Analiza los problemas más comunes en las discrepancias.
        """
        issue_counts = {}

        for episode in episode_details:
            for issue in episode[issue_type]:
                if issue in issue_counts:
                    issue_counts[issue] += 1
                else:
                    issue_counts[issue] = 1

        # Ordenar por frecuencia
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)

        return [{"issue": issue, "count": count} for issue, count in sorted_issues[:5]]

    def save_report(self, report: dict, filename: str = None) -> str:
        """
        Guarda el reporte en un archivo JSON.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"web_discrepancy_report_{timestamp}.json"

        filepath = f"outputs/{filename}"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return filepath

    def print_summary(self, report: dict):
        """
        Imprime un resumen del reporte en consola.
        """
        print("\n" + "=" * 60)
        print("📊 REPORTE DE DISCREPANCIAS RSS vs WEB")
        print("=" * 60)

        summary = report["summary"]

        print(f"📅 Generado: {report['generated_at']}")
        print(f"📄 Episodios analizados: {report['total_episodes_analyzed']}")
        print(f"✅ Sin discrepancias: {report['episodes_without_discrepancies']}")
        print(f"⚠️  Con discrepancias: {report['episodes_with_discrepancies']}")
        print(f"📈 Tasa de discrepancias: {summary.get('discrepancy_rate', 0):.1f}%")

        print("\n🎵 Discrepancias en canciones:")
        print(f"   Total: {report['total_song_discrepancies']}")
        print(
            f"   Promedio por episodio: {summary.get('average_song_discrepancies_per_episode', 0):.1f}"
        )
        print(
            f"   Episodios afectados: {summary.get('episodes_with_song_discrepancies', 0)}"
        )

        print("\n🔗 Discrepancias en enlaces:")
        print(f"   Total: {report['total_link_discrepancies']}")
        print(
            f"   Promedio por episodio: {summary.get('average_link_discrepancies_per_episode', 0):.1f}"
        )
        print(
            f"   Episodios afectados: {summary.get('episodes_with_link_discrepancies', 0)}"
        )

        # Mostrar problemas más comunes
        if summary.get("most_common_song_issues"):
            print("\n🎵 Problemas más comunes en canciones:")
            for issue in summary["most_common_song_issues"][:3]:
                print(f"   • {issue['issue']} ({issue['count']} veces)")

        if summary.get("most_common_link_issues"):
            print("\n🔗 Problemas más comunes en enlaces:")
            for issue in summary["most_common_link_issues"][:3]:
                print(f"   • {issue['issue']} ({issue['count']} veces)")

        print("\n" + "=" * 60)

    def generate_episode_list_report(self, max_episodes: int = 50) -> dict:
        """
        Genera un reporte simple con la lista de episodios y sus discrepancias.
        """
        print("📋 Generando reporte de lista de episodios...")

        podcasts = self._get_episodes_with_web_info(max_episodes)

        report = {"generated_at": datetime.now().isoformat(), "episodes": []}

        for podcast in podcasts:
            discrepancies = self.extractor.compare_rss_vs_web(podcast["id"])

            episode_info = {
                "id": podcast["id"],
                "program_number": podcast["program_number"],
                "date": podcast["date"],
                "title": podcast["title"],
                "wordpress_url": podcast["wordpress_url"],
                "has_discrepancies": discrepancies.get("summary", {}).get(
                    "has_discrepancies", False
                ),
                "rss_songs": discrepancies.get("summary", {}).get("rss_songs_count", 0),
                "web_songs": discrepancies.get("summary", {}).get("web_songs_count", 0),
                "rss_links": discrepancies.get("summary", {}).get("rss_links_count", 0),
                "web_links": discrepancies.get("summary", {}).get("web_links_count", 0),
            }

            report["episodes"].append(episode_info)

        return report


def main():
    """
    Función principal para ejecutar el generador de reportes.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generador de reportes web de Popcasting"
    )
    parser.add_argument(
        "--max-episodes",
        type=int,
        default=50,
        help="Número máximo de episodios a analizar",
    )
    parser.add_argument("--output", type=str, help="Nombre del archivo de salida")
    parser.add_argument(
        "--type",
        choices=["detailed", "list"],
        default="detailed",
        help="Tipo de reporte",
    )

    args = parser.parse_args()

    # Inicializar base de datos
    db.initialize_database()

    generator = WebReportGenerator()

    if args.type == "detailed":
        report = generator.generate_discrepancy_report(args.max_episodes)
        generator.print_summary(report)
    else:
        report = generator.generate_episode_list_report(args.max_episodes)
        print(f"📋 Reporte de lista generado con {len(report['episodes'])} episodios")

    # Guardar reporte
    if args.output:
        filepath = generator.save_report(report, args.output)
    else:
        filepath = generator.save_report(report)

    print(f"💾 Reporte guardado en: {filepath}")


if __name__ == "__main__":
    main()
