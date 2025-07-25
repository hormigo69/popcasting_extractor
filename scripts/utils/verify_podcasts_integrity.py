#!/usr/bin/env python3
"""
import sys
from datetime import datetime
from pathlib import Path
from services.supabase_database import SupabaseDatabase

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

                from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para verificar la integridad de la tabla podcasts en Supabase.
Realiza las siguientes verificaciones:
1. Verifica que no faltan números de capítulos entre el 0 y el 484
2. Verifica que las fechas sean correlativas al ordenar por número de capítulo
3. Marca qué campos faltan en qué filas
"""


# Agregar el directorio raíz al path


def verify_missing_episode_numbers(podcasts):
    """
    Verifica que no faltan números de capítulos entre el 0 y el 484.
    """
    print("🔍 VERIFICANDO NÚMEROS DE CAPÍTULOS FALTANTES")
    print("-" * 60)

    # Extraer números de programa válidos
    program_numbers = []
    for podcast in podcasts:
        program_number = podcast.get("program_number")
        if program_number is not None:  # Incluir el valor 0
            program_numbers.append(int(program_number))

    # Ordenar y encontrar faltantes
    program_numbers.sort()
    missing_numbers = []

    # Verificar desde 0 hasta el máximo encontrado
    max_number = max(program_numbers) if program_numbers else 0
    expected_range = range(0, max_number + 1)

    for num in expected_range:
        if num not in program_numbers:
            missing_numbers.append(num)

    # Resultados
    print(f"📊 Total de episodios con número válido: {len(program_numbers)}")
    print(f"📊 Rango esperado: 0 - {max_number}")
    print(f"📊 Números encontrados: {len(program_numbers)}")

    if missing_numbers:
        print(f"❌ Números de capítulo faltantes: {len(missing_numbers)}")
        print("   Números faltantes:")
        for num in missing_numbers:
            print(f"     - #{num}")
    else:
        print("✅ No faltan números de capítulo en el rango")

    return {
        "total_with_number": len(program_numbers),
        "max_number": max_number,
        "missing_numbers": missing_numbers,
        "missing_count": len(missing_numbers),
    }


def verify_date_sequence(podcasts):
    """
    Verifica que las fechas sean correlativas al ordenar por número de capítulo.
    """
    print("\n📅 VERIFICANDO SECUENCIA DE FECHAS")
    print("-" * 60)

    # Filtrar podcasts con número de programa válido
    valid_podcasts = []
    for podcast in podcasts:
        program_number = podcast.get("program_number")
        if program_number is not None:  # Incluir el valor 0
            valid_podcasts.append(podcast)

    # Ordenar por número de programa
    valid_podcasts.sort(key=lambda x: int(x.get("program_number")))

    print(f"📊 Episodios con número válido para análisis: {len(valid_podcasts)}")

    # Verificar secuencia de fechas
    date_issues = []
    previous_date = None
    previous_number = None

    for podcast in valid_podcasts:
        current_number = int(podcast.get("program_number"))
        current_date = podcast.get("date")

        if current_date and previous_date:
            try:
                # Convertir fechas a datetime para comparación

                current_dt = datetime.strptime(str(current_date), "%Y-%m-%d")
                previous_dt = datetime.strptime(str(previous_date), "%Y-%m-%d")

                # Verificar si la fecha actual es anterior a la anterior
                if current_dt < previous_dt:
                    date_issues.append(
                        {
                            "episode_number": current_number,
                            "episode_id": podcast.get("id"),
                            "current_date": current_date,
                            "previous_number": previous_number,
                            "previous_date": previous_date,
                            "issue": "Fecha anterior a episodio previo",
                        }
                    )

            except ValueError:
                date_issues.append(
                    {
                        "episode_number": current_number,
                        "episode_id": podcast.get("id"),
                        "current_date": current_date,
                        "previous_number": previous_number,
                        "previous_date": previous_date,
                        "issue": "Formato de fecha inválido",
                    }
                )

        previous_date = current_date
        previous_number = current_number

    # Resultados
    if date_issues:
        print(f"❌ Problemas de secuencia de fechas encontrados: {len(date_issues)}")
        print("   Problemas detectados:")
        for issue in date_issues:
            print(
                f"     - Episodio #{issue['episode_number']} (ID {issue['episode_id']}): {issue['current_date']}"
            )
            print(
                f"       vs Episodio #{issue['previous_number']}: {issue['previous_date']}"
            )
            print(f"       Problema: {issue['issue']}")
    else:
        print("✅ Las fechas están en secuencia correcta")

    return {
        "valid_podcasts": len(valid_podcasts),
        "date_issues": date_issues,
        "issues_count": len(date_issues),
    }


