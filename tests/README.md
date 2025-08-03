# Tests del Extractor de WordPress

Este directorio contiene archivos de prueba y utilidades para el extractor de WordPress.

## Archivos de Test

- `test_main.py` - Prueba del extractor principal

## Archivos de Utilidad

- `setup_synology_env.py` - Script para configurar variables de entorno de Synology
- `synology.env.example` - Ejemplo de configuración para Synology
- `example_usage.py` - Ejemplo de uso general del sistema

## Uso

Para ejecutar los tests, desde el directorio raíz del proyecto:

```bash
# Activar el entorno virtual
source .venv/bin/activate

# Ejecutar test principal
python tests/test_main.py

# Configurar variables de Synology
python tests/setup_synology_env.py
```

## Convenciones

- Todos los archivos de test deben empezar con `test_`
- Usar nombres descriptivos que indiquen qué se está probando
- Mantener los tests simples y enfocados
- Documentar cualquier configuración especial necesaria

## Limpieza Realizada

Se han eliminado los siguientes archivos obsoletos:
- Tests con referencias rotas a módulos RSS
- Tests redundantes de AudioManager
- Ejemplos con importaciones obsoletas 