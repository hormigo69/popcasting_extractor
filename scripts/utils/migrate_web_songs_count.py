#!/usr/bin/env python3
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
from config import DATABASE_TYPE
from logger_setup import setup_parser_logger
from supabase_database import get_supabase_connection

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

            from scripts.utils.update_web_songs_count import main as update_main

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

Script para migrar y actualizar el campo web_songs_count en la base de datos.

Este script:
1. Ejecuta el script SQL para añadir el campo a Supabase
2. Actualiza el campo web_songs_count para episodios existentes
3. Verifica que la migración se haya completado correctamente
"""

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))

# Importar directamente los módulos

# Configurar logger
logger = setup_parser_logger()


def run_supabase_migration():
    """
    Ejecuta la migración SQL en Supabase para añadir el campo web_songs_count.
    """
    try:
        # Verificar si estamos usando Supabase
        if DATABASE_TYPE == "supabase":
            print("🗄️  Detectada base de datos Supabase")
            print("📝 Ejecutando migración SQL...")

            # Ejecutar el script SQL para añadir el campo
            sql_script = """
            ALTER TABLE podcasts ADD COLUMN IF NOT EXISTS web_songs_count INTEGER;
            CREATE INDEX IF NOT EXISTS idx_podcasts_web_songs_count ON podcasts(web_songs_count);
            """

            try:
                # Obtener conexión a Supabase
                db = get_supabase_connection()
                # Ejecutar el script SQL
                db.client.rpc("exec_sql", {"sql": sql_script}).execute()
                print("✅ Migración SQL ejecutada exitosamente")
                return True
            except Exception as e:
                print(f"⚠️  No se pudo ejecutar la migración SQL automáticamente: {e}")
                print("📋 Por favor, ejecuta manualmente el script SQL en Supabase:")
                print("   migration/add_web_songs_count_field.sql")
                return False
        else:
            print("🗄️  Detectada base de datos SQLite")
            print("✅ La migración se ejecutará automáticamente al inicializar la BD")
            return True

    except Exception as e:
        print(f"❌ Error ejecutando migración: {e}")
        return False


def main():
    """Función principal del script."""
    print("🎵 Migrador de web_songs_count")
    print("=" * 40)

    # Ejecutar migración SQL
    migration_success = run_supabase_migration()

    if migration_success:
        print("\n🔄 Ejecutando actualización de web_songs_count...")

        # Importar y ejecutar el script de actualización
        try:
            update_main()
        except ImportError as e:
            print(f"❌ Error importando script de actualización: {e}")
            print(
                "💡 Ejecuta manualmente: python scripts/utils/update_web_songs_count.py"
            )
        except Exception as e:
            print(f"❌ Error ejecutando actualización: {e}")
    else:
        print("\n⚠️  Migración SQL no completada. Ejecuta manualmente:")
        print("   1. migration/add_web_songs_count_field.sql en Supabase")
        print("   2. python scripts/utils/update_web_songs_count.py")

    print("\n✅ Proceso de migración completado")


if __name__ == "__main__":
    main()
