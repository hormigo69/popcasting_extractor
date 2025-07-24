# Cliente de Synology NAS

Un cliente de línea de comandos simple para subir archivos a tu Synology NAS utilizando la API de File Station.

## Características

- ✅ Autenticación segura con SID (Session ID)
- ✅ Subida de archivos a cualquier carpeta del NAS
- ✅ Configuración mediante variables de entorno
- ✅ Manejo de errores robusto
- ✅ Cierre automático de sesión

## Configuración

### 1. Instalar dependencias

El proyecto ya incluye las dependencias necesarias en `pyproject.toml`:
- `requests` - Para las peticiones HTTP
- `python-dotenv` - Para cargar variables de entorno

### 2. Configurar credenciales

1. Copia el archivo de ejemplo:
   ```bash
   cp synology.env.example .env
   ```

2. Edita el archivo `.env` con tus datos reales:
   ```env
   SYNOLOGY_HOST=192.168.1.100
   SYNOLOGY_PORT=5000
   SYNOLOGY_USERNAME=tu_usuario
   SYNOLOGY_PASSWORD=tu_contraseña
   ```

### 3. Habilitar la API en tu Synology NAS

1. Accede al Panel de Control de tu Synology NAS
2. Ve a **Servicios de archivos** > **SMB/AFP/NFS**
3. Asegúrate de que el servicio SMB esté habilitado
4. Ve a **Servicios de archivos** > **File Station**
5. Habilita el servicio File Station

## Uso

### Comando básico

```bash
python synology_uploader.py data/Especiales.json
```

### Especificar carpeta de destino

```bash
python synology_uploader.py --remote-path "/backup" data/Especiales.json
```

### Sobrescribir configuración del .env

```bash
python synology_uploader.py --host 192.168.1.200 --port 5001 data/Especiales.json
```

### Ver ayuda

```bash
python synology_uploader.py --help
```

## Ejemplos de uso

### Subir archivo a la raíz del NAS
```bash
python synology_uploader.py data/Especiales.json
```

### Subir archivo a una carpeta específica
```bash
python synology_uploader.py --remote-path "/home/backup" data/Especiales.json
```

### Subir archivo usando HTTPS (puerto 5001)
```bash
python synology_uploader.py --host 192.168.1.100 --port 5001 data/Especiales.json
```

## Estructura del programa

El programa sigue este flujo:

1. **Carga de configuración**: Lee las credenciales del archivo `.env`
2. **Autenticación**: Se conecta al NAS y obtiene un SID
3. **Subida de archivo**: Sube el archivo especificado
4. **Cierre de sesión**: Libera el SID

## Solución de problemas

### Error de conexión
- Verifica que la IP y puerto sean correctos
- Asegúrate de que el NAS esté encendido y accesible
- Comprueba que no haya un firewall bloqueando la conexión

### Error de autenticación
- Verifica que el usuario y contraseña sean correctos
- Asegúrate de que el usuario tenga permisos para usar File Station

### Error al subir archivo
- Verifica que la carpeta de destino exista o tenga permisos para crearla
- Comprueba que tengas permisos de escritura en la carpeta de destino

### Puerto incorrecto
- Puerto 5000: HTTP (no seguro)
- Puerto 5001: HTTPS (recomendado para producción)

## Próximas mejoras

- [ ] Soporte para subida de múltiples archivos
- [ ] Soporte para subida de carpetas completas
- [ ] Barra de progreso durante la subida
- [ ] Verificación de integridad de archivos
- [ ] Soporte para autenticación de dos factores
- [ ] Configuración de timeouts personalizables 