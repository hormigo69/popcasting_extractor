#!/usr/bin/env python3
"""
Script para arreglar automáticamente errores de linting comunes en los archivos de scripts/utils
"""

import re
from pathlib import Path


def fix_import_order(file_path):
    """Arregla el orden de imports moviendo sys.path.insert después de los imports estándar"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Patrón para encontrar imports que están después de sys.path.insert
    pattern = (
        r"(sys\.path\.insert\(.*?\)\s*\n\s*)(from\s+supabase_database\s+import.*?)(\n)"
    )

    if re.search(pattern, content):
        # Mover el import al inicio del archivo
        lines = content.split("\n")
        new_lines = []
        imports_to_move = []
        sys_path_lines = []

        for line in lines:
            if line.strip().startswith("sys.path.insert"):
                sys_path_lines.append(line)
            elif line.strip().startswith("from supabase_database import"):
                imports_to_move.append(line)
            else:
                new_lines.append(line)

        # Reconstruir el archivo con el orden correcto
        fixed_content = "\n".join(
            imports_to_move + [""] + sys_path_lines + [""] + new_lines
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)

        print(f"✅ Arreglado orden de imports en {file_path}")
        return True

    return False


def fix_bare_except(file_path):
    """Arregla los except sin especificar tipo de excepción"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Reemplazar except Exception: por except Exception:
    original_content = content
    content = re.sub(r"(\s+)except:", r"\1except Exception:", content)

    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Arreglado bare except en {file_path}")
        return True

    return False


def main():
    """Función principal que arregla todos los archivos en scripts/utils"""
    scripts_dir = Path(__file__).parent
    files_fixed = 0

    for py_file in scripts_dir.glob("*.py"):
        if py_file.name == __file__:
            continue

        print(f"Procesando {py_file.name}...")
        file_fixed = False

        # Arreglar orden de imports
        if fix_import_order(py_file):
            file_fixed = True

        # Arreglar bare except
        if fix_bare_except(py_file):
            file_fixed = True

        if file_fixed:
            files_fixed += 1

    print(f"\n🎉 Proceso completado. {files_fixed} archivos arreglados.")
    print("Ahora puedes ejecutar: git add . && git commit")


if __name__ == "__main__":
    main()
