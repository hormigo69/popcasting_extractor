#!/usr/bin/env python3
"""
Script para migrar los enlaces únicos de la tabla extra_links al campo web_extra_links
de la tabla podcasts. Solo migra los episodios 419, 322, 321 y 319.
"""

import json
import sys
from pathlib import Path

# Añadir el directorio services al path
sys.path.append(str(Path(__file__).parent.parent.parent / "services"))

from supabase_database import SupabaseDatabase


class ExtraLinksMigrator:
    def __init__(self):
        self.db = SupabaseDatabase()
        # Solo estos episodios tienen enlaces únicos en la tabla extra_links
        self.target_episodes = [419, 322, 321, 319]

    def get_extra_links_from_table(self):
        """Obtiene los enlaces extras de la tabla extra_links para los episodios objetivo"""
        try:
            # Obtener los podcast_ids de los episodios objetivo
            response = (
                self.db.client.table("podcasts")
                .select("id, program_number")
                .in_("program_number", self.target_episodes)
                .execute()
            )
            podcast_ids = [podcast["id"] for podcast in response.data]

            if not podcast_ids:
                print("❌ No se encontraron los episodios objetivo")
                return []

            # Obtener los enlaces extras de estos episodios
            response = (
                self.db.client.table("extra_links")
                .select("podcast_id, text, url")
                .in_("podcast_id", podcast_ids)
                .execute()
            )
            return response.data

        except Exception as e:
            print(f"❌ Error obteniendo enlaces de tabla extra_links: {e}")
            return []

    def get_current_web_extra_links(self, podcast_id):
        """Obtiene los enlaces extras actuales del campo web_extra_links"""
        try:
            response = (
                self.db.client.table("podcasts")
                .select("web_extra_links")
                .eq("id", podcast_id)
                .execute()
            )
            if response.data and response.data[0].get("web_extra_links"):
                return json.loads(response.data[0]["web_extra_links"])
            return []
        except Exception as e:
            print(f"❌ Error obteniendo web_extra_links para podcast {podcast_id}: {e}")
            return []

    def update_web_extra_links(self, podcast_id, new_links):
        """Actualiza el campo web_extra_links de un podcast"""
        try:
            update_data = {
                "web_extra_links": json.dumps(new_links),
                "last_web_check": "now()",
            }

            self.db.client.table("podcasts").update(update_data).eq(
                "id", podcast_id
            ).execute()
            return True
        except Exception as e:
            print(
                f"❌ Error actualizando web_extra_links para podcast {podcast_id}: {e}"
            )
            return False

    def migrate_links(self):
        """Migra los enlaces únicos de la tabla extra_links al campo web_extra_links"""
        print("🔄 Iniciando migración de enlaces únicos...")

        # Obtener enlaces de la tabla extra_links
        table_links = self.get_extra_links_from_table()

        if not table_links:
            print("❌ No se encontraron enlaces para migrar")
            return

        print(f"📊 Encontrados {len(table_links)} enlaces para migrar")

        # Agrupar por podcast_id
        links_by_podcast = {}
        for link in table_links:
            podcast_id = link["podcast_id"]
            if podcast_id not in links_by_podcast:
                links_by_podcast[podcast_id] = []
            links_by_podcast[podcast_id].append(link)

        # Obtener información de los podcasts
        podcast_ids = list(links_by_podcast.keys())
        response = (
            self.db.client.table("podcasts")
            .select("id, program_number, title")
            .in_("id", podcast_ids)
            .execute()
        )
        podcast_info = {podcast["id"]: podcast for podcast in response.data}

        migrated_count = 0
        updated_count = 0

        for podcast_id, links in links_by_podcast.items():
            program_number = podcast_info.get(podcast_id, {}).get("program_number")
            title = podcast_info.get(podcast_id, {}).get("title")

            print(f"\n📝 Procesando episodio #{program_number} - {title}")

            # Obtener enlaces actuales del campo web_extra_links
            current_links = self.get_current_web_extra_links(podcast_id)

            # Convertir enlaces de tabla al formato JSON
            new_links = []
            for link in links:
                new_links.append({"text": link["text"], "url": link["url"]})

            # Si no hay enlaces actuales, usar solo los nuevos
            if not current_links:
                final_links = new_links
                migrated_count += 1
                print(f"   ✅ Migrados {len(new_links)} enlaces (nuevos)")
            else:
                # Combinar enlaces existentes con nuevos (evitando duplicados)
                existing_urls = {link["url"] for link in current_links}
                unique_new_links = [
                    link for link in new_links if link["url"] not in existing_urls
                ]

                if unique_new_links:
                    final_links = current_links + unique_new_links
                    updated_count += 1
                    print(
                        f"   ✅ Añadidos {len(unique_new_links)} enlaces únicos a {len(current_links)} existentes"
                    )
                else:
                    final_links = current_links
                    print("   ⚠️  No se añadieron enlaces (ya existían)")

            # Actualizar el campo web_extra_links
            if self.update_web_extra_links(podcast_id, final_links):
                print(
                    f"   💾 Campo web_extra_links actualizado con {len(final_links)} enlaces"
                )
            else:
                print("   ❌ Error actualizando campo web_extra_links")

        print("\n📊 RESUMEN DE MIGRACIÓN:")
        print(f"   • Episodios migrados (nuevos): {migrated_count}")
        print(f"   • Episodios actualizados: {updated_count}")
        print(f"   • Total enlaces procesados: {len(table_links)}")

        return migrated_count + updated_count


def main():
    """Función principal"""
    print("🚀 Iniciando migración de enlaces únicos de extra_links a web_extra_links")
    print("📋 Episodios objetivo: 419, 322, 321, 319")

    migrator = ExtraLinksMigrator()
    result = migrator.migrate_links()

    if result:
        print("\n✅ Migración completada exitosamente")
    else:
        print("\n❌ Error en la migración")


if __name__ == "__main__":
    main()
