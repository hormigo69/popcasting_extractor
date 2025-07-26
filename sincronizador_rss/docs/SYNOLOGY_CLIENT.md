# Cliente Synology NAS

## Descripción

El `SynologyClient` es una clase Python que proporciona una interfaz simplificada para interactuar con la API File Station de Synology NAS. Permite autenticación, subida de archivos, listado de contenido y lectura de archivos de forma segura y eficiente.

## Características

- ✅ **Autenticación automática** con token de sesión
- ✅ **Subida de archivos** a carpetas compartidas específicas
- ✅ **Listado de contenido** de carpetas y carpetas compartidas
- ✅ **Lectura de archivos** de texto del NAS
- ✅ **Context manager** para gestión automática de sesiones
- ✅ **Manejo robusto de errores** y timeouts
- ✅ **Configuración desde variables de entorno**

## Instalación y Configuración

### 1. Variables de Entorno

Añade las siguientes variables a tu archivo `.env`:

```bash
SYNOLOGY_IP=192.168.1.143
SYNOLOGY_PORT=5000
SYNOLOGY_USER=tu_usuario
SYNOLOGY_PASS=tu_contraseña
SYNOLOGY_SHARED_FOLDER=/popcasting_marilyn
```

### 2. Configuración del ConfigManager

El `ConfigManager` ya incluye el método `get_synology_credentials()` que lee estas variables:

```python
from src.components.config_manager import ConfigManager

cfg = ConfigManager()
credentials = cfg.get_synology_credentials()
```

## Uso Básico

### Inicialización y Autenticación

```python
from src.components.synology_client import SynologyClient
from src.components.config_manager import ConfigManager

# Obtener credenciales
cfg = ConfigManager()
credentials = cfg.get_synology_credentials()

# Usar con context manager (recomendado)
with SynologyClient(
    ip=credentials["ip"],
    port=credentials["port"],
    username=credentials["user"],
    password=credentials["password"]
) as client:
    # Tu código aquí
    pass
```

### Subida de Archivos

```python
with SynologyClient(**credentials) as client:
    # Subir un archivo
    success = client.upload_file(
        local_path="archivo_local.txt",
        remote_folder_path="/popcasting_marilyn"
    )
    
    if success:
        print("✅ Archivo subido exitosamente")
    else:
        print("❌ Error al subir archivo")
```

### Listado de Contenido

```python
with SynologyClient(**credentials) as client:
    # Listar carpetas compartidas disponibles
    shared_folders = client.list_shared_folders()
    for folder in shared_folders:
        print(f"Carpeta: {folder.get('name')} -> {folder.get('path')}")
    
    # Listar contenido de una carpeta específica
    files = client.list_files("/popcasting_marilyn")
    if files:
        for file_info in files:
            name = file_info.get("name")
            is_dir = file_info.get("isdir", False)
            size = file_info.get("size", 0)
            print(f"{'📁' if is_dir else '📄'} {name} ({size} bytes)")
```

### Lectura de Archivos

```python
with SynologyClient(**credentials) as client:
    # Leer contenido de un archivo
    content = client.read_file("/popcasting_marilyn/archivo.txt")
    if content:
        print(f"Contenido: {content}")
    else:
        print("❌ No se pudo leer el archivo")
```

## API Reference

### SynologyClient

#### Constructor

```python
SynologyClient(ip: str, port: str, username: str, password: str)
```

**Parámetros:**
- `ip`: IP del NAS de Synology
- `port`: Puerto del NAS (normalmente 5000 para HTTP)
- `username`: Nombre de usuario
- `password`: Contraseña

#### Métodos

##### `login() -> bool`
Autentica con el NAS y obtiene el token de sesión.

**Retorna:** `True` si el login fue exitoso, `False` en caso contrario.

##### `logout() -> bool`
Cierra la sesión en el NAS.

**Retorna:** `True` si el logout fue exitoso, `False` en caso contrario.

##### `upload_file(local_path: str, remote_folder_path: str) -> bool`
Sube un archivo local a una carpeta específica en el NAS.

**Parámetros:**
- `local_path`: Ruta del archivo local a subir
- `remote_folder_path`: Carpeta de destino en el NAS

**Retorna:** `True` si la subida fue exitosa, `False` en caso contrario.

##### `list_files(folder_path: str = "/") -> list`
Lista archivos y carpetas en una ruta específica del NAS.

**Parámetros:**
- `folder_path`: Ruta de la carpeta a listar (por defecto "/")

**Retorna:** Lista de archivos y carpetas, o `None` si hay error.

