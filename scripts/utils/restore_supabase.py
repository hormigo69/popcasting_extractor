#!/usr/bin/env python3
"""
import re

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from services.logger_setup import setup_logger
from services.supabase_database import SupabaseDatabase

Script para restaurar datos desde un backup de Supabase.
Permite restaurar tablas específicas o todo el backup.
"""

# Agregar el directorio raíz al path para importar los servicios
sys.path.append(str(Path(__file__).parent.parent.parent))


# Configurar logger
logger = setup_logger(__name__)


class SupabaseRestore:
    """Clase para manejar la restauración de backups de Supabase."""

    def __init__(self, backup_dir: str):
        """
        Inicializa el restore manager.

        Args:
            backup_dir: Directorio del backup a restaurar
        """
        self.db = SupabaseDatabase()
        self.backup_dir = Path(backup_dir)

        if not self.backup_dir.exists():
            raise ValueError(f"El directorio de backup no existe: {backup_dir}")

        # Verificar archivos de backup
        self.backup_files = self._find_backup_files()

    def _find_backup_files(self) -> dict[str, str]:
        """Encuentra los archivos de backup disponibles."""
        files = {}

        for json_file in self.backup_dir.glob("*.json"):
            if json_file.name != "metadata.json":
                table_name = json_file.stem
                files[table_name] = str(json_file)

        return files

    def load_backup_data(self, table_name: str) -> list[dict[str, Any]]:
        """
        Carga los datos de backup de una tabla específica.

        Args:
            table_name: Nombre de la tabla

        Returns:
            Lista de registros de la tabla
        """
        if table_name not in self.backup_files:
            raise ValueError(f"No se encontró backup para la tabla: {table_name}")

        json_file = self.backup_files[table_name]

        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            logger.info(f"✅ Datos cargados de {json_file}: {len(data)} registros")
            return data

        except Exception as e:
            logger.error(f"❌ Error cargando datos de {json_file}: {e}")
            raise

    def restore_table(self, table_name: str, clear_existing: bool = False) -> bool:
        """
        Restaura una tabla específica desde el backup.

        Args:
            table_name: Nombre de la tabla a restaurar
            clear_existing: Si True, borra los datos existentes antes de restaurar

        Returns:
            True si la restauración fue exitosa
        """
        try:
            logger.info(f"🔄 Restaurando tabla: {table_name}")

            # Cargar datos del backup
            backup_data = self.load_backup_data(table_name)

            if clear_existing:
                logger.info(f"🗑️ Borrando datos existentes de {table_name}...")
                self.db.client.table(table_name).delete().neq("id", 0).execute()
                logger.info(f"✅ Datos existentes borrados de {table_name}")

            if not backup_data:
                logger.warning(f"⚠️ No hay datos para restaurar en {table_name}")
                return True

            # Restaurar datos
            logger.info(
                f"📥 Insertando {len(backup_data)} registros en {table_name}..."
            )

            # Insertar en lotes para evitar límites de tamaño
            batch_size = 100
            for i in range(0, len(backup_data), batch_size):
                batch = backup_data[i : i + batch_size]
                self.db.client.table(table_name).insert(batch).execute()
                logger.info(f"   ✅ Lote {i//batch_size + 1}: {len(batch)} registros")

            logger.info(f"✅ Tabla {table_name} restaurada exitosamente")
            return True

        except Exception as e:
            logger.error(f"❌ Error restaurando tabla {table_name}: {e}")
            return False

    def restore_all_tables(self, clear_existing: bool = False) -> dict[str, bool]:
        """
        Restaura todas las tablas disponibles en el backup.

        Args:
            clear_existing: Si True, borra los datos existentes antes de restaurar

        Returns:
            Diccionario con el estado de restauración de cada tabla
        """
        logger.info("🚀 Iniciando restauración completa...")

        results = {}

        for table_name in self.backup_files.keys():
            success = self.restore_table(table_name, clear_existing)
            results[table_name] = success

            if not success:
                logger.error(f"❌ Falló la restauración de {table_name}")

        # Resumen
        successful = sum(results.values())
        total = len(results)

        logger.info("\n📊 Resumen de restauración:")
        logger.info(f"   ✅ Exitosas: {successful}/{total}")
        logger.info(f"   ❌ Fallidas: {total - successful}/{total}")

        return results

    def preview_backup(self) -> dict[str, Any]:
        """
        Muestra una vista previa del contenido del backup.

        Returns:
            Información del backup
        """
        preview = {"backup_dir": str(self.backup_dir), "tables": {}, "metadata": None}

        # Información de tablas
        for table_name, json_file in self.backup_files.items():
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                preview["tables"][table_name] = {
                    "file": json_file,
                    "records": len(data),
                    "sample_fields": list(data[0].keys()) if data else [],
                }
            except Exception as e:
                preview["tables"][table_name] = {"file": json_file, "error": str(e)}

        # Buscar archivo de metadatos
        metadata_file = self.backup_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, encoding="utf-8") as f:
                    preview["metadata"] = json.load(f)
            except Exception as e:
                preview["metadata"] = {"error": str(e)}

        return preview


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description="Restaurar backup de Supabase")
    parser.add_argument("backup_dir", help="Directorio del backup a restaurar")
    parser.add_argument("--table", help="Restaurar solo una tabla específica")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Borrar datos existentes antes de restaurar",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Solo mostrar vista previa del backup sin restaurar",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simular la restauración sin ejecutarla"
    )

    args = parser.parse_args()

    try:
        # Crear instancia de restore
        restore = SupabaseRestore(args.backup_dir)

        if args.preview:
            # Mostrar vista previa
            preview = restore.preview_backup()

            print(f"\n📁 Backup: {preview['backup_dir']}")
            print(f"📊 Tablas disponibles: {len(preview['tables'])}")

            for table_name, info in preview["tables"].items():
                if "error" in info:
                    print(f"   ❌ {table_name}: Error - {info['error']}")
                else:
                    print(f"   ✅ {table_name}: {info['records']} registros")
                    print(f"      Campos: {', '.join(info['sample_fields'][:5])}...")

            if preview["metadata"]:
                print("\n📋 Metadatos disponibles")

            return 0

        if args.dry_run:
            # Simular restauración
            print("🔍 Simulando restauración...")
            preview = restore.preview_backup()

            if args.table:
                if args.table in preview["tables"]:
                    info = preview["tables"][args.table]
                    print(
                        f"📊 Se restaurarían {info['records']} registros en {args.table}"
                    )
                else:
                    print(f"❌ Tabla {args.table} no encontrada en el backup")
            else:
                total_records = sum(
                    info.get("records", 0) for info in preview["tables"].values()
                )
                print(f"📊 Se restaurarían {total_records} registros en total")

            return 0

        # Ejecutar restauración real
        if args.table:
            # Restaurar tabla específica
            success = restore.restore_table(args.table, args.clear)
            if success:
                print(f"✅ Tabla {args.table} restaurada exitosamente")
                return 0
            else:
                print(f"❌ Error restaurando tabla {args.table}")
                return 1
        else:
            # Restaurar todas las tablas
            results = restore.restore_all_tables(args.clear)

            if all(results.values()):
                print("✅ Restauración completada exitosamente")
                return 0
            else:
                print("⚠️ Restauración completada con errores")
                return 1

    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        print(f"❌ Error fatal: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
