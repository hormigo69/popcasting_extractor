#!/usr/bin/env python3
"""
Script para verificar la integridad de la tabla songs en la base de datos.
Compara el número de canciones en songs vs web_songs_count en podcasts.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Añadir el directorio raíz al path para importar los servicios
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.config import DATABASE_TYPE
from services.database import get_db_connection
from services.supabase_database import SupabaseDatabase


def verify_songs_integrity():
    """Verifica la integridad de la tabla songs"""

    db_type = DATABASE_TYPE
    print(f"🔍 Verificando integridad de la tabla songs usando {db_type}")

    if db_type == "supabase":
        db = SupabaseDatabase()
        results = verify_supabase_songs_integrity(db)
    else:
        results = verify_sqlite_songs_integrity()

    # Generar informe
    generate_integrity_report(results)

    return results


def verify_supabase_songs_integrity(db):
    """Verifica la integridad de songs en Supabase"""

    results = {
        "total_podcasts": 0,
        "total_songs": 0,
        "podcasts_with_songs": 0,
        "podcasts_without_songs": [],
        "songs_count_mismatch": [],
        "missing_web_songs_count": [],
        "podcast_songs_summary": [],
    }

    try:
        # Obtener todos los podcasts con program_number y web_songs_count
        response = (
            db.client.table("podcasts")
            .select("id,program_number,title,date,web_songs_count")
            .not_.is_("program_number", "null")
            .order("program_number")
            .execute()
        )
        podcasts = response.data

        results["total_podcasts"] = len(podcasts)
        print(f"📊 Analizando {results['total_podcasts']} podcasts...")

        # Analizar cada podcast
        for podcast in podcasts:
            podcast_id = podcast["id"]
            program_number = podcast["program_number"]
            web_songs_count = podcast["web_songs_count"]

            # Obtener canciones del podcast
            songs_response = (
                db.client.table("songs")
                .select("id")
                .eq("podcast_id", podcast_id)
                .execute()
            )
            songs = songs_response.data

            songs_count = len(songs)
            results["total_songs"] += songs_count

            if songs_count > 0:
                results["podcasts_with_songs"] += 1
            else:
                results["podcasts_without_songs"].append(
                    {
                        "program_number": program_number,
                        "title": podcast["title"],
                        "date": str(podcast["date"]) if podcast["date"] else None,
                    }
                )

            # Verificar si web_songs_count está presente
            if web_songs_count is None:
                results["missing_web_songs_count"].append(
                    {
                        "program_number": program_number,
                        "title": podcast["title"],
                        "songs_count": songs_count,
                    }
                )

            # Verificar discrepancias en el conteo
            if web_songs_count is not None and songs_count != web_songs_count:
                results["songs_count_mismatch"].append(
                    {
                        "program_number": program_number,
                        "title": podcast["title"],
                        "web_songs_count": web_songs_count,
                        "actual_songs_count": songs_count,
                        "difference": songs_count - web_songs_count,
                    }
                )

            # Resumen del podcast
            results["podcast_songs_summary"].append(
                {
                    "program_number": program_number,
                    "title": podcast["title"],
                    "date": str(podcast["date"]) if podcast["date"] else None,
                    "web_songs_count": web_songs_count,
                    "actual_songs_count": songs_count,
                    "has_mismatch": web_songs_count is not None
                    and songs_count != web_songs_count,
                }
            )

        print("✅ Análisis completado")

    except Exception as e:
        print(f"❌ Error al verificar integridad en Supabase: {e}")
        raise

    return results


def verify_sqlite_songs_integrity():
    """Verifica la integridad de songs en SQLite"""

    results = {
        "total_podcasts": 0,
        "total_songs": 0,
        "podcasts_with_songs": 0,
        "podcasts_without_songs": [],
        "songs_count_mismatch": [],
        "missing_web_songs_count": [],
        "podcast_songs_summary": [],
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener todos los podcasts con program_number y web_songs_count
        cursor.execute("""
        SELECT id, program_number, title, date, web_songs_count
        FROM podcasts
        WHERE program_number IS NOT NULL
        ORDER BY program_number
        """)
        podcasts = cursor.fetchall()

        results["total_podcasts"] = len(podcasts)
        print(f"📊 Analizando {results['total_podcasts']} podcasts...")

        # Analizar cada podcast
        for podcast in podcasts:
            podcast_id = podcast["id"]
            program_number = podcast["program_number"]
            web_songs_count = podcast["web_songs_count"]

            # Obtener canciones del podcast
            cursor.execute("SELECT id FROM songs WHERE podcast_id = ?", (podcast_id,))
            songs = cursor.fetchall()

            songs_count = len(songs)
            results["total_songs"] += songs_count

            if songs_count > 0:
                results["podcasts_with_songs"] += 1
            else:
                results["podcasts_without_songs"].append(
                    {
                        "program_number": program_number,
                        "title": podcast["title"],
                        "date": podcast["date"],
                    }
                )

            # Verificar si web_songs_count está presente
            if web_songs_count is None:
                results["missing_web_songs_count"].append(
                    {
                        "program_number": program_number,
                        "title": podcast["title"],
                        "songs_count": songs_count,
                    }
                )

            # Verificar discrepancias en el conteo
            if web_songs_count is not None and songs_count != web_songs_count:
                results["songs_count_mismatch"].append(
                    {
                        "program_number": program_number,
                        "title": podcast["title"],
                        "web_songs_count": web_songs_count,
                        "actual_songs_count": songs_count,
                        "difference": songs_count - web_songs_count,
                    }
                )

            # Resumen del podcast
            results["podcast_songs_summary"].append(
                {
                    "program_number": program_number,
                    "title": podcast["title"],
                    "date": podcast["date"],
                    "web_songs_count": web_songs_count,
                    "actual_songs_count": songs_count,
                    "has_mismatch": web_songs_count is not None
                    and songs_count != web_songs_count,
                }
            )

        conn.close()
        print("✅ Análisis completado")

    except Exception as e:
        print(f"❌ Error al verificar integridad en SQLite: {e}")
        raise

    return results


def generate_integrity_report(results):
    """Genera un informe detallado en markdown"""

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = f"logs/songs_integrity_report_{timestamp}.md"

    # Crear directorio logs si no existe
    os.makedirs("logs", exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 📊 Informe de Integridad de la Tabla Songs\n\n")
        f.write(
            f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        # Resumen general
        f.write("## 📈 Resumen General\n\n")
        f.write(f"- **Total de podcasts:** {results['total_podcasts']}\n")
        f.write(f"- **Total de canciones:** {results['total_songs']}\n")
        f.write(f"- **Podcasts con canciones:** {results['podcasts_with_songs']}\n")
        f.write(f"- **Podcasts sin canciones:** {results['podcasts_without_songs']}\n")
        f.write(
            f"- **Promedio de canciones por podcast:** {results['total_songs'] / results['total_podcasts']:.1f}\n\n"
        )

        # Discrepancias en conteo de canciones
        if results["songs_count_mismatch"]:
            f.write("## ⚠️ Discrepancias en Conteo de Canciones\n\n")
            f.write(
                f"Se encontraron {len(results['songs_count_mismatch'])} discrepancias:\n\n"
            )
            f.write(
                "| Programa | Título | Web Songs Count | Actual Songs | Diferencia |\n"
            )
            f.write(
                "|----------|--------|-----------------|--------------|------------|\n"
            )
            for mismatch in results["songs_count_mismatch"]:
                f.write(
                    f"| {mismatch['program_number']} | {mismatch['title'][:50]}... | {mismatch['web_songs_count']} | {mismatch['actual_songs_count']} | {mismatch['difference']:+d} |\n"
                )
            f.write("\n")
        else:
            f.write("## ✅ Conteo de Canciones\n\n")
            f.write("No se encontraron discrepancias en el conteo de canciones.\n\n")

        # Podcasts sin web_songs_count
        if results["missing_web_songs_count"]:
            f.write("## 🔍 Podcasts sin web_songs_count\n\n")
            f.write(
                f"Se encontraron {len(results['missing_web_songs_count'])} podcasts sin web_songs_count:\n\n"
            )
            f.write("| Programa | Título | Canciones Actuales |\n")
            f.write("|----------|--------|-------------------|\n")
            for missing in results["missing_web_songs_count"]:
                f.write(
                    f"| {missing['program_number']} | {missing['title'][:50]}... | {missing['songs_count']} |\n"
                )
            f.write("\n")
        else:
            f.write("## ✅ Campo web_songs_count\n\n")
            f.write("Todos los podcasts tienen el campo web_songs_count.\n\n")

        # Podcasts sin canciones
        if results["podcasts_without_songs"]:
            f.write("## 🚫 Podcasts sin Canciones\n\n")
            f.write(
                f"Se encontraron {len(results['podcasts_without_songs'])} podcasts sin canciones:\n\n"
            )
            f.write("| Programa | Título | Fecha |\n")
            f.write("|----------|--------|-------|\n")
            for podcast in results["podcasts_without_songs"]:
                date_str = podcast["date"] if podcast["date"] else "N/A"
                f.write(
                    f"| {podcast['program_number']} | {podcast['title'][:50]}... | {date_str} |\n"
                )
            f.write("\n")
        else:
            f.write("## ✅ Podcasts con Canciones\n\n")
            f.write("Todos los podcasts tienen canciones.\n\n")

        # Recomendaciones
        f.write("## 💡 Recomendaciones\n\n")

        if results["songs_count_mismatch"]:
            f.write(
                "- **Corregir discrepancias de conteo:** Actualizar web_songs_count o agregar canciones faltantes\n"
            )

        if results["missing_web_songs_count"]:
            f.write(
                "- **Extraer web_songs_count faltantes:** Ejecutar extracción web para obtener el conteo de canciones\n"
            )

        if results["podcasts_without_songs"]:
            f.write(
                "- **Extraer canciones faltantes:** Revisar y extraer playlists de podcasts sin canciones\n"
            )

        if not any(
            [
                results["songs_count_mismatch"],
                results["missing_web_songs_count"],
                results["podcasts_without_songs"],
            ]
        ):
            f.write(
                "- **✅ Base de datos en excelente estado:** No se requieren acciones inmediatas\n"
            )

        f.write("\n---\n")
        f.write("*Informe generado automáticamente por verify_songs_integrity.py*\n")

    print(f"📄 Informe generado: {report_path}")
    return report_path


def main():
    """Función principal"""
    try:
        results = verify_songs_integrity()

        # Mostrar resumen en pantalla
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE INTEGRIDAD DE SONGS")
        print("=" * 60)
        print(f"Total podcasts: {results['total_podcasts']}")
        print(f"Total canciones: {results['total_songs']}")
        print(f"Podcasts con canciones: {results['podcasts_with_songs']}")
        print(f"Podcasts sin canciones: {results['podcasts_without_songs']}")
        print(f"Discrepancias de conteo: {len(results['songs_count_mismatch'])}")
        print(f"Sin web_songs_count: {len(results['missing_web_songs_count'])}")
        print("=" * 60)

        # Mostrar problemas críticos
        if results["songs_count_mismatch"]:
            print(f"\n⚠️ DISCREPANCIAS: {len(results['songs_count_mismatch'])} podcasts")

        if results["podcasts_without_songs"]:
            print(
                f"\n🚫 SIN CANCIONES: {len(results['podcasts_without_songs'])} podcasts"
            )

        if results["missing_web_songs_count"]:
            print(
                f"\n🔍 SIN WEB_SONGS_COUNT: {len(results['missing_web_songs_count'])} podcasts"
            )

        if not any(
            [
                results["songs_count_mismatch"],
                results["missing_web_songs_count"],
                results["podcasts_without_songs"],
            ]
        ):
            print("\n✅ ¡EXCELENTE! La tabla songs está en perfecto estado")

    except Exception as e:
        print(f"❌ Error en la verificación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
