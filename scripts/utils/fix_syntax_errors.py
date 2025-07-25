#!/usr/bin/env python3
"""
Script para arreglar errores de sintaxis específicos
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def fix_find_single_song_episodes(file_path):
    """Arregla el error de sintaxis en find_single_song_episodes.py"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # El problema está en la línea 5 con indentación incorrecta
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        if i == 4:  # Línea 5 (índice 4)
            # Arreglar la indentación incorrecta
            if line.strip().startswith("import json"):
                fixed_lines.append("import json")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(fixed_lines))

    return True


def fix_web_extractor(file_path):
    """Arregla el error de sintaxis en web_extractor.py"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # El problema está en el try sin contenido
    content = content.replace(
        "try:\nexcept ImportError:", "try:\n    pass\nexcept ImportError:"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True


def fix_web_report(file_path):
    """Arregla el error de sintaxis en web_report.py"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # El problema está en el try sin contenido
    content = content.replace(
        "try:\nexcept ImportError:", "try:\n    pass\nexcept ImportError:"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True


def fix_missing_imports(file_path):
    """Agrega imports faltantes al inicio del archivo"""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Detectar qué imports faltan
    missing_imports = []

    if "re." in content and "import re" not in content:
        missing_imports.append("import re")

    if "json." in content and "import json" not in content:
        missing_imports.append("import json")

    if "datetime." in content and "from datetime import datetime" not in content:
        missing_imports.append("from datetime import datetime")

    if "Path(" in content and "from pathlib import Path" not in content:
        missing_imports.append("from pathlib import Path")

    if "load_dotenv()" in content and "from dotenv import load_dotenv" not in content:
        missing_imports.append("from dotenv import load_dotenv")

    if "sys." in content and "import sys" not in content:
        missing_imports.append("import sys")

    if missing_imports:
        lines = content.split("\n")

        # Encontrar dónde insertar los imports
        insert_pos = 0
        for i, line in enumerate(lines):
            if (
                line.strip()
                and not line.strip().startswith('"""')
                and not line.strip().startswith("'''")
            ):
                if not line.strip().startswith("#"):
                    insert_pos = i
                    break

        # Insertar imports faltantes
        new_lines = lines[:insert_pos] + missing_imports + [""] + lines[insert_pos:]

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))

        return True

    return False


def main():
    """Función principal"""
    scripts_dir = Path(__file__).parent
    files_fixed = 0

    print("🔧 Arreglando errores de sintaxis...")

    # Arreglar archivos específicos con errores de sintaxis
    specific_files = {
        "find_single_song_episodes.py": fix_find_single_song_episodes,
        "web_extractor.py": fix_web_extractor,
        "web_report.py": fix_web_report,
    }

    for filename, fix_func in specific_files.items():
        file_path = scripts_dir / filename
        if file_path.exists():
            print(f"  Arreglando {filename}...")
            if fix_func(file_path):
                files_fixed += 1
                print("    ✅ Arreglado")

    # Arreglar imports faltantes en todos los archivos
    print("\n📦 Arreglando imports faltantes...")
    for py_file in scripts_dir.glob("*.py"):
        if py_file.name in [__file__, "fix_linting_errors.py", "fix_all_linting.py"]:
            continue

        if fix_missing_imports(py_file):
            print(f"  ✅ Imports arreglados en {py_file.name}")
            files_fixed += 1

    print(f"\n🎉 Proceso completado. {files_fixed} archivos arreglados.")


if __name__ == "__main__":
    main()
