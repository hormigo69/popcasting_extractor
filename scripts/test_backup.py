#!/usr/bin/env python3
"""
Script de prueba para verificar que los scripts de backup funcionan correctamente.
"""

import os
import subprocess
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from services.supabase_database import SupabaseDatabase


def test_connection():
    """Prueba la conexión a Supabase."""
    print("🔍 Probando conexión a Supabase...")

    try:
        db = SupabaseDatabase()
        print("✅ Conexión a Supabase exitosa")

        # Probar consulta simple
        response = db.client.table("podcasts").select("id").limit(1).execute()
        print(
            f"✅ Consulta de prueba exitosa: {len(response.data)} registros encontrados"
        )

        return True

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def test_backup_simple():
    """Prueba el script de backup simple."""
    print("\n🔍 Probando script de backup simple...")

    try:
        # Ejecutar script de backup simple
        result = subprocess.run(
            [sys.executable, "scripts/backup_supabase_simple.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            print("✅ Script de backup simple ejecutado exitosamente")
            print("📄 Salida:", result.stdout.strip())
            return True
        else:
            print("❌ Error en script de backup simple:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error ejecutando script: {e}")
        return False


def test_backup_advanced():
    """Prueba el script de backup avanzado."""
    print("\n🔍 Probando script de backup avanzado...")

    try:
        # Ejecutar script de backup avanzado con vista previa
        result = subprocess.run(
            [
                sys.executable,
                "scripts/utils/backup_supabase.py",
                "--output-dir",
                "test_backups",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            print("✅ Script de backup avanzado ejecutado exitosamente")
            return True
        else:
            print("❌ Error en script de backup avanzado:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error ejecutando script: {e}")
        return False


def test_restore_preview():
    """Prueba la vista previa del script de restauración."""
    print("\n🔍 Probando vista previa de restauración...")

    # Buscar el backup más reciente
    backup_dirs = list(Path("backups").glob("backup_*"))
    if not backup_dirs:
        backup_dirs = list(Path("test_backups").glob("backup_*"))

    if not backup_dirs:
        print("⚠️ No se encontraron directorios de backup para probar")
        return True

    latest_backup = max(backup_dirs, key=lambda x: x.stat().st_mtime)

    try:
        # Ejecutar vista previa
        result = subprocess.run(
            [
                sys.executable,
                "scripts/utils/restore_supabase.py",
                str(latest_backup),
                "--preview",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            print(f"✅ Vista previa exitosa para {latest_backup}")
            print("📄 Salida:", result.stdout.strip())
            return True
        else:
            print("❌ Error en vista previa:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error ejecutando vista previa: {e}")
        return False


def check_environment():
    """Verifica que el entorno esté configurado correctamente."""
    print("🔍 Verificando configuración del entorno...")

    # Verificar variables de entorno
    required_vars = ["supabase_project_url", "supabase_api_key"]

    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Configurado")
        else:
            print(f"❌ {var}: No configurado")
            return False

    # Verificar archivos de script
    script_files = [
        "scripts/backup_supabase_simple.py",
        "scripts/utils/backup_supabase.py",
        "scripts/utils/restore_supabase.py",
    ]

    for script in script_files:
        if Path(script).exists():
            print(f"✅ {script}: Existe")
        else:
            print(f"❌ {script}: No existe")
            return False

    return True


def main():
    """Función principal de pruebas."""
    print("🧪 Iniciando pruebas de scripts de backup...\n")

    tests = [
        ("Configuración del entorno", check_environment),
        ("Conexión a Supabase", test_connection),
        ("Script de backup simple", test_backup_simple),
        ("Script de backup avanzado", test_backup_advanced),
        ("Vista previa de restauración", test_restore_preview),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"PRUEBA: {test_name}")
        print(f"{'='*50}")

        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            results.append((test_name, False))

    # Resumen final
    print(f"\n{'='*50}")
    print("RESUMEN DE PRUEBAS")
    print(f"{'='*50}")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASÓ" if success else "❌ FALLÓ"
        print(f"{status} {test_name}")

    print(f"\n📊 Resultado: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! Los scripts están listos para usar.")
        return 0
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return 1


if __name__ == "__main__":
    exit(main())