##### `read_file(file_path: str) -> str`
Lee el contenido de un archivo del NAS.

**Parámetros:**
- `file_path`: Ruta completa del archivo a leer

**Retorna:** Contenido del archivo, o `None` si hay error.

##### `list_shared_folders() -> list`
Devuelve una lista de carpetas compartidas accesibles.

**Retorna:** Lista de carpetas compartidas disponibles.

#### Context Manager

```python
def __enter__(self) -> SynologyClient
def __exit__(self, exc_type, exc_val, exc_tb) -> None
```

Permite usar la clase con un bloque `with` para gestión automática de sesiones.

## Ejemplos de Uso

### Ejemplo 1: Subida Simple

```python
from src.components.synology_client import SynologyClient
from src.components.config_manager import ConfigManager

def subir_archivo(archivo_local, carpeta_destino):
    cfg = ConfigManager()
    credentials = cfg.get_synology_credentials()
    
    with SynologyClient(**credentials) as client:
        return client.upload_file(archivo_local, carpeta_destino)

# Uso
if subir_archivo("mi_archivo.txt", "/popcasting_marilyn"):
    print("✅ Archivo subido")
else:
    print("❌ Error al subir")
```

### Ejemplo 2: Backup de Archivos

```python
import os
from src.components.synology_client import SynologyClient
from src.components.config_manager import ConfigManager

def hacer_backup(carpeta_local, carpeta_nas):
    cfg = ConfigManager()
    credentials = cfg.get_synology_credentials()
    
    with SynologyClient(**credentials) as client:
        archivos_subidos = 0
        archivos_fallidos = 0
        
        for archivo in os.listdir(carpeta_local):
            ruta_local = os.path.join(carpeta_local, archivo)
            if os.path.isfile(ruta_local):
                if client.upload_file(ruta_local, carpeta_nas):
                    archivos_subidos += 1
                    print(f"✅ {archivo}")
                else:
                    archivos_fallidos += 1
                    print(f"❌ {archivo}")
        
        print(f"\nResumen: {archivos_subidos} subidos, {archivos_fallidos} fallidos")
```

### Ejemplo 3: Verificación de Contenido

```python
from src.components.synology_client import SynologyClient
from src.components.config_manager import ConfigManager

def verificar_contenido(carpeta_nas):
    cfg = ConfigManager()
    credentials = cfg.get_synology_credentials()
    
    with SynologyClient(**credentials) as client:
        # Listar carpetas compartidas
        shared_folders = client.list_shared_folders()
        print("Carpetas compartidas disponibles:")
        for folder in shared_folders:
            print(f"  - {folder.get('name')}: {folder.get('path')}")
        
        # Listar contenido de la carpeta específica
        files = client.list_files(carpeta_nas)
        if files:
            print(f"\nContenido de {carpeta_nas}:")
            for file_info in files:
                name = file_info.get("name")
                is_dir = file_info.get("isdir", False)
                size = file_info.get("size", 0)
                print(f"  {'📁' if is_dir else '📄'} {name} ({size} bytes)")
        else:
            print(f"❌ No se pudo listar contenido de {carpeta_nas}")
```

## Manejo de Errores

El cliente maneja automáticamente los siguientes tipos de errores:

- **Errores de conexión**: Timeouts y problemas de red
- **Errores de autenticación**: Credenciales incorrectas o sesión expirada
- **Errores de permisos**: Acceso denegado a carpetas o archivos
- **Errores de archivo**: Archivos inexistentes o corruptos

### Códigos de Error Comunes

- **119**: Parámetro inválido
- **400**: Error de solicitud
- **401**: No autorizado
- **407**: Proxy requerido
- **408**: Timeout de solicitud

## Limitaciones

- Solo soporta archivos de texto para lectura
- No incluye soporte para autenticación de dos factores
- No incluye verificación de integridad de archivos (checksum)
- No incluye barra de progreso para subidas grandes

## Próximas Mejoras

- [ ] Soporte para subida de múltiples archivos
- [ ] Barra de progreso durante subidas
- [ ] Verificación de integridad de archivos (checksum)
- [ ] Soporte para autenticación de dos factores
- [ ] Configuración de carpetas por defecto personalizable
- [ ] Logs detallados de operaciones
- [ ] Retry automático en caso de fallos de red

## Archivos Relacionados

- `src/components/synology_client.py`: Implementación del cliente
- `src/components/config_manager.py`: Gestión de configuración
- `src/utils/logger.py`: Sistema de logging
- `.env`: Variables de entorno para configuración 