def verify_missing_fields(podcasts):
    """
    Marca qué campos faltan en qué filas.
    """
    print("\n📋 VERIFICANDO CAMPOS FALTANTES")
    print("-" * 60)

    # Campos obligatorios que no deberían faltar
    required_fields = ["title", "date", "program_number"]

    # Campos opcionales que pueden faltar legítimamente
    optional_fields = [
        "url",
        "download_url",
        "file_size",
        "wordpress_url",
        "cover_image_url",
        "web_extra_links",
        "web_playlist",
        "last_web_check",
    ]

    missing_required = []
    missing_optional = []

    for podcast in podcasts:
        podcast_id = podcast.get("id")
        program_number = podcast.get("program_number")

        # Verificar campos obligatorios
        for field in required_fields:
            value = podcast.get(field)
            # Para program_number, permitir el valor 0
            if field == "program_number":
                if value is None:
                    missing_required.append(
                        {
                            "episode_id": podcast_id,
                            "program_number": program_number,
                            "field": field,
                            "title": podcast.get("title", "Sin título"),
                        }
                    )
            else:
                if not value:
                    missing_required.append(
                        {
                            "episode_id": podcast_id,
                            "program_number": program_number,
                            "field": field,
                            "title": podcast.get("title", "Sin título"),
                        }
                    )

        # Verificar campos opcionales (solo para reporte)
        for field in optional_fields:
            if not podcast.get(field):
                missing_optional.append(
                    {
                        "episode_id": podcast_id,
                        "program_number": program_number,
                        "field": field,
                        "title": podcast.get("title", "Sin título"),
                    }
                )

    # Resultados
    print(f"📊 Total de episodios analizados: {len(podcasts)}")
    print(f"📊 Campos obligatorios faltantes: {len(missing_required)}")
    print(f"📊 Campos opcionales faltantes: {len(missing_optional)}")

    if missing_required:
        print("\n❌ Campos obligatorios faltantes:")
        for item in missing_required:
            print(
                f"     - Episodio #{item['program_number']} (ID {item['episode_id']}): {item['field']} faltante"
            )
            print(f"       Título: {item['title'][:50]}...")
    else:
        print("\n✅ Todos los campos obligatorios están presentes")

    # Mostrar resumen de campos opcionales faltantes
    optional_summary = {}
    for item in missing_optional:
        field = item["field"]
        optional_summary[field] = optional_summary.get(field, 0) + 1

    if optional_summary:
        print("\n📊 Resumen de campos opcionales faltantes:")
        for field, count in sorted(optional_summary.items()):
            percentage = (count / len(podcasts)) * 100
            print(f"     - {field}: {count} episodios ({percentage:.1f}%)")

    return {
        "total_podcasts": len(podcasts),
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "required_count": len(missing_required),
        "optional_count": len(missing_optional),
    }


