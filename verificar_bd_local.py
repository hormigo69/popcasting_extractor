#!/usr/bin/env python3
"""
Script para verificar el estado de la base de datos local SQLite.
"""

import services.database as local_db


def verificar_bd_local():
    """Verifica el estado de la base de datos local."""
    print("🔍 VERIFICANDO BASE DE DATOS LOCAL")
    print("=" * 50)

    try:
        # Obtener todos los podcasts de la BD local
        local_podcasts = local_db.get_all_podcasts()

        print("📊 ESTADO DE LA BD LOCAL:")
        print(f"   Total episodios: {len(local_podcasts)}")

        # Contar episodios con información web
        con_web = 0
        sin_web = 0

        for p in local_podcasts:
            # Verificar si wordpress_url existe y no es None
            if "wordpress_url" in p and p["wordpress_url"]:
                con_web += 1
            else:
                sin_web += 1

        cobertura = (con_web / len(local_podcasts)) * 100 if local_podcasts else 0

        print(f"   Con información web: {con_web}")
        print(f"   Sin información web: {sin_web}")
        print(f"   Cobertura: {cobertura:.1f}%")

        if cobertura == 100.0:
            print("\n🎉 ¡BD LOCAL COMPLETA!")
            print("   Todos los episodios tienen información web")
        elif cobertura > 90:
            print("\n✅ BD LOCAL CASI COMPLETA")
            print(f"   Solo faltan {sin_web} episodios para el 100%")
        else:
            print("\n⚠️  BD LOCAL INCOMPLETA")
            print(f"   Faltan {sin_web} episodios para completar")

        # Mostrar algunos episodios sin info web si los hay
        if sin_web > 0:
            print("\n📋 EPISODIOS SIN INFO WEB:")
            faltantes = [
                p
                for p in local_podcasts
                if not ("wordpress_url" in p and p["wordpress_url"])
            ]
            for p in faltantes[:10]:  # Mostrar solo los primeros 10
                print(f"   - Episodio #{p['program_number']}")
            if len(faltantes) > 10:
                print(f"   ... y {len(faltantes) - 10} más")

        return con_web, sin_web, cobertura

    except Exception as e:
        print(f"❌ Error verificando BD local: {e}")
        return 0, 0, 0


if __name__ == "__main__":
    verificar_bd_local()
