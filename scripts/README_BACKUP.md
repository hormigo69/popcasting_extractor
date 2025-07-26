# Script de Backup de Supabase

## Descripción

Script simplificado para hacer backup de la base de datos Supabase. Utiliza el `DatabaseManager` interno del sincronizador_rss y solo depende de componentes internos del proyecto.

## Características

- ✅ **Solo dependencias internas**: No depende de servicios externos
- ✅ **Paginación automática**: Maneja tablas grandes sin problemas
- ✅ **Múltiples formatos**: Exporta a JSON y CSV
- ✅ **Configuración flexible**: Permite especificar tablas y directorio de salida
- ✅ **Logging detallado**: Información completa del proceso
- ✅ **Manejo de errores**: Gestión robusta de errores

## Uso

### Uso básico
```bash
python scripts/backup_supabase.py
```

### Con opciones personalizadas
```bash
# Especificar directorio de salida
python scripts/backup_supabase.py --output-dir mi_backup

# Especificar tablas específicas
python scripts/backup_supabase.py --tables podcasts

# Combinar opciones
python scripts/backup_supabase.py --output-dir backups --tables podcasts,songs
```

## Opciones

- `--output-dir`: Directorio donde guardar los backups (default: `backups`)
- `--tables`: Tablas a hacer backup separadas por coma (default: `podcasts,songs`)

## Estructura del backup

Cada backup se guarda en un directorio con timestamp:
```
backups/
└── backup_20241201_143022/
    ├── podcasts.json
    ├── podcasts.csv
    ├── songs.json
    ├── songs.csv
    └── resumen.txt
```

## Archivos generados

- **`{tabla}.json`**: Datos completos en formato JSON
- **`{tabla}.csv`**: Datos completos en formato CSV
- **`resumen.txt`**: Resumen del backup con estadísticas

## Funcionalidades del DatabaseManager

Se han agregado los siguientes métodos al `DatabaseManager`:

### `export_table_with_pagination(table_name, page_size=1000)`
Exporta una tabla completa usando paginación para manejar tablas grandes.

### `get_table_count(table_name)`
Obtiene el número total de registros en una tabla.

### `create_backup(output_dir="backups", tables=None)`
Crea un backup completo de las tablas especificadas.

## Cambios realizados

### ✅ Eliminado
- Archivo `backup_supabase_simple.py` (consolidado)
- Dependencias externas (`services.supabase_database`, `services.logger_setup`)
- Tabla `extra_links` (ya no existe)

### ✅ Mejorado
- Código simplificado y mantenible
- Paginación automática para tablas grandes
- Solo dependencias internas del `sincronizador_rss`
- Mejor manejo de errores y logging

### ✅ Agregado
- Métodos de backup al `DatabaseManager`
- Script unificado con funcionalidad completa
- Documentación detallada

## Ejemplo de salida

```
🚀 Iniciando backup de Supabase...
📋 Cargando configuración...
🔌 Conectando a Supabase...
📊 Tablas a hacer backup: podcasts, songs
Exportando tabla podcasts con paginación...
  📄 Página 1: 1000 registros
  📄 Página 2: 500 registros
✅ Tabla podcasts exportada: 1500 registros totales
Exportando tabla songs con paginación...
  📄 Página 1: 1000 registros
  📄 Página 2: 1000 registros
  📄 Página 3: 250 registros
✅ Tabla songs exportada: 2250 registros totales
✅ Backup completado exitosamente en backups/backup_20241201_143022

✅ Backup completado exitosamente!
📁 Directorio: backups/backup_20241201_143022
📊 Tablas procesadas: 2
   - podcasts: 1500 registros
     JSON: backups/backup_20241201_143022/podcasts.json
     CSV: backups/backup_20241201_143022/podcasts.csv
   - songs: 2250 registros
     JSON: backups/backup_20241201_143022/songs.json
     CSV: backups/backup_20241201_143022/songs.csv
📄 Resumen: backups/backup_20241201_143022/resumen.txt
``` 