# Migración a Supabase

Este documento describe cómo migrar el proyecto de SQLite a Supabase.

## 📋 Prerrequisitos

1. Una cuenta en [Supabase](https://supabase.com)
2. Un proyecto creado en Supabase
3. Las credenciales del proyecto (URL y API Key)

## 🚀 Pasos para la migración

### 1. Configurar variables de entorno

Configura el archivo `.env` en el directorio raíz del proyecto con las siguientes variables:

```bash
# Tipo de base de datos (sqlite o supabase)
DATABASE_TYPE=supabase

# Configuración de Supabase
supabase_project_url=your_supabase_project_url_here
supabase_api_key=your_supabase_api_key_here
supabase_db_name=your_database_name_here
supabase_db_pass=your_database_password_here
```

### 2. Crear las tablas en Supabase

1. Ve al dashboard de tu proyecto en Supabase
2. Navega a **SQL Editor**
3. Copia y pega el contenido del archivo `supabase_schema.sql`
4. Ejecuta el script

### 3. Instalar dependencias

Las dependencias ya están incluidas en el proyecto:

```bash
# Activar el entorno virtual
source .venv/bin/activate

# Las dependencias ya están instaladas:
# - supabase
# - python-dotenv
```

### 4. Migrar los datos

Ejecuta el script de migración desde el directorio raíz:

```bash
python migration/migrate_to_supabase.py
```

Este script:
- Lee todos los datos de la base de datos SQLite
- Los migra a Supabase
- Mantiene las relaciones entre tablas
- Verifica que la migración fue exitosa

### 5. Verificar la migración

El script de migración incluye una verificación automática, pero puedes ejecutarla manualmente:

```bash
# Forma recomendada (como módulo)
python -m migration.test_supabase_connection

# O desde el directorio raíz
python migration/test_supabase_connection.py
```

O desde Python:

```python
from services.supabase_database import SupabaseDatabase

db = SupabaseDatabase()
podcasts = db.get_all_podcasts()
print(f"Podcasts migrados: {len(podcasts)}")
```

## 🔧 Configuración del código

### Opción 1: Usar configuración automática

El proyecto incluye un sistema de configuración automática. Solo necesitas cambiar la variable `DATABASE_TYPE` en el archivo `.env`:

```bash
# Para usar SQLite
DATABASE_TYPE=sqlite

# Para usar Supabase
DATABASE_TYPE=supabase
```

### Opción 2: Cambiar importaciones manualmente

Si prefieres cambiar las importaciones manualmente, reemplaza:

```python
# Antes (SQLite)
from services.database import (
    initialize_database,
    add_podcast_if_not_exists,
    # ... otras funciones
)

# Después (Supabase)
from services.supabase_database import (
    initialize_database,
    add_podcast_if_not_exists,
    # ... otras funciones
)
```

## 📊 Estructura de la base de datos

### Tabla `podcasts`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | ID único del podcast |
| title | TEXT | Título del podcast |
| date | TEXT | Fecha del podcast (único) |
| url | TEXT | URL del podcast |
| download_url | TEXT | URL de descarga |
| file_size | INTEGER | Tamaño del archivo |
| program_number | TEXT | Número del programa |
| wordpress_url | TEXT | URL de WordPress |
| cover_image_url | TEXT | URL de la imagen de portada |
| web_extra_links | TEXT | Links extras de la web |
| web_playlist | TEXT | Playlist de la web |
| last_web_check | TIMESTAMP | Última verificación web |
| created_at | TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP | Fecha de actualización |

### Tabla `songs`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | ID único de la canción |
| title | TEXT | Título de la canción |
| artist | TEXT | Artista |
| position | INTEGER | Posición en la lista |
| podcast_id | BIGINT | ID del podcast (FK) |
| created_at | TIMESTAMP | Fecha de creación |

### Tabla `extra_links`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGSERIAL | ID único del link |
| text | TEXT | Texto del link |
| url | TEXT | URL del link |
| podcast_id | BIGINT | ID del podcast (FK) |
| created_at | TIMESTAMP | Fecha de creación |

## 🔍 Diferencias con SQLite

### Ventajas de Supabase

1. **Escalabilidad**: Puede manejar grandes volúmenes de datos
2. **Concurrencia**: Múltiples usuarios pueden acceder simultáneamente
3. **Backup automático**: Copias de seguridad automáticas
4. **API REST**: Acceso a través de API REST
5. **Autenticación**: Sistema de autenticación integrado
6. **Tiempo real**: Suscripciones en tiempo real

### Consideraciones

1. **Latencia**: Las consultas pueden ser más lentas que SQLite local
2. **Dependencia de internet**: Requiere conexión a internet
3. **Límites de plan**: Dependiendo del plan de Supabase
4. **Complejidad**: Configuración inicial más compleja

## 🛠️ Solución de problemas

### Error de conexión

```
❌ Error al inicializar la base de datos: [Errno 11001] getaddrinfo failed
```

**Solución**: Verifica que las variables de entorno estén correctamente configuradas en el archivo `.env`.

### Error de autenticación

```
❌ Error al inicializar la base de datos: 401 Unauthorized
```

**Solución**: Verifica que el API Key sea correcto y tenga los permisos necesarios.

### Error de tabla no encontrada

```
❌ Error al inicializar la base de datos: relation "podcasts" does not exist
```

**Solución**: Ejecuta el script SQL en Supabase para crear las tablas.

### Error de migración

```
❌ Error migrando podcast: duplicate key value violates unique constraint
```

**Solución**: Los datos ya existen en Supabase. Puedes limpiar las tablas antes de migrar o usar el modo de actualización.

## 🔄 Rollback a SQLite

Si necesitas volver a SQLite:

1. Cambia `DATABASE_TYPE=sqlite` en el archivo `.env`
2. Las importaciones se ajustarán automáticamente
3. Los datos de SQLite permanecen intactos

## 📝 Notas adicionales

- El archivo `popcasting.db` se mantiene como respaldo
- Puedes usar ambas bases de datos simultáneamente cambiando la configuración
- Las funciones mantienen la misma interfaz, por lo que el código existente funciona sin cambios
- Se recomienda hacer una copia de seguridad antes de la migración

## 🆘 Soporte

Si encuentras problemas durante la migración:

1. Revisa los logs de error
2. Verifica la configuración de Supabase
3. Asegúrate de que las tablas existan
4. Consulta la documentación de Supabase: https://supabase.com/docs 