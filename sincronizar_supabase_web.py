#!/usr/bin/env python3
"""
Script para sincronizar la información web de SQLite a Supabase.
Actualiza todos los episodios en Supabase con la información web extraída.
"""

from services import database as sqlite_db
from services.supabase_database import SupabaseDatabase


def sincronizar_informacion_web():
    """
    Sincroniza la información web de SQLite a Supabase.
    """
    print("🔄 Sincronizando información web de SQLite a Supabase")
    print("=" * 60)

    # Inicializar bases de datos
    sqlite_db.initialize_database()
    supabase_db = SupabaseDatabase()

    # Obtener todos los episodios de SQLite con información web
    conn = sqlite_db.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, wordpress_url, cover_image_url, web_extra_links, web_playlist, last_web_check
        FROM podcasts
        WHERE wordpress_url IS NOT NULL
    """)

    episodios_con_web = [dict(row) for row in cursor.fetchall()]
    conn.close()

    print(
        f"📊 Encontrados {len(episodios_con_web)} episodios con información web en SQLite"
    )

    # Obtener episodios de Supabase para mapear IDs
    episodios_supabase = supabase_db.get_all_podcasts()
    mapeo_ids = {}

    for episodio in episodios_supabase:
        # Mapear por fecha y número de programa
        key = (episodio["date"], episodio["program_number"])
        mapeo_ids[key] = episodio["id"]

    print(f"📊 Encontrados {len(episodios_supabase)} episodios en Supabase")

    # Sincronizar información web
    actualizados = 0
    errores = 0

    for episodio_sqlite in episodios_con_web:
        try:
            # Obtener información del episodio para mapear
            conn = sqlite_db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT date, program_number FROM podcasts WHERE id = ?",
                (episodio_sqlite["id"],),
            )
            info_episodio = cursor.fetchone()
            conn.close()

            if not info_episodio:
                print(
                    f"⚠️  No se encontró información del episodio SQLite ID {episodio_sqlite['id']}"
                )
                errores += 1
                continue

            fecha = info_episodio["date"]
            numero = info_episodio["program_number"]

            # Buscar ID correspondiente en Supabase
            if (fecha, numero) in mapeo_ids:
                supabase_id = mapeo_ids[(fecha, numero)]

                # Actualizar información web en Supabase
                supabase_db.update_web_info(
                    podcast_id=supabase_id,
                    wordpress_url=episodio_sqlite["wordpress_url"],
                    cover_image_url=episodio_sqlite["cover_image_url"],
                    web_extra_links=episodio_sqlite["web_extra_links"],
                    web_playlist=episodio_sqlite["web_playlist"],
                )

                print(
                    f"✅ Actualizado episodio {numero} ({fecha}) - ID Supabase: {supabase_id}"
                )
                actualizados += 1
            else:
                print(f"⚠️  No se encontró episodio {numero} ({fecha}) en Supabase")
                errores += 1

        except Exception as e:
            print(f"❌ Error actualizando episodio {episodio_sqlite['id']}: {e}")
            errores += 1
            continue

    # Estadísticas finales
    print("\n🎉 Sincronización completada!")
    print("=" * 60)
    print("📊 Estadísticas:")
    print(f"   Episodios procesados: {len(episodios_con_web)}")
    print(f"   ✅ Actualizados: {actualizados}")
    print(f"   ❌ Errores: {errores}")
    print(f"   📈 Tasa de éxito: {actualizados/len(episodios_con_web)*100:.1f}%")

    # Verificar estado final de Supabase
    episodios_supabase_final = supabase_db.get_all_podcasts()
    total_supabase = len(episodios_supabase_final)
    con_web_supabase = len(
        [p for p in episodios_supabase_final if p.get("wordpress_url")]
    )

    print("\n💾 Estado final de Supabase:")
    print(f"   Total episodios: {total_supabase}")
    print(f"   Con información web: {con_web_supabase}")
    print(f"   Porcentaje: {con_web_supabase/total_supabase*100:.1f}%")


def verificar_estado_actual():
    """
    Verifica el estado actual de ambas bases de datos.
    """
    print("🔍 VERIFICACIÓN DE ESTADO ACTUAL")
    print("=" * 50)

    # SQLite
    sqlite_db.initialize_database()
    conn = sqlite_db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM podcasts")
    total_sqlite = cursor.fetchone()["total"]
    cursor.execute(
        "SELECT COUNT(*) as with_web FROM podcasts WHERE wordpress_url IS NOT NULL"
    )
    with_web_sqlite = cursor.fetchone()["with_web"]
    conn.close()

    # Supabase
    supabase_db = SupabaseDatabase()
    episodios_supabase = supabase_db.get_all_podcasts()
    total_supabase = len(episodios_supabase)
    with_web_supabase = len([p for p in episodios_supabase if p.get("wordpress_url")])

    print("📊 SQLite:")
    print(f"   Total episodios: {total_sqlite}")
    print(f"   Con información web: {with_web_sqlite}")
    print(f"   Porcentaje: {with_web_sqlite/total_sqlite*100:.1f}%")

    print("\n📊 Supabase:")
    print(f"   Total episodios: {total_supabase}")
    print(f"   Con información web: {with_web_supabase}")
    print(f"   Porcentaje: {with_web_supabase/total_supabase*100:.1f}%")

    print("\n📈 Diferencia:")
    print(f"   Episodios por sincronizar: {with_web_sqlite - with_web_supabase}")


def main():
    print("🔄 SINCRONIZACIÓN SQLITE → SUPABASE")
    print("=" * 60)

    # Verificar estado actual
    verificar_estado_actual()

    print("\n" + "=" * 60)
    print("🚀 Iniciando sincronización automática...")

    # Ejecutar sincronización directamente
    sincronizar_informacion_web()


if __name__ == "__main__":
    main()
