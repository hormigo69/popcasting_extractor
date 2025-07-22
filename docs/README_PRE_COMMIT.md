# Configuración de Pre-commit para Popcasting Extractor

## 📋 Resumen

Este proyecto tiene configurado un sistema de pre-commit inteligente que te ayuda a mantener la calidad del código sin interrumpir tu flujo de trabajo.

## 🚀 Uso Rápido

### Commit Normal (Recomendado)
```bash
python scripts/utils/smart_commit.py "tu mensaje de commit"
```

### Commit Sin Linting (Para emergencias)
```bash
python scripts/utils/smart_commit.py "tu mensaje de commit" --no-lint
```

### Commit Manual (Git tradicional)
```bash
git add .
git commit -m "tu mensaje"
```

## 🔧 Scripts Disponibles

### 1. `smart_commit.py` - Commit Inteligente
- **Uso**: `python scripts/utils/smart_commit.py "mensaje" [--no-lint]`
- **Función**: Hace commit automáticamente, si falla el linting, lo intenta sin linting
- **Ventaja**: No te bloquea si hay errores menores de linting

### 2. `commit_without_linting.py` - Commit Sin Linting
- **Uso**: `python scripts/utils/commit_without_linting.py "mensaje"`
- **Función**: Hace commit saltándose completamente los hooks de pre-commit
- **Uso**: Solo para emergencias o cuando necesitas hacer commit rápido

### 3. `fix_all_linting.py` - Arreglar Linting
- **Uso**: `python scripts/utils/fix_all_linting.py`
- **Función**: Arregla automáticamente errores comunes de linting
- **Uso**: Antes de hacer commit para limpiar el código

### 4. `fix_syntax_errors.py` - Arreglar Errores de Sintaxis
- **Uso**: `python scripts/utils/fix_syntax_errors.py`
- **Función**: Arregla errores de sintaxis específicos
- **Uso**: Cuando hay errores de sintaxis que impiden el commit

## ⚙️ Configuración de Pre-commit

### Archivo: `.pre-commit-config.yaml`
```yaml
repos:
-   repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.2
    hooks:
    -   id: ruff
        args: [--fix, --unsafe-fixes]
        files: ^scripts/utils/.*\.py$
    -   id: ruff-format
        files: ^scripts/utils/.*\.py$
```

### Características:
- ✅ Solo verifica archivos en `scripts/utils/`
- ✅ Arregla automáticamente errores que puede arreglar
- ✅ Formatea código automáticamente
- ✅ No bloquea commits por errores menores

## 🛠️ Instalación y Configuración

### Instalar Pre-commit
```bash
pip install pre-commit
```

### Configurar el Proyecto
```bash
python scripts/utils/setup_smart_precommit.py
```

### Instalar Hooks Manualmente
```bash
pre-commit install
```

## 📝 Flujo de Trabajo Recomendado

### 1. Desarrollo Normal
```bash
# Hacer cambios en tu código
# ...

# Commit inteligente (recomendado)
python scripts/utils/smart_commit.py "Agregar nueva funcionalidad"
```

### 2. Si Hay Errores de Linting
```bash
# Arreglar errores automáticamente
python scripts/utils/fix_all_linting.py

# Intentar commit nuevamente
python scripts/utils/smart_commit.py "Arreglar linting"
```

### 3. Si Hay Errores de Sintaxis
```bash
# Arreglar errores de sintaxis
python scripts/utils/fix_syntax_errors.py

# Intentar commit nuevamente
python scripts/utils/smart_commit.py "Arreglar sintaxis"
```

### 4. Emergencia (Commit Rápido)
```bash
# Commit sin linting
python scripts/utils/smart_commit.py "Fix urgente" --no-lint
```

## 🚨 Errores Comunes y Soluciones

### Error: "Found X errors"
- **Solución**: Ejecuta `python scripts/utils/fix_all_linting.py`
- **Alternativa**: Usa `--no-lint` en el commit

### Error: "SyntaxError"
- **Solución**: Ejecuta `python scripts/utils/fix_syntax_errors.py`
- **Verificación**: Revisa el archivo manualmente

### Error: "pre-commit not found"
- **Solución**: `pip install pre-commit`
- **Alternativa**: Usa `python scripts/utils/commit_without_linting.py`

## 🎯 Beneficios

1. **No te bloquea**: El sistema es inteligente y no te impide hacer commits
2. **Arregla automáticamente**: Muchos errores se arreglan solos
3. **Mantiene calidad**: Asegura que el código esté bien formateado
4. **Fácil de usar**: Un solo comando para hacer commit
5. **Flexible**: Opciones para diferentes situaciones

## 📞 Comandos de Emergencia

Si todo falla, siempre puedes usar:
```bash
git add .
git commit --no-verify -m "tu mensaje"
```

## 🔄 Actualizar Configuración

Para actualizar la configuración de pre-commit:
```bash
python scripts/utils/setup_smart_precommit.py
```

---

**💡 Consejo**: Usa `python scripts/utils/smart_commit.py` como tu comando de commit principal. Es la forma más fácil y segura de hacer commits en este proyecto. 