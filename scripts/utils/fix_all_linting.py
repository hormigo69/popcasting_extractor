#!/usr/bin/env python3
"""
import os
import re
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


Script avanzado para arreglar automáticamente todos los errores de linting
"""


def fix_file_imports(file_path):
    """Arregla completamente el orden de imports en un archivo"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Separar el contenido en secciones
    lines = content.split("\n")

    # Encontrar dónde empieza el código real (después de docstrings)
    code_start = 0
    for i, line in enumerate(lines):
        if (
            line.strip()
            and not line.strip().startswith('"""')
            and not line.strip().startswith("'''")
        ):
            if not line.strip().startswith("#"):
                code_start = i
                break

    # Extraer docstring y comentarios iniciales
    header = lines[:code_start]
    code_lines = lines[code_start:]

    # Separar imports de otras líneas
    imports = []
    sys_path_lines = []
    other_lines = []

    for line in code_lines:
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            imports.append(line)
        elif stripped.startswith("sys.path.insert"):
            sys_path_lines.append(line)
        else:
            other_lines.append(line)

    # Reconstruir el archivo con el orden correcto
    new_content = []

    # 1. Header (docstring y comentarios)
    new_content.extend(header)
    if header and not header[-1].strip():
        new_content.append("")

    # 2. Imports estándar
    if imports:
        new_content.extend(imports)
        new_content.append("")

    # 3. sys.path.insert
    if sys_path_lines:
        new_content.extend(sys_path_lines)
        new_content.append("")

    # 4. Resto del código
    new_content.extend(other_lines)

    # Escribir el archivo
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_content))

    return len(imports) > 0 or len(sys_path_lines) > 0


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
        return True

    return False


def fix_unused_imports(file_path):
    """Elimina imports no utilizados"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Lista de imports comunes que podrían no estar siendo usados
    common_unused = [
        "import os",
        "import time",
        "import datetime",
        "from datetime import datetime",
        "from datetime import date",
    ]

    lines = content.split("\n")
    new_lines = []
    removed_count = 0

    for line in lines:
        should_keep = True
        for unused_import in common_unused:
            if line.strip() == unused_import:
                # Verificar si realmente se usa
                if unused_import not in content.replace(line, "", 1):
                    should_keep = False
                    removed_count += 1
                    break

        if should_keep:
            new_lines.append(line)

    if removed_count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        return True

    return False


def main():
    """Función principal que arregla todos los archivos"""
    scripts_dir = Path(__file__).parent
    files_fixed = 0

    print("🔧 Arreglando errores de linting...")

    for py_file in scripts_dir.glob("*.py"):
        if py_file.name in [__file__, "fix_linting_errors.py"]:
            continue

        print(f"  Procesando {py_file.name}...")
        file_fixed = False

        # Arreglar orden de imports
        if fix_file_imports(py_file):
            file_fixed = True

        # Arreglar bare except
        if fix_bare_except(py_file):
            file_fixed = True

        # Eliminar imports no utilizados
        if fix_unused_imports(py_file):
            file_fixed = True

        if file_fixed:
            files_fixed += 1
            print("    ✅ Arreglado")
        else:
            print("    ⏭️  Sin cambios necesarios")

    print(f"\n🎉 Proceso completado. {files_fixed} archivos arreglados.")
    print("\n📝 Ahora ejecuta:")
    print("   git add .")
    print("   git commit -m 'Arreglar errores de linting'")


if __name__ == "__main__":
    main()
