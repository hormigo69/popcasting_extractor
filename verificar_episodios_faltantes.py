#!/usr/bin/env python3
"""
Script para verificar el estado actual de los episodios faltantes.
Muestra estadísticas detalladas y lista los episodios que aún necesitan información web.
"""

from services import database as db


def verificar_estado_actual():
    """
    Verifica el estado actual de la base de datos.
    """
    db.initialize_database()
    conn = db.get_db_connection()
    cursor = conn.cursor()

    # Estadísticas generales
    cursor.execute("SELECT COUNT(*) as total FROM podcasts")
    total = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) as with_web FROM podcasts WHERE wordpress_url IS NOT NULL"
    )
    with_web = cursor.fetchone()["with_web"]

    cursor.execute(
        "SELECT COUNT(*) as with_cover FROM podcasts WHERE cover_image_url IS NOT NULL"
    )
    with_cover = cursor.fetchone()["with_cover"]

    cursor.execute(
        "SELECT COUNT(*) as without_web FROM podcasts WHERE wordpress_url IS NULL"
    )
    without_web = cursor.fetchone()["without_web"]

    conn.close()

    print("📊 ESTADO ACTUAL DE LA BASE DE DATOS")
    print("=" * 50)
    print(f"Total episodios: {total}")
    print(f"Con información web: {with_web}")
    print(f"Con imagen de portada: {with_cover}")
    print(f"Sin información web: {without_web}")
    print(f"Porcentaje de éxito: {with_web/total*100:.1f}%")
    print(f"Porcentaje faltante: {without_web/total*100:.1f}%")

    return {
        "total": total,
        "with_web": with_web,
        "with_cover": with_cover,
        "without_web": without_web,
    }


def listar_episodios_faltantes():
    """
    Lista todos los episodios que aún no tienen información web.
    """
    conn = db.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, date, program_number, wordpress_url, last_web_check
        FROM podcasts
        WHERE wordpress_url IS NULL OR last_web_check IS NULL
        ORDER BY date DESC
    """)

    episodios_faltantes = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if not episodios_faltantes:
        print("\n🎉 ¡Todos los episodios tienen información web!")
        return []

    print(f"\n📋 EPISODIOS SIN INFORMACIÓN WEB ({len(episodios_faltantes)} total)")
    print("=" * 80)

    # Agrupar por año
    episodios_por_ano = {}
    for episodio in episodios_faltantes:
        ano = episodio["date"][:4]
        if ano not in episodios_por_ano:
            episodios_por_ano[ano] = []
        episodios_por_ano[ano].append(episodio)

    # Mostrar por año
    for ano in sorted(episodios_por_ano.keys(), reverse=True):
        episodios_ano = episodios_por_ano[ano]
        print(f"\n📅 {ano} ({len(episodios_ano)} episodios):")
        print("-" * 40)

        for episodio in episodios_ano:
            print(
                f"  ID: {episodio['id']:3d} | #{episodio['program_number']:6s} | {episodio['date']} | {episodio['title'][:50]}..."
            )

    return episodios_faltantes


def generar_archivo_actualizado():
    """
    Genera un archivo actualizado con los episodios que aún faltan.
    """
    episodios_faltantes = listar_episodios_faltantes()

    if not episodios_faltantes:
        print("\n✅ No hay episodios faltantes para generar archivo")
        return

    # Crear archivo actualizado
    with open("episodios_faltantes_actualizado.txt", "w", encoding="utf-8") as f:
        f.write("# EPISODIOS FALTANTES - ACTUALIZADO\n")
        f.write("# ======================================\n")
        f.write(
            f"# Generado automáticamente - {len(episodios_faltantes)} episodios faltantes\n"
        )
        f.write("# ======================================\n\n")

        # Agrupar por año
        episodios_por_ano = {}
        for episodio in episodios_faltantes:
            ano = episodio["date"][:4]
            if ano not in episodios_por_ano:
                episodios_por_ano[ano] = []
            episodios_por_ano[ano].append(episodio)

        for ano in sorted(episodios_por_ano.keys(), reverse=True):
            episodios_ano = episodios_por_ano[ano]
            f.write(f"# EPISODIOS {ano}\n")
            f.write("# " + "=" * 20 + "\n")

            for episodio in episodios_ano:
                f.write(
                    f"ID: {episodio['id']} | Número: {episodio['program_number']} | Fecha: {episodio['date']} | Título: {episodio['title']} | URL_MANUAL: \n"
                )

            f.write("\n")

        f.write("# ======================================\n")
        f.write("# INSTRUCCIONES:\n")
        f.write("# 1. Busca cada episodio en https://popcastingpop.com\n")
        f.write("# 2. Copia la URL de la página del episodio\n")
        f.write("# 3. Pégala en la columna URL_MANUAL\n")
        f.write("# 4. Ejecuta: python completar_episodios_faltantes.py\n")
        f.write("# ======================================\n")

    print("\n📄 Archivo generado: episodios_faltantes_actualizado.txt")
    print("💡 Edita este archivo y añade las URLs manuales encontradas")


def main():
    print("🔍 VERIFICACIÓN DE EPISODIOS FALTANTES")
    print("=" * 50)

    # Verificar estado actual
    verificar_estado_actual()

    # Listar episodios faltantes
    episodios_faltantes = listar_episodios_faltantes()

    if episodios_faltantes:
        # Generar archivo actualizado
        generar_archivo_actualizado()

        print("\n💡 PRÓXIMOS PASOS:")
        print("1. Revisa el archivo episodios_faltantes_actualizado.txt")
        print("2. Busca las URLs manualmente en https://popcastingpop.com")
        print("3. Añade las URLs encontradas al archivo")
        print("4. Ejecuta: python completar_episodios_faltantes.py")
    else:
        print("\n🎉 ¡Sistema completo! Todos los episodios tienen información web.")


if __name__ == "__main__":
    main()
