#!/usr/bin/env python3
"""
from datetime import datetime

import csv
import json
import sys
from pathlib import Path
from typing import Any
from services.logger_setup import setup_logger
from services.supabase_database import SupabaseDatabase
    import argparse

Script para hacer backup de la base de datos Supabase.
Exporta todas las tablas a archivos JSON y CSV con timestamp.
"""

# Agregar el directorio raíz al path para importar los servicios
sys.path.append(str(Path(__file__).parent.parent.parent))


# Configurar logger
logger = setup_logger(__name__)


class SupabaseBackup:
    """Clase para manejar backups de la base de datos Supabase."""

    def __init__(self, output_dir: str = "backups"):
        """
        Inicializa el backup manager.

        Args:
            output_dir: Directorio donde se guardarán los backups
        """
        self.db = SupabaseDatabase()
        self.output_dir = Path(output_dir)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.output_dir / f"backup_{self.timestamp}"

        # Crear directorio de backup
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Definir las tablas a hacer backup
        self.tables = ["podcasts", "songs", "extra_links"]

    def export_table_to_json(self, table_name: str) -> str:
        """
        Exporta una tabla a formato JSON.

        Args:
            table_name: Nombre de la tabla

        Returns:
            Ruta del archivo JSON creado
        """
        try:
            logger.info(f"Exportando tabla {table_name} a JSON...")

            # Obtener todos los datos de la tabla
            response = self.db.client.table(table_name).select("*").execute()
            data = response.data

            # Crear archivo JSON
            json_file = self.backup_dir / f"{table_name}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(
                f"✅ Tabla {table_name} exportada a {json_file} ({len(data)} registros)"
            )
            return str(json_file)

        except Exception as e:
            logger.error(f"❌ Error al exportar tabla {table_name} a JSON: {e}")
            raise

    def export_table_to_csv(self, table_name: str) -> str:
        """
        Exporta una tabla a formato CSV.

        Args:
            table_name: Nombre de la tabla

        Returns:
            Ruta del archivo CSV creado
        """
        try:
            logger.info(f"Exportando tabla {table_name} a CSV...")

            # Obtener todos los datos de la tabla
            response = self.db.client.table(table_name).select("*").execute()
            data = response.data

            if not data:
                logger.warning(f"⚠️ Tabla {table_name} está vacía")
                return ""

            # Crear archivo CSV
            csv_file = self.backup_dir / f"{table_name}.csv"
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)

            logger.info(
                f"✅ Tabla {table_name} exportada a {csv_file} ({len(data)} registros)"
            )
            return str(csv_file)

        except Exception as e:
            logger.error(f"❌ Error al exportar tabla {table_name} a CSV: {e}")
            raise

    def create_backup_summary(self) -> str:
        """
        Crea un archivo de resumen del backup.

        Returns:
            Ruta del archivo de resumen
        """
        try:
            summary_file = self.backup_dir / "backup_summary.txt"

            with open(summary_file, "w", encoding="utf-8") as f:
                f.write("=== RESUMEN DE BACKUP SUPABASE ===\n")
                f.write(
                    f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
                f.write(f"Directorio: {self.backup_dir}\n\n")

                # Contar registros por tabla
                f.write("ESTADÍSTICAS POR TABLA:\n")
                f.write("-" * 30 + "\n")

                for table in self.tables:
                    try:
                        response = self.db.client.table(table).select("id").execute()
                        count = len(response.data)
                        f.write(f"{table}: {count} registros\n")
                    except Exception as e:
                        f.write(f"{table}: Error al contar - {e}\n")

                f.write("\nARCHIVOS CREADOS:\n")
                f.write("-" * 30 + "\n")

                for file_path in self.backup_dir.glob("*"):
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        f.write(f"{file_path.name}: {size} bytes\n")

            logger.info(f"✅ Resumen de backup creado en {summary_file}")
            return str(summary_file)

        except Exception as e:
            logger.error(f"❌ Error al crear resumen de backup: {e}")
            raise

    def create_metadata_file(self) -> str:
        """
        Crea un archivo de metadatos con información del backup.

        Returns:
            Ruta del archivo de metadatos
        """
        try:
            metadata_file = self.backup_dir / "metadata.json"

            metadata = {
                "backup_info": {
                    "timestamp": self.timestamp,
                    "datetime": datetime.now().isoformat(),
                    "backup_dir": str(self.backup_dir),
                    "tables": self.tables,
                },
                "database_info": {
                    "type": "supabase",
                    "project_url": self.db.project_url,
                    "api_key_length": len(self.db.api_key) if self.db.api_key else 0,
                },
                "files": [],
            }

            # Agregar información de archivos
            for file_path in self.backup_dir.glob("*"):
                if file_path.is_file():
                    metadata["files"].append(
                        {
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "type": file_path.suffix,
                        }
                    )

            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Metadatos creados en {metadata_file}")
            return str(metadata_file)

        except Exception as e:
            logger.error(f"❌ Error al crear metadatos: {e}")
            raise

    def run_backup(self) -> dict[str, Any]:
        """
        Ejecuta el backup completo de la base de datos.

        Returns:
            Diccionario con información del backup realizado
        """
        logger.info("🚀 Iniciando backup de Supabase...")

        backup_info = {
            "timestamp": self.timestamp,
            "backup_dir": str(self.backup_dir),
            "tables": {},
            "files": [],
            "success": True,
            "errors": [],
        }

        try:
            # Exportar cada tabla
            for table in self.tables:
                try:
                    # Exportar a JSON
                    json_file = self.export_table_to_json(table)
                    backup_info["tables"][table] = {
                        "json_file": json_file,
                        "csv_file": None,
                    }

                    # Exportar a CSV
                    csv_file = self.export_table_to_csv(table)
                    if csv_file:
                        backup_info["tables"][table]["csv_file"] = csv_file

                except Exception as e:
                    error_msg = f"Error en tabla {table}: {e}"
                    logger.error(error_msg)
                    backup_info["errors"].append(error_msg)
                    backup_info["success"] = False

            # Crear archivos adicionales
            try:
                summary_file = self.create_backup_summary()
                metadata_file = self.create_metadata_file()

                backup_info["files"].extend([summary_file, metadata_file])

            except Exception as e:
                error_msg = f"Error creando archivos adicionales: {e}"
                logger.error(error_msg)
                backup_info["errors"].append(error_msg)

            if backup_info["success"]:
                logger.info(f"✅ Backup completado exitosamente en {self.backup_dir}")
            else:
                logger.warning("⚠️ Backup completado con errores")

            return backup_info

        except Exception as e:
            logger.error(f"❌ Error fatal durante el backup: {e}")
            backup_info["success"] = False
            backup_info["errors"].append(f"Error fatal: {e}")
            return backup_info


def main():
    """Función principal del script."""

    parser = argparse.ArgumentParser(description="Backup de base de datos Supabase")
    parser.add_argument(
        "--output-dir",
        default="backups",
        help="Directorio donde guardar los backups (default: backups)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "both"],
        default="both",
        help="Formato de exportación (default: both)",
    )

    args = parser.parse_args()

    try:
        # Crear instancia de backup
        backup = SupabaseBackup(args.output_dir)

        # Ejecutar backup
        result = backup.run_backup()

        if result["success"]:
            print("\n✅ Backup completado exitosamente!")
            print(f"📁 Directorio: {result['backup_dir']}")
            print(f"📊 Tablas procesadas: {len(result['tables'])}")
        else:
            print("\n⚠️ Backup completado con errores:")
            for error in result["errors"]:
                print(f"   - {error}")

        return 0 if result["success"] else 1

    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        print(f"❌ Error fatal: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
