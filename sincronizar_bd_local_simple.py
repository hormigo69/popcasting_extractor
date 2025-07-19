#!/usr/bin/env python3
"""
Script simple para sincronizar la base de datos local con Supabase.
"""

import services.database as local_db
from services.supabase_database import SupabaseDatabase


def sincronizar_bd_local_simple():
    """Sincroniza la base de datos local con Supabase de forma simple."""
    print("🔄 SINCRONIZACIÓN SIMPLE BD LOCAL ↔️ SUPABASE")
    print("=" * 60)

    # Conectar a Supabase
    supabase_db = SupabaseDatabase()

    try:
        # Obtener todos los podcasts de ambas BD
        print("📥 Obteniendo datos...")
        supabase_podcasts = supabase_db.get_all_podcasts()
        local_podcasts = local_db.get_all_podcasts()

        print(f"   Supabase: {len(supabase_podcasts)} episodios")
        print(f"   Local: {len(local_podcasts)} episodios")

        # Crear diccionario de episodios locales por número
        local_dict = {p["program_number"]: p for p in local_podcasts}

        # Contadores
        actualizados = 0
        no_encontrados = 0

        print("\n🔄 ACTUALIZANDO EPISODIOS")
        print("-" * 40)

        for supabase_podcast in supabase_podcasts:
            program_number = supabase_podcast.get("program_number")

            # Buscar en BD local
            if program_number in local_dict:
                local_podcast = local_dict[program_number]

                # Obtener datos de Supabase
                wordpress_url = supabase_podcast.get("wordpress_url")
                cover_image_url = supabase_podcast.get("cover_image_url")
                extra_links = supabase_podcast.get("extra_links")
                playlist = supabase_podcast.get("playlist")

                # Actualizar en BD local
                try:
                    local_db.update_web_info(
                        local_podcast["id"],
                        wordpress_url,
                        cover_image_url,
                        extra_links,
                        playlist,
                    )

                    print(f"  ✅ Episodio #{program_number} actualizado")
                    actualizados += 1

                except Exception as e:
                    print(f"  ❌ Error actualizando #{program_number}: {e}")
            else:
                no_encontrados += 1
                if no_encontrados <= 5:  # Mostrar solo los primeros 5
                    print(f"  ⚠️  Episodio #{program_number} no encontrado en BD local")

        if no_encontrados > 5:
            print(f"  ... y {no_encontrados - 5} episodios más no encontrados")

        print("\n📊 RESUMEN")
        print("-" * 20)
        print(f"Episodios actualizados: {actualizados}")
        print(f"Episodios no encontrados: {no_encontrados}")

        # Verificar estado final
        verificar_estado_final()

        return actualizados

    except Exception as e:
        print(f"❌ Error en sincronización: {e}")
        return 0


def verificar_estado_final():
    """Verifica el estado final de la BD local."""
    print("\n🔍 VERIFICANDO ESTADO FINAL")
    print("=" * 40)

    try:
        local_podcasts = local_db.get_all_podcasts()

        # Contar episodios con información web
        con_web = 0
        sin_web = 0

        for p in local_podcasts:
            if "wordpress_url" in p and p["wordpress_url"]:
                con_web += 1
            else:
                sin_web += 1

        cobertura = (con_web / len(local_podcasts)) * 100 if local_podcasts else 0

        print("📊 BD LOCAL:")
        print(f"   Total: {len(local_podcasts)}")
        print(f"   Con web: {con_web}")
        print(f"   Sin web: {sin_web}")
        print(f"   Cobertura: {cobertura:.1f}%")

        if cobertura == 100.0:
            print("\n🎉 ¡BD LOCAL COMPLETA!")
        elif cobertura > 90:
            print("\n✅ BD LOCAL CASI COMPLETA")
        else:
            print("\n⚠️  BD LOCAL INCOMPLETA")

    except Exception as e:
        print(f"❌ Error verificando estado final: {e}")


if __name__ == "__main__":
    print("🚀 INICIANDO SINCRONIZACIÓN SIMPLE")
    print("=" * 60)

    actualizados = sincronizar_bd_local_simple()

    print("\n" + "=" * 60)
    if actualizados > 0:
        print("🎯 SINCRONIZACIÓN COMPLETADA")
        print(f"   {actualizados} episodios actualizados")
    else:
        print("⚠️  SINCRONIZACIÓN FALLIDA")
    print("=" * 60)
