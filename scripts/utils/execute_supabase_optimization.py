#!/usr/bin/env python3
"""
Script para ejecutar la optimización SQL directamente en Supabase.
Este script ejecuta el SQL para cambiar los tipos de columna.
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase


def execute_supabase_optimization():
    """
    Ejecuta la optimización SQL en Supabase para cambiar tipos de columna.
    """
    print("🔧 EJECUTANDO OPTIMIZACIÓN SQL EN SUPABASE")
    print("=" * 60)

    db = SupabaseDatabase()

    try:
        # PASO 1: Verificar estado actual
        print("📊 PASO 1: Verificando estado actual...")

        # Verificar tipos actuales
        result = db.client.rpc(
            "execute_sql",
            {
                "sql": """
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_name = 'podcasts'
              AND column_name IN ('date', 'program_number')
            ORDER BY column_name;
            """
            },
        ).execute()

        print("Tipos actuales de columnas:")
        for row in result.data:
            print(
                f"  - {row['column_name']}: {row['data_type']} ({'NULL' if row['is_nullable'] == 'YES' else 'NOT NULL'})"
            )

        # Verificar datos actuales
        result = db.client.rpc(
            "execute_sql",
            {
                "sql": r"""
            SELECT
                'program_number' as column_name,
                COUNT(*) as total_records,
                COUNT(CASE WHEN program_number ~ '^[0-9]+$' THEN 1 END) as valid_numbers,
                COUNT(CASE WHEN program_number !~ '^[0-9]+$' THEN 1 END) as invalid_numbers
            FROM podcasts
            UNION ALL
            SELECT
                'date' as column_name,
                COUNT(*) as total_records,
                COUNT(CASE WHEN date ~ '^\d{4}-\d{2}-\d{2}$' THEN 1 END) as valid_dates,
                COUNT(CASE WHEN date !~ '^\d{4}-\d{2}-\d{2}$' THEN 1 END) as invalid_dates
            FROM podcasts;
            """
            },
        ).execute()

        print("\nDatos actuales:")
        for row in result.data:
            print(
                f"  - {row['column_name']}: {row['total_records']} total, {row['valid_numbers'] or row['valid_dates']} válidos, {row['invalid_numbers'] or row['invalid_dates']} inválidos"
            )

        # Confirmar con el usuario
        print(
            "\n⚠️  ADVERTENCIA: Esto cambiará los tipos de columna en la base de datos."
        )
        print("   Se recomienda hacer un backup antes de continuar.")

        response = input("\n¿Continuar con la optimización? (s/N): ").strip().lower()
        if response not in ["s", "si", "sí", "y", "yes"]:
            print("❌ Optimización cancelada por el usuario.")
            return

        # PASO 2: Limpiar datos
        print("\n🔄 PASO 2: Limpiando datos...")

        # Limpiar program_number
        result = db.client.rpc(
            "execute_sql",
            {
                "sql": """
            UPDATE podcasts
            SET program_number = REGEXP_REPLACE(program_number, '[^0-9]', '', 'g')
            WHERE program_number IS NOT NULL
              AND program_number !~ '^[0-9]+$';
            """
            },
        ).execute()
        print("  ✅ Program numbers limpiados")

        # Limpiar date
        result = db.client.rpc(
            "execute_sql",
            {
                "sql": r"""
            UPDATE podcasts
            SET date = TO_CHAR(TO_DATE(date, 'YYYY-MM-DD'), 'YYYY-MM-DD')
            WHERE date IS NOT NULL
              AND date ~ '^\d{4}-\d{2}-\d{2}$';
            """
            },
        ).execute()
        print("  ✅ Fechas limpiadas")

        # PASO 3: Cambiar tipos de columna
        print("\n🔄 PASO 3: Cambiando tipos de columna...")

        # Cambiar program_number
        result = db.client.rpc(
            "execute_sql",
            {
                "sql": """
            ALTER TABLE podcasts
            ALTER COLUMN program_number TYPE INTEGER USING program_number::INTEGER;
            """
            },
        ).execute()
        print("  ✅ program_number cambiado a INTEGER")

        # Cambiar date
        result = db.client.rpc(
            "execute_sql",
            {
                "sql": """
            ALTER TABLE podcasts
            ALTER COLUMN date TYPE DATE USING date::DATE;
            """
            },
        ).execute()
        print("  ✅ date cambiado a DATE")

        # PASO 4: Recrear índices
        print("\n🔄 PASO 4: Recreando índices...")

        # Eliminar índices existentes
        result = db.client.rpc(
            "execute_sql",
            {
                "sql": """
            DROP INDEX IF EXISTS idx_podcasts_date;
            DROP INDEX IF EXISTS idx_podcasts_program_number;
            """
            },
        ).execute()

        # Crear nuevos índices
        result = db.client.rpc(
            "execute_sql",
            {
                "sql": """
            CREATE INDEX idx_podcasts_date ON podcasts(date);
            CREATE INDEX idx_podcasts_program_number ON podcasts(program_number);
            """
            },
        ).execute()
        print("  ✅ Índices recreados")

        # PASO 5: Verificar resultado
        print("\n📊 PASO 5: Verificando resultado...")

        # Verificar tipos después del cambio
        result = db.client.rpc(
            "execute_sql",
            {
                "sql": """
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_name = 'podcasts'
              AND column_name IN ('date', 'program_number')
            ORDER BY column_name;
            """
            },
        ).execute()

        print("Tipos después del cambio:")
        for row in result.data:
            print(
                f"  - {row['column_name']}: {row['data_type']} ({'NULL' if row['is_nullable'] == 'YES' else 'NOT NULL'})"
            )

        # Verificar datos después del cambio
        result = db.client.rpc(
            "execute_sql",
            {
                "sql": """
            SELECT
                'program_number' as column_name,
                COUNT(*) as total_records,
                COUNT(CASE WHEN program_number IS NOT NULL THEN 1 END) as non_null_values,
                MIN(program_number) as min_value,
                MAX(program_number) as max_value
            FROM podcasts
            UNION ALL
            SELECT
                'date' as column_name,
                COUNT(*) as total_records,
                COUNT(CASE WHEN date IS NOT NULL THEN 1 END) as non_null_values,
                MIN(date) as min_value,
                MAX(date) as max_value
            FROM podcasts;
            """
            },
        ).execute()

        print("\nDatos después del cambio:")
        for row in result.data:
            print(
                f"  - {row['column_name']}: {row['total_records']} total, {row['non_null_values']} no nulos, rango: {row['min_value']} - {row['max_value']}"
            )

        print("\n✅ ¡Optimización completada exitosamente!")

    except Exception as e:
        print(f"❌ Error durante la optimización: {e}")
        raise


def main():
    """Función principal."""
    execute_supabase_optimization()


if __name__ == "__main__":
    main()
