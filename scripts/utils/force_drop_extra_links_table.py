#!/usr/bin/env python3
"""
Script para forzar la eliminación de la tabla extra_links de Supabase.
Los enlaces únicos ya han sido migrados al campo web_extra_links.
"""

import sys
from pathlib import Path

# Añadir el directorio services al path
sys.path.append(str(Path(__file__).parent.parent.parent / "services"))

from supabase_database import SupabaseDatabase


class ForceExtraLinksTableDropper:
    def __init__(self):
        self.db = SupabaseDatabase()

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
    print("🚨 ELIMINACIÓN FORZADA DE TABLA EXTRA_LINKS")
    print("=" * 50)
    print("⚠️  ADVERTENCIA: Esta operación es irreversible")
    print("   Los enlaces únicos ya han sido migrados al campo web_extra_links")
    print("=" * 50)

    # Confirmación del usuario
    response = input(
        "\n¿Estás seguro de que quieres eliminar la tabla extra_links? (sí/no): "
    )
    if response.lower() not in ["sí", "si", "yes", "y"]:
        print("❌ Operación cancelada")
        return

    dropper = ForceExtraLinksTableDropper()

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
