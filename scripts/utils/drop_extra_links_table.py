#!/usr/bin/env python3
"""
Script para eliminar la tabla extra_links de Supabase.
Solo ejecutar después de confirmar que todos los enlaces únicos han sido migrados.
"""

import sys
from pathlib import Path

# Añadir el directorio services al path
sys.path.append(str(Path(__file__).parent.parent.parent / "services"))

from supabase_database import SupabaseDatabase


class ExtraLinksTableDropper:
    def __init__(self):
        self.db = SupabaseDatabase()

    def verify_migration_complete(self):
        """Verifica que todos los enlaces únicos han sido migrados"""
        print("🔍 Verificando que la migración está completa...")

        try:
            # Obtener todos los enlaces de la tabla extra_links
            response = (
                self.db.client.table("extra_links")
                .select("podcast_id, text, url")
                .execute()
            )
            remaining_links = response.data

            if not remaining_links:
                print("✅ No quedan enlaces en la tabla extra_links")
                return True

            print(f"⚠️  Quedan {len(remaining_links)} enlaces en la tabla extra_links")

            # Obtener información de los podcasts con enlaces restantes
            podcast_ids = list({link["podcast_id"] for link in remaining_links})
            response = (
                self.db.client.table("podcasts")
                .select("id, program_number, title")
                .in_("id", podcast_ids)
                .execute()
            )
            podcast_info = {podcast["id"]: podcast for podcast in response.data}

            print("📋 Enlaces restantes:")
            for link in remaining_links:
                podcast = podcast_info.get(link["podcast_id"], {})
                print(
                    f"   • #{podcast.get('program_number')} - {link['text']}: {link['url']}"
                )

            return False

        except Exception as e:
            print(f"❌ Error verificando migración: {e}")
            return False

    def drop_extra_links_table(self):
        """Elimina la tabla extra_links"""
        print("🗑️  Eliminando tabla extra_links...")

        try:
            # Ejecutar SQL para eliminar la tabla
            sql = "DROP TABLE IF EXISTS extra_links CASCADE;"
            self.db.client.rpc("exec_sql", {"sql": sql}).execute()

            print("✅ Tabla extra_links eliminada exitosamente")
            return True

        except Exception as e:
            print(f"❌ Error eliminando tabla extra_links: {e}")
            return False

    def verify_table_dropped(self):
        """Verifica que la tabla ha sido eliminada"""
        print("🔍 Verificando que la tabla ha sido eliminada...")

        try:
            # Intentar acceder a la tabla
            self.db.client.table("extra_links").select("id").limit(1).execute()
            print("❌ La tabla extra_links aún existe")
            return False

        except Exception as e:
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                print("✅ Tabla extra_links eliminada correctamente")
                return True
            else:
                print(f"❌ Error inesperado: {e}")
                return False


def main():
    """Función principal"""
    print("🚨 ELIMINACIÓN DE TABLA EXTRA_LINKS")
    print("=" * 50)
    print("⚠️  ADVERTENCIA: Esta operación es irreversible")
    print("   Solo ejecutar después de migrar todos los enlaces únicos")
    print("=" * 50)

    # Confirmación del usuario
    response = input(
        "\n¿Estás seguro de que quieres eliminar la tabla extra_links? (sí/no): "
    )
    if response.lower() not in ["sí", "si", "yes", "y"]:
        print("❌ Operación cancelada")
        return

    dropper = ExtraLinksTableDropper()

    # Verificar que la migración está completa
    if not dropper.verify_migration_complete():
        print("\n❌ No se puede eliminar la tabla: quedan enlaces sin migrar")
        return

    # Confirmación final
    response = input("\n¿Confirmas la eliminación de la tabla extra_links? (sí/no): ")
    if response.lower() not in ["sí", "si", "yes", "y"]:
        print("❌ Operación cancelada")
        return

    # Eliminar la tabla
    if dropper.drop_extra_links_table():
        # Verificar que se eliminó correctamente
        if dropper.verify_table_dropped():
            print("\n✅ Tabla extra_links eliminada exitosamente")
        else:
            print("\n❌ Error verificando la eliminación")
    else:
        print("\n❌ Error eliminando la tabla")


if __name__ == "__main__":
    main()
