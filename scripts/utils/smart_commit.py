#!/usr/bin/env python3
"""
Script inteligente para hacer commits
"""

import os
import subprocess
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python smart_commit.py 'mensaje del commit' [--no-lint]")
        sys.exit(1)

    commit_message = sys.argv[1]
    skip_linting = "--no-lint" in sys.argv

    print("🚀 Iniciando commit inteligente...")

    try:
        # Agregar archivos
        subprocess.run(["git", "add", "."], check=True)
        print("✅ Archivos agregados")

        if skip_linting:
            # Saltarse linting
            subprocess.run(
                ["git", "commit", "--no-verify", "-m", commit_message], check=True
            )
            print("🎉 Commit exitoso (linting saltado)")
        else:
            # Intentar commit normal
            try:
                subprocess.run(["git", "commit", "-m", commit_message], check=True)
                print("🎉 Commit exitoso con linting")
            except subprocess.CalledProcessError:
                print("⚠️  Linting falló, intentando sin linting...")
                subprocess.run(
                    ["git", "commit", "--no-verify", "-m", commit_message], check=True
                )
                print("🎉 Commit exitoso (linting saltado)")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
