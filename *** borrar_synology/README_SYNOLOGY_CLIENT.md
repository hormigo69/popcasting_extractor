# SynologyClient - Cliente para Synology NAS

Una clase Python reutilizable para interactuar con Synology NAS usando la API de File Station.

## Características

- ✅ **Autenticación automática** con SID
- ✅ **Subida de archivos** a carpetas específicas
- ✅ **Listado de archivos** con detalles
- ✅ **Creación de carpetas** automática
- ✅ **Descarga de archivos** del NAS
- ✅ **Context manager** para manejo automático de sesiones
- ✅ **Manejo de errores** robusto

## Configuración

### 1. Variables de entorno

Crea un archivo `.env` con las siguientes variables:

```env
SYNOLOGY_IP=192.168.1.143
SYNOLOGY_PORT=5000
SYNOLOGY_USER=popcasting
SYNOLOGY_PASS=tu_contraseña
```

### 2. Dependencias

```bash
pip install requests python-dotenv
```

## Uso básico

### Importar la clase

```python
from synology_client import SynologyClient
```

### Uso manual

```python
# Crear cliente
client = SynologyClient()

# Autenticar
if client.login():
    # Listar archivos
    files = client.list_files("/popcasting_marilyn")
    
    # Crear carpeta
    client.create_folder("/popcasting_marilyn/mp3")
    
    # Subir archivo
    success = client.upload_file("data/Especiales.json", "/popcasting_marilyn/mp3")
    
    # Cerrar sesión
    client.logout()
```

### Uso con context manager (recomendado)

```python
with SynologyClient() as client:
    # Listar archivos
    files = client.list_files("/popcasting_marilyn")
    
    # Crear carpeta y subir archivo
    client.create_folder("/popcasting_marilyn/mp3")
    success = client.upload_file("data/Especiales.json", "/popcasting_marilyn/mp3")
    
    if success:
        # Verificar subida
        mp3_files = client.list_files("/popcasting_marilyn/mp3")
```

## Métodos disponibles

### `__init__(host=None, port=None, username=None, password=None)`
Inicializa el cliente. Si no se proporcionan parámetros, los toma del archivo `.env`.

### `login()`
Autentica con el NAS y obtiene un SID.

**Returns:** `bool` - True si la autenticación fue exitosa

### `logout()`
Cierra la sesión y libera el SID.

### `upload_file(local_file_path, remote_folder="/mp3")`
Sube un archivo al NAS.

**Args:**
- `local_file_path`: Ruta del archivo local
- `remote_folder`: Carpeta de destino (por defecto "/mp3")

**Returns:** `bool` - True si la subida fue exitosa

### `list_files(remote_folder="/mp3")`
Lista archivos en una carpeta.

**Args:**
- `remote_folder`: Carpeta a listar (por defecto "/mp3")

**Returns:** `list` - Lista de archivos o None si hay error

### `create_folder(folder_path)`
Crea una carpeta en el NAS.

**Args:**
- `folder_path`: Ruta de la carpeta a crear

**Returns:** `bool` - True si la carpeta se creó exitosamente

### `download_file(remote_file_path, local_folder="downloads")`
Descarga un archivo del NAS.

**Args:**
- `remote_file_path`: Ruta del archivo en el NAS
- `local_folder`: Carpeta local de destino

**Returns:** `bool` - True si la descarga fue exitosa

## Ejemplos de uso

### Subir archivos a carpeta mp3

```python
with SynologyClient() as client:
    # Crear carpeta mp3 si no existe
    client.create_folder("/popcasting_marilyn/mp3")
    
    # Subir archivo
    success = client.upload_file("mi_archivo.mp3", "/popcasting_marilyn/mp3")
    
    if success:
        print("✅ Archivo subido correctamente")
```

### Listar archivos en una carpeta

```python
with SynologyClient() as client:
    files = client.list_files("/popcasting_marilyn")
    
    if files:
        for file in files:
            file_type = "📁" if file["isdir"] else "📄"
            print(f"{file_type} {file['name']}")
```

### Descargar archivo del NAS

```python
with SynologyClient() as client:
    success = client.download_file("/popcasting_marilyn/mi_archivo.txt", "downloads")
    
    if success:
        print("✅ Archivo descargado correctamente")
```

## Manejo de errores

La clase maneja automáticamente:
- Errores de conexión
- Errores de autenticación
- Errores de permisos
- Timeouts

Los errores se muestran con códigos específicos:
- `401`: Error de autenticación
- `408`: Timeout
- `1100`: Error de permisos
- `414`: Error de parámetros

## Archivos del proyecto

- `synology_client.py`: Clase principal
- `test_synology_client.py`: Script de pruebas
- `example_usage.py`: Ejemplos de uso
- `README_SYNOLOGY_CLIENT.md`: Esta documentación

## Notas importantes

1. **Carpeta por defecto**: La carpeta por defecto es `/mp3`, pero puedes cambiarla
2. **Permisos**: Asegúrate de que el usuario tenga permisos en las carpetas
3. **Timeouts**: Los timeouts están configurados para archivos grandes
4. **SSL**: Los warnings de SSL están deshabilitados para desarrollo

## Próximas mejoras

- [ ] Soporte para subida de múltiples archivos
- [ ] Barra de progreso durante subidas
- [ ] Verificación de integridad de archivos
- [ ] Soporte para autenticación de dos factores 