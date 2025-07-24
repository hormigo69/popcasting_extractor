#!/usr/bin/env python3
"""
Script para comparar los enlaces extras de la tabla extra_links vs el campo web_extra_links
en la tabla podcasts para identificar diferencias y duplicaciones.
"""

import json
import sys
from pathlib import Path

# Añadir el directorio services al path
sys.path.append(str(Path(__file__).parent.parent.parent / "services"))

from supabase_database import SupabaseDatabase


class ExtraLinksComparator:
    def __init__(self):
        self.db = SupabaseDatabase()

    def get_extra_links_from_table(self):
        """Obtiene todos los enlaces extras de la tabla extra_links"""
        try:
            response = (
                self.db.client.table("extra_links")
                .select("podcast_id, text, url")
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"❌ Error obteniendo enlaces de tabla extra_links: {e}")
            return []

    def get_extra_links_from_podcasts(self):
        """Obtiene todos los enlaces extras del campo web_extra_links en podcasts"""
        try:
            response = (
                self.db.client.table("podcasts")
                .select("id, program_number, web_extra_links")
                .execute()
            )
            podcast_links = []

            for podcast in response.data:
                if podcast.get("web_extra_links"):
                    try:
                        links = json.loads(podcast["web_extra_links"])
                        for link in links:
                            podcast_links.append(
                                {
                                    "podcast_id": podcast["id"],
                                    "program_number": podcast["program_number"],
                                    "text": link.get("text", ""),
                                    "url": link.get("url", ""),
                                }
                            )
                    except json.JSONDecodeError:
                        print(f"⚠️  Error parseando JSON para episodio {podcast['id']}")
                        continue

            return podcast_links
        except Exception as e:
            print(f"❌ Error obteniendo enlaces de campo web_extra_links: {e}")
            return []

    def get_podcast_info(self, podcast_ids):
        """Obtiene información básica de los podcasts"""
        try:
            response = (
                self.db.client.table("podcasts")
                .select("id, program_number, title, date")
                .in_("id", podcast_ids)
                .execute()
            )
            return {podcast["id"]: podcast for podcast in response.data}
        except Exception as e:
            print(f"❌ Error obteniendo información de podcasts: {e}")
            return {}

    def compare_links(self):
        """Compara los enlaces de ambas fuentes"""
        print("🔍 Comparando enlaces extras de ambas fuentes...")

        # Obtener enlaces de ambas fuentes
        table_links = self.get_extra_links_from_table()
        podcast_links = self.get_extra_links_from_podcasts()

        print(f"📊 Enlaces en tabla extra_links: {len(table_links)}")
        print(f"📊 Enlaces en campo web_extra_links: {len(podcast_links)}")

        # Agrupar por podcast_id
        table_by_podcast = {}
        for link in table_links:
            podcast_id = link["podcast_id"]
            if podcast_id not in table_by_podcast:
                table_by_podcast[podcast_id] = []
            table_by_podcast[podcast_id].append(link)

        podcast_by_podcast = {}
        for link in podcast_links:
            podcast_id = link["podcast_id"]
            if podcast_id not in podcast_by_podcast:
                podcast_by_podcast[podcast_id] = []
            podcast_by_podcast[podcast_id].append(link)

        # Obtener información de podcasts
        all_podcast_ids = set(table_by_podcast.keys()) | set(podcast_by_podcast.keys())
        podcast_info = self.get_podcast_info(list(all_podcast_ids))

        # Análisis detallado
        analysis = {
            "solo_en_tabla": [],
            "solo_en_podcasts": [],
            "en_ambas": [],
            "diferencias": [],
            "estadisticas": {
                "total_episodios_con_enlaces": len(all_podcast_ids),
                "episodios_solo_tabla": 0,
                "episodios_solo_podcasts": 0,
                "episodios_en_ambas": 0,
                "enlaces_solo_tabla": 0,
                "enlaces_solo_podcasts": 0,
                "enlaces_en_ambas": 0,
            },
        }

        for podcast_id in all_podcast_ids:
            table_links_for_podcast = table_by_podcast.get(podcast_id, [])
            podcast_links_for_podcast = podcast_by_podcast.get(podcast_id, [])

            podcast_data = {
                "podcast_id": podcast_id,
                "program_number": podcast_info.get(podcast_id, {}).get(
                    "program_number"
                ),
                "title": podcast_info.get(podcast_id, {}).get("title"),
                "date": podcast_info.get(podcast_id, {}).get("date"),
                "table_links": table_links_for_podcast,
                "podcast_links": podcast_links_for_podcast,
            }

            if table_links_for_podcast and not podcast_links_for_podcast:
                analysis["solo_en_tabla"].append(podcast_data)
                analysis["estadisticas"]["episodios_solo_tabla"] += 1
                analysis["estadisticas"]["enlaces_solo_tabla"] += len(
                    table_links_for_podcast
                )
            elif podcast_links_for_podcast and not table_links_for_podcast:
                analysis["solo_en_podcasts"].append(podcast_data)
                analysis["estadisticas"]["episodios_solo_podcasts"] += 1
                analysis["estadisticas"]["enlaces_solo_podcasts"] += len(
                    podcast_links_for_podcast
                )
            elif table_links_for_podcast and podcast_links_for_podcast:
                analysis["en_ambas"].append(podcast_data)
                analysis["estadisticas"]["episodios_en_ambas"] += 1

                # Comparar enlaces individuales
                table_urls = {
                    link["url"]: link["text"] for link in table_links_for_podcast
                }
                podcast_urls = {
                    link["url"]: link["text"] for link in podcast_links_for_podcast
                }

                solo_table_urls = set(table_urls.keys()) - set(podcast_urls.keys())
                solo_podcast_urls = set(podcast_urls.keys()) - set(table_urls.keys())

                analysis["estadisticas"]["enlaces_solo_tabla"] += len(solo_table_urls)
                analysis["estadisticas"]["enlaces_solo_podcasts"] += len(
                    solo_podcast_urls
                )
                analysis["estadisticas"]["enlaces_en_ambas"] += len(
                    set(table_urls.keys()) & set(podcast_urls.keys())
                )

                if solo_table_urls or solo_podcast_urls:
                    analysis["diferencias"].append(
                        {
                            "podcast_id": podcast_id,
                            "program_number": podcast_info.get(podcast_id, {}).get(
                                "program_number"
                            ),
                            "solo_en_tabla": [
                                {"url": url, "text": table_urls[url]}
                                for url in solo_table_urls
                            ],
                            "solo_en_podcasts": [
                                {"url": url, "text": podcast_urls[url]}
                                for url in solo_podcast_urls
                            ],
                        }
                    )

        return analysis

    def print_report(self, analysis):
        """Imprime el reporte de comparación"""
        print("\n" + "=" * 80)
        print("📋 REPORTE DE COMPARACIÓN DE ENLACES EXTRAS")
        print("=" * 80)

        stats = analysis["estadisticas"]
        print("\n📊 ESTADÍSTICAS GENERALES:")
        print(
            f"   • Total episodios con enlaces: {stats['total_episodios_con_enlaces']}"
        )
        print(
            f"   • Episodios solo en tabla extra_links: {stats['episodios_solo_tabla']}"
        )
        print(
            f"   • Episodios solo en campo web_extra_links: {stats['episodios_solo_podcasts']}"
        )
        print(f"   • Episodios en ambas fuentes: {stats['episodios_en_ambas']}")
        print(f"   • Enlaces solo en tabla: {stats['enlaces_solo_tabla']}")
        print(f"   • Enlaces solo en campo podcasts: {stats['enlaces_solo_podcasts']}")
        print(f"   • Enlaces en ambas fuentes: {stats['enlaces_en_ambas']}")

        print(
            f"\n🔍 EPISODIOS SOLO EN TABLA EXTRA_LINKS ({len(analysis['solo_en_tabla'])}):"
        )
        for item in analysis["solo_en_tabla"][:10]:  # Mostrar solo los primeros 10
            print(
                f"   • #{item['program_number']} - {item['title']} ({len(item['table_links'])} enlaces)"
            )
        if len(analysis["solo_en_tabla"]) > 10:
            print(f"   ... y {len(analysis['solo_en_tabla']) - 10} más")

        print(
            f"\n🔍 EPISODIOS SOLO EN CAMPO WEB_EXTRA_LINKS ({len(analysis['solo_en_podcasts'])}):"
        )
        for item in analysis["solo_en_podcasts"][:10]:  # Mostrar solo los primeros 10
            print(
                f"   • #{item['program_number']} - {item['title']} ({len(item['podcast_links'])} enlaces)"
            )
        if len(analysis["solo_en_podcasts"]) > 10:
            print(f"   ... y {len(analysis['solo_en_podcasts']) - 10} más")

        print(f"\n🔍 EPISODIOS EN AMBAS FUENTES ({len(analysis['en_ambas'])}):")
        for item in analysis["en_ambas"][:5]:  # Mostrar solo los primeros 5
            print(f"   • #{item['program_number']} - {item['title']}")
            print(
                f"     Tabla: {len(item['table_links'])} enlaces, Campo: {len(item['podcast_links'])} enlaces"
            )
        if len(analysis["en_ambas"]) > 5:
            print(f"   ... y {len(analysis['en_ambas']) - 5} más")

        if analysis["diferencias"]:
            print(f"\n⚠️  EPISODIOS CON DIFERENCIAS ({len(analysis['diferencias'])}):")
            for diff in analysis["diferencias"][:5]:  # Mostrar solo los primeros 5
                print(f"   • #{diff['program_number']}:")
                if diff["solo_en_tabla"]:
                    print(f"     Solo en tabla: {len(diff['solo_en_tabla'])} enlaces")
                if diff["solo_en_podcasts"]:
                    print(
                        f"     Solo en campo: {len(diff['solo_en_podcasts'])} enlaces"
                    )
            if len(analysis["diferencias"]) > 5:
                print(f"   ... y {len(analysis['diferencias']) - 5} más")

        print("\n💡 RECOMENDACIONES:")
        if stats["episodios_solo_tabla"] > 0:
            print(
                f"   • Migrar {stats['episodios_solo_tabla']} episodios de tabla a campo web_extra_links"
            )
        if stats["episodios_solo_podcasts"] > 0:
            print("   • Los episodios solo en web_extra_links ya están actualizados")
        if analysis["diferencias"]:
            print(
                f"   • Revisar {len(analysis['diferencias'])} episodios con diferencias"
            )

        print("=" * 80)

    def save_detailed_report(self, analysis):
        """Guarda un reporte detallado en archivo"""
        report_path = (
            Path(__file__).parent.parent.parent
            / "logs"
            / "extra_links_comparison_report.txt"
        )

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("REPORTE DETALLADO DE COMPARACIÓN DE ENLACES EXTRAS\n")
            f.write("=" * 80 + "\n\n")

            stats = analysis["estadisticas"]
            f.write("ESTADÍSTICAS GENERALES:\n")
            f.write(
                f"Total episodios con enlaces: {stats['total_episodios_con_enlaces']}\n"
            )
            f.write(
                f"Episodios solo en tabla extra_links: {stats['episodios_solo_tabla']}\n"
            )
            f.write(
                f"Episodios solo en campo web_extra_links: {stats['episodios_solo_podcasts']}\n"
            )
            f.write(f"Episodios en ambas fuentes: {stats['episodios_en_ambas']}\n")
            f.write(f"Enlaces solo en tabla: {stats['enlaces_solo_tabla']}\n")
            f.write(
                f"Enlaces solo en campo podcasts: {stats['enlaces_solo_podcasts']}\n"
            )
            f.write(f"Enlaces en ambas fuentes: {stats['enlaces_en_ambas']}\n\n")

            f.write("EPISODIOS SOLO EN TABLA EXTRA_LINKS:\n")
            for item in analysis["solo_en_tabla"]:
                f.write(
                    f"#{item['program_number']} - {item['title']} ({item['date']})\n"
                )
                for link in item["table_links"]:
                    f.write(f"  • {link['text']}: {link['url']}\n")
                f.write("\n")

            f.write("EPISODIOS SOLO EN CAMPO WEB_EXTRA_LINKS:\n")
            for item in analysis["solo_en_podcasts"]:
                f.write(
                    f"#{item['program_number']} - {item['title']} ({item['date']})\n"
                )
                for link in item["podcast_links"]:
                    f.write(f"  • {link['text']}: {link['url']}\n")
                f.write("\n")

            f.write("EPISODIOS CON DIFERENCIAS:\n")
            for diff in analysis["diferencias"]:
                f.write(f"#{diff['program_number']}:\n")
                if diff["solo_en_tabla"]:
                    f.write("  Solo en tabla:\n")
                    for link in diff["solo_en_tabla"]:
                        f.write(f"    • {link['text']}: {link['url']}\n")
                if diff["solo_en_podcasts"]:
                    f.write("  Solo en campo:\n")
                    for link in diff["solo_en_podcasts"]:
                        f.write(f"    • {link['text']}: {link['url']}\n")
                f.write("\n")

        print(f"📄 Reporte detallado guardado en: {report_path}")


def main():
    """Función principal"""
    print("🔍 Iniciando comparación de enlaces extras...")

    comparator = ExtraLinksComparator()
    analysis = comparator.compare_links()

    comparator.print_report(analysis)
    comparator.save_detailed_report(analysis)


if __name__ == "__main__":
    main()
