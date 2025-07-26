#!/usr/bin/env python3
"""
Script simplificado para hacer backup de la base de datos Supabase.
Usa el DatabaseManager interno del sincronizador_rss.

Uso: python scripts/backup_supabase.py [--output-dir backups] [--tables podcasts,songs]
"""

import argparse
import sys
from pathlib import Path

# Agregar el directorio src al path para importaciones internas
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Importar directamente usando rutas absolutas para evitar problemas de importación
sys.path.insert(0, str(src_path / "components"))
sys.path.insert(0, str(src_path / "utils"))

from database_manager import DatabaseManager
from config_manager import ConfigManager
from logger import logger


def main():
    """Función principal del script."""
    
    parser = argparse.ArgumentParser(description="Backup de base de datos Supabase")
    parser.add_argument(
        "--output-dir",
        default="backups",
        help="Directorio donde guardar los backups (default: backups)"
    )
    parser.add_argument(
        "--tables",
        default="podcasts,songs",
        help="Tablas a hacer backup separadas por coma (default: podcasts,songs)"
    )
    
    args = parser.parse_args()
    
    try:
        # Configurar logger
        logger.info("🚀 Iniciando backup de Supabase...")
        
        # Cargar configuración
        logger.info("📋 Cargando configuración...")
        config_manager = ConfigManager()
        supabase_credentials = config_manager.get_supabase_credentials()
        
        # Crear instancia de DatabaseManager
        logger.info("🔌 Conectando a Supabase...")
        db_manager = DatabaseManager(
            supabase_url=supabase_credentials["url"],
            supabase_key=supabase_credentials["key"]
        )
        
        # Probar conexión
        db_manager.test_connection()
        
        # Parsear tablas
        tables = [table.strip() for table in args.tables.split(",")]
        logger.info(f"📊 Tablas a hacer backup: {', '.join(tables)}")
        
        # Ejecutar backup
        result = db_manager.create_backup(
            output_dir=args.output_dir,
            tables=tables
        )
        
        # Mostrar resultados
        if result["success"]:
            print("\n✅ Backup completado exitosamente!")
            print(f"📁 Directorio: {result['backup_dir']}")
            print(f"📊 Tablas procesadas: {len(result['tables'])}")
            
            for table, info in result["tables"].items():
                print(f"   - {table}: {info['record_count']} registros")
                print(f"     JSON: {info['json_file']}")
                if info['csv_file']:
                    print(f"     CSV: {info['csv_file']}")
            
            print(f"📄 Resumen: {result['summary_file']}")
            
        else:
            print("\n⚠️ Backup completado con errores:")
            for error in result["errors"]:
                print(f"   - {error}")
        
        # Cerrar conexión
        db_manager.close()
        
        return 0 if result["success"] else 1
        
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        print(f"❌ Error fatal: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
