#!/usr/bin/env python3
"""
Script para limpiar y eliminar la tabla extra_links de Supabase.
Primero elimina todos los registros y luego la tabla.
"""

import sys
from pathlib import Path

# Añadir el directorio services al path
sys.path.append(str(Path(__file__).parent.parent.parent / "services"))

from supabase_database import SupabaseDatabase


class CleanAndDropExtraLinksTable:
    def __init__(self):
        self.db = SupabaseDatabase()

    def delete_all_extra_links(self):
        """Elimina todos los registros de la tabla extra_links"""
        print("🗑️  Eliminando todos los registros de extra_links...")

        try:
            # Eliminar todos los registros
            response = (
                self.db.client.table("extra_links").delete().neq("id", 0).execute()
            )
            deleted_count = len(response.data) if response.data else 0

            print(f"✅ Eliminados {deleted_count} registros de extra_links")
            return True

        except Exception as e:
            print(f"❌ Error eliminando registros: {e}")
            return False

    def verify_table_empty(self):
        """Verifica que la tabla está vacía"""
        print("🔍 Verificando que la tabla está vacía...")

        try:
            response = (
                self.db.client.table("extra_links").select("id").limit(1).execute()
            )
            if response.data:
                print(f"❌ La tabla aún tiene {len(response.data)} registros")
                return False
            else:
                print("✅ Tabla extra_links está vacía")
                return True

        except Exception as e:
            print(f"❌ Error verificando tabla: {e}")
            return False

    def drop_table_via_sql(self):
        """Elimina la tabla usando SQL directo"""
        print("🗑️  Eliminando tabla extra_links...")

        try:
            # Usar el método execute_query si existe
            if hasattr(self.db, "execute_query"):
                self.db.execute_query("DROP TABLE IF EXISTS extra_links CASCADE;")
            else:
                # Alternativa: usar el cliente directamente
                # Esto puede no funcionar dependiendo de los permisos
                print(
                    "⚠️  No se puede ejecutar SQL directo. La tabla debe eliminarse manualmente."
                )
                print(
                    "   Ejecuta en Supabase SQL Editor: DROP TABLE IF EXISTS extra_links CASCADE;"
                )
                return False

            print("✅ Tabla extra_links eliminada exitosamente")
            return True

        except Exception as e:
            print(f"❌ Error eliminando tabla: {e}")
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
    print("🚨 LIMPIEZA Y ELIMINACIÓN DE TABLA EXTRA_LINKS")
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

    cleaner = CleanAndDropExtraLinksTable()

    # Paso 1: Eliminar todos los registros
    if not cleaner.delete_all_extra_links():
        print("❌ Error eliminando registros")
        return

    # Paso 2: Verificar que está vacía
    if not cleaner.verify_table_empty():
        print("❌ La tabla no está vacía")
        return

    # Paso 3: Eliminar la tabla
    if cleaner.drop_table_via_sql():
        # Paso 4: Verificar que se eliminó
        if cleaner.verify_table_dropped():
            print("\n✅ Tabla extra_links eliminada exitosamente")
        else:
            print("\n❌ Error verificando la eliminación")
    else:
        print("\n⚠️  La tabla debe eliminarse manualmente desde Supabase SQL Editor")
        print("   Ejecuta: DROP TABLE IF EXISTS extra_links CASCADE;")


if __name__ == "__main__":
    main()
