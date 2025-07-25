#!/usr/bin/env python3
"""
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


import sys
from services.supabase_database import SupabaseDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para diagnosticar el estado actual de los datos en Supabase.
Esto nos ayudará a verificar si es seguro cambiar los tipos de columna.
"""


# Agregar el directorio raíz al path


def diagnose_supabase_data():
    """
    Diagnostica el estado actual de los datos en Supabase.
    """
    print("🔍 DIAGNÓSTICO DE DATOS EN SUPABASE")
    print("=" * 60)

    db = SupabaseDatabase()

    try:
        # Obtener todos los podcasts
        podcasts = db.get_all_podcasts()

        print(f"📊 Total de episodios: {len(podcasts)}")
        print()

        # Analizar program_number
        print("🔢 ANÁLISIS DE PROGRAM_NUMBER")
        print("-" * 40)

        program_numbers = []
        invalid_program_numbers = []

        for podcast in podcasts:
            program_number = podcast.get("program_number")
            if program_number:
                program_numbers.append(str(program_number))
                # Verificar si es numérico
                if not str(program_number).isdigit():
                    invalid_program_numbers.append(
                        {
                            "id": podcast["id"],
                            "program_number": program_number,
                            "title": podcast.get("title", "Sin título"),
                        }
                    )

        print(f"Total program_numbers: {len(program_numbers)}")
        print(
            f"Program numbers válidos (numéricos): {len(program_numbers) - len(invalid_program_numbers)}"
        )
        print(f"Program numbers inválidos: {len(invalid_program_numbers)}")

        if invalid_program_numbers:
            print("\n❌ Program numbers problemáticos:")
            for item in invalid_program_numbers[:10]:  # Mostrar solo los primeros 10
                print(
                    f"  - ID {item['id']}: '{item['program_number']}' en '{item['title']}'"
                )
            if len(invalid_program_numbers) > 10:
                print(f"  ... y {len(invalid_program_numbers) - 10} más")

        # Analizar date
        print("\n📅 ANÁLISIS DE DATE")
        print("-" * 40)

        dates = []
        invalid_dates = []
        date_formats = {}

        for podcast in podcasts:
            date = podcast.get("date")
            if date:
                dates.append(str(date))

                # Verificar formato YYYY-MM-DD
                if len(str(date)) == 10 and str(date)[4] == "-" and str(date)[7] == "-":
                    try:
                        # Intentar parsear como fecha

                        datetime.strptime(str(date), "%Y-%m-%d")
                        format_key = "YYYY-MM-DD"
                    except ValueError:
                        invalid_dates.append(
                            {
                                "id": podcast["id"],
                                "date": date,
                                "title": podcast.get("title", "Sin título"),
                                "reason": "Formato YYYY-MM-DD pero fecha inválida",
                            }
                        )
                        format_key = "YYYY-MM-DD (inválida)"
                else:
                    invalid_dates.append(
                        {
                            "id": podcast["id"],
                            "date": date,
                            "title": podcast.get("title", "Sin título"),
                            "reason": f"Formato no estándar: {str(date)}",
                        }
                    )
                    format_key = f"Formato: {str(date)[:20]}..."

                date_formats[format_key] = date_formats.get(format_key, 0) + 1

        print(f"Total dates: {len(dates)}")
        print(f"Dates válidas (YYYY-MM-DD): {len(dates) - len(invalid_dates)}")
        print(f"Dates inválidas: {len(invalid_dates)}")

        print("\n📊 Formatos de fecha encontrados:")
        for format_type, count in sorted(
            date_formats.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  - {format_type}: {count}")

        if invalid_dates:
            print("\n❌ Fechas problemáticas:")
            for item in invalid_dates[:10]:  # Mostrar solo los primeros 10
                print(
                    f"  - ID {item['id']}: '{item['date']}' en '{item['title']}' ({item['reason']})"
                )
            if len(invalid_dates) > 10:
                print(f"  ... y {len(invalid_dates) - 10} más")

        # Verificar duplicados de fecha
        print("\n🔄 VERIFICACIÓN DE DUPLICADOS")
        print("-" * 40)

        date_counts = {}
        for date in dates:
            date_counts[date] = date_counts.get(date, 0) + 1

        duplicates = {date: count for date, count in date_counts.items() if count > 1}

        if duplicates:
            print(f"❌ Fechas duplicadas encontradas: {len(duplicates)}")
            for date, count in sorted(duplicates.items())[
                :5
            ]:  # Mostrar solo las primeras 5
                print(f"  - {date}: {count} episodios")
            if len(duplicates) > 5:
                print(f"  ... y {len(duplicates) - 5} fechas más con duplicados")
        else:
            print("✅ No se encontraron fechas duplicadas")

        # Recomendaciones
        print("\n💡 RECOMENDACIONES")
        print("-" * 40)

        if invalid_program_numbers or invalid_dates or duplicates:
            print("❌ NO ES SEGURO cambiar los tipos de columna ahora.")
            print("   Se encontraron problemas que deben resolverse primero:")

            if invalid_program_numbers:
                print(
                    f"   - {len(invalid_program_numbers)} program_numbers no numéricos"
                )
            if invalid_dates:
                print(f"   - {len(invalid_dates)} fechas en formato no estándar")
            if duplicates:
                print(f"   - {len(duplicates)} fechas duplicadas")

            print("\n🔧 Pasos recomendados:")
            print("1. Normalizar program_numbers no numéricos")
            print("2. Convertir fechas a formato YYYY-MM-DD")
            print("3. Resolver duplicados de fecha")
            print("4. Luego cambiar tipos de columna")
        else:
            print("✅ ES SEGURO cambiar los tipos de columna.")
            print("   Todos los datos están en formato correcto.")

        # Mostrar algunos ejemplos
        print("\n📋 EJEMPLOS DE DATOS")
        print("-" * 40)

        print("Primeros 5 episodios:")
        for i, podcast in enumerate(podcasts[:5]):
            print(
                f"  {i+1}. ID {podcast['id']}: #{podcast.get('program_number', 'N/A')} - {podcast.get('date', 'N/A')} - {podcast.get('title', 'Sin título')[:50]}..."
            )

    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        raise


def main():
    """Función principal."""
    diagnose_supabase_data()


if __name__ == "__main__":
    main()
