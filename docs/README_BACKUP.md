# Scripts de Backup para Supabase

Este directorio contiene scripts para hacer backup y restaurar la base de datos Supabase del proyecto Popcasting Extractor.

## 📁 Archivos Disponibles

### Scripts de Backup

1. **`scripts/utils/backup_supabase.py`** - Script completo con múltiples opciones
2. **`scripts/backup_supabase_simple.py`** - Script simple y directo
3. **`scripts/utils/restore_supabase.py`** - Script para restaurar backups

## 🚀 Uso Rápido

### Backup Simple

```bash
# Activar entorno virtual
source .venv/bin/activate

# Hacer backup básico
python scripts/backup_supabase_simple.py
```

### Backup Avanzado

```bash
# Backup con opciones personalizadas
python scripts/utils/backup_supabase.py --output-dir backups_personalizados

# Solo exportar a JSON
python scripts/utils/backup_supabase.py --format json

# Solo exportar a CSV
python scripts/utils/backup_supabase.py --format csv
```

## 📊 Estructura del Backup

Cada backup se guarda en un directorio con timestamp:

```
backups/
└── backup_20241201_143022/
    ├── podcasts.json          # Datos de podcasts
    ├── songs.json            # Datos de canciones
    ├── extra_links.json      # Datos de links extra
    ├── podcasts.csv          # Versión CSV (opcional)
    ├── songs.csv             # Versión CSV (opcional)
    ├── extra_links.csv       # Versión CSV (opcional)
    ├── backup_summary.txt    # Resumen del backup
    └── metadata.json         # Metadatos del backup
```

## 🔄 Restauración

### Vista Previa de un Backup

```bash
# Ver contenido del backup sin restaurar
python scripts/utils/restore_supabase.py backups/backup_20241201_143022 --preview

# Simular restauración
python scripts/utils/restore_supabase.py backups/backup_20241201_143022 --dry-run
```

### Restaurar Backup Completo

```bash
# Restaurar todas las tablas
python scripts/utils/restore_supabase.py backups/backup_20241201_143022

# Restaurar con limpieza previa (¡CUIDADO!)
python scripts/utils/restore_supabase.py backups/backup_20241201_143022 --clear
```

### Restaurar Tabla Específica

```bash
# Restaurar solo podcasts
python scripts/utils/restore_supabase.py backups/backup_20241201_143022 --table podcasts

# Restaurar solo canciones con limpieza
python scripts/utils/restore_supabase.py backups/backup_20241201_143022 --table songs --clear
```

## ⚙️ Configuración Requerida

Asegúrate de tener configuradas las variables de entorno en tu archivo `.env`:

```env
# Configuración de Supabase
supabase_project_url=tu_url_de_proyecto_supabase
supabase_api_key=tu_api_key_de_supabase
```

## 📋 Tablas Incluidas

Los scripts hacen backup de las siguientes tablas:

- **`podcasts`** - Información principal de los podcasts
- **`songs`** - Canciones de cada podcast
- **`extra_links`** - Links adicionales de cada podcast

## 🔧 Características

### Script de Backup Completo (`backup_supabase.py`)

- ✅ Exportación a JSON y CSV
- ✅ Archivos de metadatos y resumen
- ✅ Manejo de errores robusto
- ✅ Logging detallado
- ✅ Opciones de línea de comandos
- ✅ Validación de datos

### Script de Backup Simple (`backup_supabase_simple.py`)

- ✅ Fácil de usar
- ✅ Exportación rápida a JSON
- ✅ Resumen básico
- ✅ Sin dependencias complejas

### Script de Restauración (`restore_supabase.py`)

- ✅ Restauración completa o por tabla
- ✅ Vista previa de backups
- ✅ Modo dry-run para simulación
- ✅ Opción de limpieza previa
- ✅ Restauración en lotes para grandes volúmenes

## ⚠️ Advertencias Importantes

1. **Antes de restaurar**: Siempre haz un backup del estado actual
2. **Opción `--clear`**: Borra TODOS los datos existentes antes de restaurar
3. **Permisos**: Asegúrate de tener permisos de escritura en Supabase
4. **Espacio en disco**: Los backups pueden ocupar espacio significativo
5. **Conexión**: Verifica que tienes conexión estable a internet

## 🛠️ Solución de Problemas

### Error de Conexión

```bash
# Verificar variables de entorno
echo $supabase_project_url
echo $supabase_api_key

# Probar conexión
python -c "from services.supabase_database import SupabaseDatabase; db = SupabaseDatabase(); print('Conexión OK')"
```

### Error de Permisos

```bash
# Hacer ejecutable el script
chmod +x scripts/backup_supabase_simple.py
chmod +x scripts/utils/backup_supabase.py
chmod +x scripts/utils/restore_supabase.py
```

### Backup Vacío

- Verifica que las tablas contengan datos
- Revisa los logs para errores específicos
- Confirma que las variables de entorno son correctas

## 📈 Automatización

### Backup Automático Diario

Puedes configurar un cron job para backups automáticos:

```bash
# Editar crontab
crontab -e

# Agregar línea para backup diario a las 2 AM
0 2 * * * cd /ruta/a/popcasting_extractor && source .venv/bin/activate && python scripts/backup_supabase_simple.py
```

### Limpieza de Backups Antiguos

```bash
# Script para limpiar backups de más de 30 días
find backups/ -name "backup_*" -type d -mtime +30 -exec rm -rf {} \;
```

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs en `logs/`
2. Verifica la configuración de Supabase
3. Confirma que tienes las dependencias instaladas
4. Revisa los permisos de archivos y directorios

---

**Nota**: Estos scripts están diseñados específicamente para la estructura de datos de Popcasting Extractor. Si modificas la estructura de la base de datos, actualiza los scripts correspondientes. 