#!/usr/bin/env python3
"""
Script simple para hacer backup de la base de datos Supabase.
Uso: python scripts/backup_supabase_simple.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.supabase_database import SupabaseDatabase


def hacer_backup():
    """Función principal para hacer backup de Supabase."""

    print("🚀 Iniciando backup de Supabase...")

    try:
        # Conectar a Supabase
        db = SupabaseDatabase()
        print("✅ Conexión a Supabase establecida")

        # Crear directorio de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("backups") / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Directorio de backup: {backup_dir}")

        # Tablas a hacer backup
        tablas = ["podcasts", "songs", "extra_links"]

        for tabla in tablas:
            print(f"\n📊 Exportando tabla: {tabla}")

            try:
                # Obtener todos los datos de la tabla con paginación
                datos = []
                page_size = 1000
                offset = 0

                while True:
                    response = (
                        db.client.table(tabla)
                        .select("*")
                        .range(offset, offset + page_size - 1)
                        .execute()
                    )
                    page_data = response.data

                    if not page_data:
                        break

                    datos.extend(page_data)
                    offset += page_size

                    print(
                        f"   📄 Página {offset//page_size}: {len(page_data)} registros"
                    )

                # Guardar como JSON
                archivo_json = backup_dir / f"{tabla}.json"
                with open(archivo_json, "w", encoding="utf-8") as f:
                    json.dump(datos, f, indent=2, ensure_ascii=False, default=str)

                print(
                    f"   ✅ {tabla}: {len(datos)} registros exportados a {archivo_json}"
                )

            except Exception as e:
                print(f"   ❌ Error exportando {tabla}: {e}")

        # Crear archivo de resumen
        resumen_file = backup_dir / "resumen.txt"
        with open(resumen_file, "w", encoding="utf-8") as f:
            f.write(
                f"Backup Supabase - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"Directorio: {backup_dir}\n\n")

            for tabla in tablas:
                try:
                    # Contar registros con paginación
                    total_count = 0
                    page_size = 1000
                    offset = 0

                    while True:
                        response = (
                            db.client.table(tabla)
                            .select("id")
                            .range(offset, offset + page_size - 1)
                            .execute()
                        )
                        page_data = response.data

                        if not page_data:
                            break

                        total_count += len(page_data)
                        offset += page_size

                    f.write(f"{tabla}: {total_count} registros\n")
                except Exception as e:
                    f.write(f"{tabla}: Error al contar - {e}\n")

        print("\n✅ Backup completado exitosamente!")
        print(f"📁 Ubicación: {backup_dir}")
        print(f"📄 Resumen: {resumen_file}")

        return True

    except Exception as e:
        print(f"❌ Error durante el backup: {e}")
        return False


if __name__ == "__main__":
    success = hacer_backup()
    exit(0 if success else 1)
