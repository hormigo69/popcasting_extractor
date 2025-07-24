#!/usr/bin/env python3
"""
Script para corregir canciones en la tabla songs usando el campo web_playlist.
Compara las canciones actuales con el JSON de web_playlist y corrige discrepancias.
"""

import json
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importar los servicios
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.config import DATABASE_TYPE
from services.database import get_db_connection
from services.supabase_database import SupabaseDatabase


def fix_songs_from_web_playlist():
    """Corrige canciones usando web_playlist como fuente de verdad"""

    db_type = DATABASE_TYPE
    print(f"🔧 Corrigiendo canciones usando web_playlist con {db_type}")

    if db_type == "supabase":
        db = SupabaseDatabase()
        results = fix_supabase_songs_from_web_playlist(db)
    else:
        results = fix_sqlite_songs_from_web_playlist()

    # Mostrar resultados
    display_fix_results(results)

    return results


def fix_supabase_songs_from_web_playlist(db):
    """Corrige canciones en Supabase usando web_playlist"""

    results = {
        "total_podcasts": 0,
        "podcasts_with_web_playlist": 0,
        "podcasts_fixed": 0,
        "podcasts_no_changes": 0,
        "podcasts_without_web_playlist": 0,
        "errors": [],
        "fix_details": [],
    }

    try:
        # Obtener todos los podcasts con web_playlist
        response = (
            db.client.table("podcasts")
            .select("id,program_number,title,web_playlist")
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
            title = podcast["title"]
            web_playlist = podcast["web_playlist"]

            try:
                if not web_playlist:
                    results["podcasts_without_web_playlist"] += 1
                    continue

                results["podcasts_with_web_playlist"] += 1

                # Parsear web_playlist JSON
                try:
                    playlist_data = json.loads(web_playlist)
                except json.JSONDecodeError as e:
                    results["errors"].append(
                        {
                            "program_number": program_number,
                            "title": title,
                            "error": f"JSON inválido: {e}",
                        }
                    )
                    continue

                # Obtener canciones actuales del podcast
                songs_response = (
                    db.client.table("songs")
                    .select("id,title,artist,position")
                    .eq("podcast_id", podcast_id)
                    .order("position")
                    .execute()
                )
                current_songs = songs_response.data

                # Comparar y corregir
                fix_result = compare_and_fix_songs(
                    db, podcast_id, program_number, title, current_songs, playlist_data
                )

                if fix_result["fixed"]:
                    results["podcasts_fixed"] += 1
                    results["fix_details"].append(fix_result)
                else:
                    results["podcasts_no_changes"] += 1

            except Exception as e:
                results["errors"].append(
                    {"program_number": program_number, "title": title, "error": str(e)}
                )

        print("✅ Análisis completado")

    except Exception as e:
        print(f"❌ Error al corregir en Supabase: {e}")
        raise

    return results


def fix_sqlite_songs_from_web_playlist():
    """Corrige canciones en SQLite usando web_playlist"""

    results = {
        "total_podcasts": 0,
        "podcasts_with_web_playlist": 0,
        "podcasts_fixed": 0,
        "podcasts_no_changes": 0,
        "podcasts_without_web_playlist": 0,
        "errors": [],
        "fix_details": [],
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener todos los podcasts con web_playlist
        cursor.execute("""
        SELECT id, program_number, title, web_playlist
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
            title = podcast["title"]
            web_playlist = podcast["web_playlist"]

            try:
                if not web_playlist:
                    results["podcasts_without_web_playlist"] += 1
                    continue

                results["podcasts_with_web_playlist"] += 1

                # Parsear web_playlist JSON
                try:
                    playlist_data = json.loads(web_playlist)
                except json.JSONDecodeError as e:
                    results["errors"].append(
                        {
                            "program_number": program_number,
                            "title": title,
                            "error": f"JSON inválido: {e}",
                        }
                    )
                    continue

                # Obtener canciones actuales del podcast
                cursor.execute(
                    """
                SELECT id, title, artist, position
                FROM songs
                WHERE podcast_id = ?
                ORDER BY position
                """,
                    (podcast_id,),
                )
                current_songs = cursor.fetchall()

                # Comparar y corregir
                fix_result = compare_and_fix_songs_sqlite(
                    cursor,
                    podcast_id,
                    program_number,
                    title,
                    current_songs,
                    playlist_data,
                )

                if fix_result["fixed"]:
                    results["podcasts_fixed"] += 1
                    results["fix_details"].append(fix_result)
                else:
                    results["podcasts_no_changes"] += 1

            except Exception as e:
                results["errors"].append(
                    {"program_number": program_number, "title": title, "error": str(e)}
                )

        conn.commit()
        conn.close()
        print("✅ Análisis completado")

    except Exception as e:
        print(f"❌ Error al corregir en SQLite: {e}")
        raise

    return results


def compare_and_fix_songs(
    db, podcast_id, program_number, title, current_songs, playlist_data
):
    """Compara y corrige canciones usando web_playlist"""

    fix_result = {
        "program_number": program_number,
        "title": title,
        "fixed": False,
        "changes": [],
        "current_count": len(current_songs),
        "expected_count": len(playlist_data),
    }

    # Crear diccionarios para comparación
    current_songs_dict = {song["position"]: song for song in current_songs}
    expected_songs_dict = {item["position"]: item for item in playlist_data}

    # Verificar si hay diferencias
    if current_songs_dict == expected_songs_dict:
        return fix_result

    # Hay diferencias, necesitamos corregir
    print(f"🔧 Corrigiendo episodio {program_number}: {title}")

    # Eliminar todas las canciones actuales
    db.client.table("songs").delete().eq("podcast_id", podcast_id).execute()

    # Insertar las canciones correctas desde web_playlist
    for song_data in playlist_data:
        try:
            db.add_song(
                podcast_id=podcast_id,
                title=song_data["title"],
                artist=song_data["artist"],
                position=song_data["position"],
            )
            fix_result["changes"].append(
                f"Agregada: {song_data['artist']} - {song_data['title']}"
            )
        except Exception as e:
            fix_result["changes"].append(
                f"Error al agregar: {song_data['artist']} - {song_data['title']} ({e})"
            )

    fix_result["fixed"] = True
    return fix_result


def compare_and_fix_songs_sqlite(
    cursor, podcast_id, program_number, title, current_songs, playlist_data
):
    """Compara y corrige canciones en SQLite usando web_playlist"""

    fix_result = {
        "program_number": program_number,
        "title": title,
        "fixed": False,
        "changes": [],
        "current_count": len(current_songs),
        "expected_count": len(playlist_data),
    }

    # Crear diccionarios para comparación
    current_songs_dict = {song["position"]: song for song in current_songs}
    expected_songs_dict = {item["position"]: item for item in playlist_data}

    # Verificar si hay diferencias
    if current_songs_dict == expected_songs_dict:
        return fix_result

    # Hay diferencias, necesitamos corregir
    print(f"🔧 Corrigiendo episodio {program_number}: {title}")

    # Eliminar todas las canciones actuales
    cursor.execute("DELETE FROM songs WHERE podcast_id = ?", (podcast_id,))

    # Insertar las canciones correctas desde web_playlist
    for song_data in playlist_data:
        try:
            cursor.execute(
                """
            INSERT INTO songs (podcast_id, title, artist, position)
            VALUES (?, ?, ?, ?)
            """,
                (
                    podcast_id,
                    song_data["title"],
                    song_data["artist"],
                    song_data["position"],
                ),
            )
            fix_result["changes"].append(
                f"Agregada: {song_data['artist']} - {song_data['title']}"
            )
        except Exception as e:
            fix_result["changes"].append(
                f"Error al agregar: {song_data['artist']} - {song_data['title']} ({e})"
            )

    fix_result["fixed"] = True
    return fix_result


def display_fix_results(results):
    """Muestra los resultados de la corrección"""

    print("\n" + "=" * 80)
    print("📊 RESULTADOS DE CORRECCIÓN DE CANCIONES")
    print("=" * 80)
    print(f"Total podcasts analizados: {results['total_podcasts']}")
    print(f"Podcasts con web_playlist: {results['podcasts_with_web_playlist']}")
    print(f"Podcasts corregidos: {results['podcasts_fixed']}")
    print(f"Podcasts sin cambios: {results['podcasts_no_changes']}")
    print(f"Podcasts sin web_playlist: {results['podcasts_without_web_playlist']}")
    print(f"Errores encontrados: {len(results['errors'])}")

    if results["fix_details"]:
        print("\n🔧 Detalles de correcciones:")
        for fix in results["fix_details"]:
            print(f"   Episodio {fix['program_number']}: {fix['title']}")
            print(
                f"     Cambios: {fix['current_count']} → {fix['expected_count']} canciones"
            )
            if fix["changes"]:
                for change in fix["changes"][:3]:  # Mostrar solo los primeros 3 cambios
                    print(f"       {change}")
                if len(fix["changes"]) > 3:
                    print(f"       ... y {len(fix['changes']) - 3} más")
            print()

    if results["errors"]:
        print("\n❌ Errores encontrados:")
        for error in results["errors"][:10]:  # Mostrar solo los primeros 10 errores
            print(f"   Episodio {error['program_number']}: {error['error']}")
        if len(results["errors"]) > 10:
            print(f"   ... y {len(results['errors']) - 10} errores más")

    print("=" * 80)


def main():
    """Función principal"""
    try:
        print("⚠️  ADVERTENCIA: Este script modificará la tabla songs.")
        print("   Se recomienda hacer un backup antes de continuar.")
        response = input("¿Continuar? (y/N): ")

        if response.lower() != "y":
            print("Operación cancelada.")
            return

        fix_songs_from_web_playlist()

    except Exception as e:
        print(f"❌ Error en la corrección: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
