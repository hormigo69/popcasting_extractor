#!/usr/bin/env python3
"""
Script para sincronizar la base de datos local SQLite con Supabase.
Actualiza toda la información web de los episodios en la BD local.
"""

import services.database as local_db
from services.supabase_database import SupabaseDatabase


def sincronizar_bd_local():
    """Sincroniza la base de datos local con Supabase."""
    print("🔄 SINCRONIZANDO BASE DE DATOS LOCAL CON SUPABASE")
    print("=" * 60)

    # Conectar a Supabase
    supabase_db = SupabaseDatabase()

    try:
        # Obtener todos los podcasts de Supabase
        print("📥 Obteniendo datos de Supabase...")
        supabase_podcasts = supabase_db.get_all_podcasts()

        print(f"   Encontrados {len(supabase_podcasts)} episodios en Supabase")

        # Contadores
        actualizados = 0
        errores = 0

        print("\n🔄 ACTUALIZANDO BASE DE DATOS LOCAL")
        print("-" * 40)

        for podcast in supabase_podcasts:
            try:
                program_number = podcast.get("program_number")
                wordpress_url = podcast.get("wordpress_url")
                cover_image_url = podcast.get("cover_image_url")
                extra_links = podcast.get("extra_links")
                playlist = podcast.get("playlist")

                # Buscar episodio en BD local por número de programa
                local_podcasts = local_db.get_all_podcasts()
                local_podcast = None

                for p in local_podcasts:
                    # Acceder a las columnas usando corchetes para sqlite3.Row
                    if p["program_number"] == program_number:
                        local_podcast = p
                        break

                if local_podcast:
                    # Actualizar información web en BD local
                    local_db.update_web_info(
                        local_podcast["id"],
                        wordpress_url,
                        cover_image_url,
                        extra_links,
                        playlist,
                    )

                    print(f"  ✅ Episodio #{program_number} sincronizado")
                    actualizados += 1
                else:
                    print(f"  ⚠️  Episodio #{program_number} no encontrado en BD local")

            except Exception as e:
                print(f"  ❌ Error sincronizando episodio #{program_number}: {e}")
                errores += 1

        print("\n📊 RESUMEN DE SINCRONIZACIÓN")
        print("-" * 30)
        print(f"Episodios actualizados: {actualizados}")
        print(f"Errores: {errores}")

        # Verificar estado final
        verificar_estado_final(supabase_db)

        return actualizados, errores

    except Exception as e:
        print(f"❌ Error general en sincronización: {e}")
        return 0, 1


def verificar_estado_final(supabase_db):
    """Verifica el estado final de ambas bases de datos."""
    print("\n🔍 VERIFICANDO ESTADO FINAL")
    print("=" * 40)

    # Obtener estadísticas de ambas BD
    local_podcasts = local_db.get_all_podcasts()
    supabase_podcasts = supabase_db.get_all_podcasts()

    # Estadísticas locales
    local_total = len(local_podcasts)
    local_con_web = sum(1 for p in local_podcasts if p["wordpress_url"])
    local_cobertura = (local_con_web / local_total) * 100 if local_total > 0 else 0

    # Estadísticas Supabase
    supabase_total = len(supabase_podcasts)
    supabase_con_web = sum(1 for p in supabase_podcasts if p.get("wordpress_url"))
    supabase_cobertura = (
        (supabase_con_web / supabase_total) * 100 if supabase_total > 0 else 0
    )

    print("📊 COMPARACIÓN:")
    print("   BD Local:")
    print(f"     - Total: {local_total}")
    print(f"     - Con web: {local_con_web}")
    print(f"     - Cobertura: {local_cobertura:.1f}%")
    print("   BD Supabase:")
    print(f"     - Total: {supabase_total}")
    print(f"     - Con web: {supabase_con_web}")
    print(f"     - Cobertura: {supabase_cobertura:.1f}%")

    if local_cobertura == supabase_cobertura and local_cobertura == 100.0:
        print("\n🎉 ¡SINCRONIZACIÓN EXITOSA!")
        print("   Ambas bases de datos tienen 100% de cobertura")
    elif local_cobertura == supabase_cobertura:
        print("\n✅ Sincronización completada")
        print(f"   Ambas BD tienen la misma cobertura: {local_cobertura:.1f}%")
    else:
        print("\n⚠️  Diferencias detectadas")
        print(
            f"   Local: {local_cobertura:.1f}% vs Supabase: {supabase_cobertura:.1f}%"
        )


def mostrar_episodios_faltantes_local():
    """Muestra episodios sin información web en la BD local."""
    print("\n🔍 EPISODIOS SIN INFO WEB EN BD LOCAL")
    print("-" * 40)

    local_podcasts = local_db.get_all_podcasts()
    faltantes = [p for p in local_podcasts if not p["wordpress_url"]]

    if faltantes:
        print(f"Encontrados {len(faltantes)} episodios sin información web:")
        for p in faltantes[:10]:  # Mostrar solo los primeros 10
            print(f"  - Episodio #{p['program_number']}")
        if len(faltantes) > 10:
            print(f"  ... y {len(faltantes) - 10} más")
    else:
        print("✅ Todos los episodios tienen información web")


if __name__ == "__main__":
    print("🚀 INICIANDO SINCRONIZACIÓN BD LOCAL ↔️ SUPABASE")
    print("=" * 60)

    # Ejecutar sincronización
    actualizados, errores = sincronizar_bd_local()

    print("\n" + "=" * 60)
    if errores == 0:
        print("🎯 SINCRONIZACIÓN COMPLETADA EXITOSAMENTE")
        print(f"   {actualizados} episodios actualizados")
        print("   Base de datos local sincronizada con Supabase")
    else:
        print("⚠️  SINCRONIZACIÓN COMPLETADA CON ERRORES")
        print(f"   {actualizados} episodios actualizados")
        print(f"   {errores} errores encontrados")
    print("=" * 60)