def generate_report(results, output_file):
    """
    Genera un reporte completo y lo guarda en archivo.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("VERIFICACIÓN DE INTEGRIDAD - TABLA PODCASTS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Fecha de verificación: {timestamp}\n")
        f.write("Base de datos: Supabase\n\n")

        # Resumen ejecutivo
        f.write("📊 RESUMEN EJECUTIVO\n")
        f.write("-" * 40 + "\n")

        # Números de capítulo
        chapter_results = results["chapter_verification"]
        f.write(
            f"Episodios con número válido: {chapter_results['total_with_number']}\n"
        )
        f.write(f"Número máximo encontrado: {chapter_results['max_number']}\n")
        f.write(f"Números faltantes: {chapter_results['missing_count']}\n")

        # Secuencia de fechas
        date_results = results["date_verification"]
        f.write(f"Episodios analizados para fechas: {date_results['valid_podcasts']}\n")
        f.write(f"Problemas de secuencia: {date_results['issues_count']}\n")

        # Campos faltantes
        field_results = results["field_verification"]
        f.write(f"Total episodios: {field_results['total_podcasts']}\n")
        f.write(f"Campos obligatorios faltantes: {field_results['required_count']}\n")
        f.write(f"Campos opcionales faltantes: {field_results['optional_count']}\n\n")

        # Detalles de números faltantes
        if chapter_results["missing_numbers"]:
            f.write("🔍 NÚMEROS DE CAPÍTULO FALTANTES\n")
            f.write("-" * 40 + "\n")
            for num in chapter_results["missing_numbers"]:
                f.write(f"  - #{num}\n")
            f.write("\n")

        # Detalles de problemas de fecha
        if date_results["date_issues"]:
            f.write("📅 PROBLEMAS DE SECUENCIA DE FECHAS\n")
            f.write("-" * 40 + "\n")
            for issue in date_results["date_issues"]:
                f.write(
                    f"  Episodio #{issue['episode_number']} (ID {issue['episode_id']}): {issue['current_date']}\n"
                )
                f.write(
                    f"    vs Episodio #{issue['previous_number']}: {issue['previous_date']}\n"
                )
                f.write(f"    Problema: {issue['issue']}\n\n")

        # Detalles de campos obligatorios faltantes
        if field_results["missing_required"]:
            f.write("❌ CAMPOS OBLIGATORIOS FALTANTES\n")
            f.write("-" * 40 + "\n")
            for item in field_results["missing_required"]:
                f.write(
                    f"  Episodio #{item['program_number']} (ID {item['episode_id']}): {item['field']}\n"
                )
                f.write(f"    Título: {item['title']}\n\n")

        # Resumen de campos opcionales
        optional_summary = {}
        for item in field_results["missing_optional"]:
            field = item["field"]
            optional_summary[field] = optional_summary.get(field, 0) + 1

        if optional_summary:
            f.write("📊 CAMPOS OPCIONALES FALTANTES\n")
            f.write("-" * 40 + "\n")
            for field, count in sorted(optional_summary.items()):
                percentage = (count / field_results["total_podcasts"]) * 100
                f.write(f"  {field}: {count} episodios ({percentage:.1f}%)\n")
            f.write("\n")

        # Recomendaciones
        f.write("💡 RECOMENDACIONES\n")
        f.write("-" * 40 + "\n")

        if chapter_results["missing_count"] > 0:
            f.write(
                f"• Investigar los {chapter_results['missing_count']} números de capítulo faltantes\n"
            )

        if date_results["issues_count"] > 0:
            f.write(
                f"• Revisar los {date_results['issues_count']} problemas de secuencia de fechas\n"
            )

        if field_results["required_count"] > 0:
            f.write(
                f"• Completar los {field_results['required_count']} campos obligatorios faltantes\n"
            )

        if not any(
            [
                chapter_results["missing_count"],
                date_results["issues_count"],
                field_results["required_count"],
            ]
        ):
            f.write("• ✅ La integridad de la tabla podcasts es correcta\n")

        f.write("\n" + "=" * 80 + "\n")


def main():
    """
    Función principal que ejecuta todas las verificaciones.
    """
    print("🔍 VERIFICACIÓN DE INTEGRIDAD - TABLA PODCASTS")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Base de datos: Supabase")
    print()

    try:
        # Conectar a Supabase
        db = SupabaseDatabase()
        print("✅ Conexión a Supabase establecida")

        # Obtener todos los podcasts
        print("📥 Obteniendo datos de podcasts...")
        podcasts = db.get_all_podcasts()
        print(f"✅ {len(podcasts)} podcasts obtenidos")
        print()

        # Ejecutar verificaciones
        chapter_results = verify_missing_episode_numbers(podcasts)
        date_results = verify_date_sequence(podcasts)
        field_results = verify_missing_fields(podcasts)

        # Consolidar resultados
        results = {
            "chapter_verification": chapter_results,
            "date_verification": date_results,
            "field_verification": field_results,
        }

        # Generar reporte en archivo
        output_dir = Path(__file__).parent.parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"podcasts_integrity_report_{timestamp}.txt"

        generate_report(results, output_file)
        print(f"\n📄 Reporte guardado en: {output_file}")

        # Resumen final
        print("\n" + "=" * 80)
        print("📊 RESUMEN FINAL")
        print("=" * 80)

        total_issues = (
            chapter_results["missing_count"]
            + date_results["issues_count"]
            + field_results["required_count"]
        )

        if total_issues == 0:
            print("🎉 ¡La integridad de la tabla podcasts es perfecta!")
        else:
            print(f"⚠️  Se encontraron {total_issues} problemas de integridad:")
            print(
                f"   - Números de capítulo faltantes: {chapter_results['missing_count']}"
            )
            print(
                f"   - Problemas de secuencia de fechas: {date_results['issues_count']}"
            )
            print(
                f"   - Campos obligatorios faltantes: {field_results['required_count']}"
            )

        print(f"\n📄 Reporte detallado disponible en: {output_file}")

    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        raise


if __name__ == "__main__":
    main()
