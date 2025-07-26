
import requests
import getpass
import os
import argparse
from dotenv import load_dotenv

def get_sid(base_url, username, password):
    """Obtiene un ID de sesión (SID) de Synology."""
    auth_url = f"{base_url}/auth.cgi"
    params = {
        'api': 'SYNO.API.Auth',
        'version': '7', 
        'method': 'login',
        'account': username,
        'passwd': password,
        'session': 'FileStation',
        'format': 'sid'
    }
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    try:
        response = requests.get(auth_url, params=params, verify=False)
        response.raise_for_status()
        data = response.json()
        if data.get('success'):
            print("Autenticación exitosa.")
            return data['data']['sid']
        else:
            error_code = data.get('error', {}).get('code')
            print(f"Error de autenticación (código {error_code}). Por favor, revisa la configuración de tu Synology (2FA, Bloqueo de IP, Permisos).")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return None

def upload_file(base_url, sid, file_path, remote_path):
    """Sube un archivo a Synology File Station."""
    upload_url = f"{base_url}/entry.cgi"
    params = {
        'api': 'SYNO.FileStation.Upload',
        'version': '2',
        'method': 'upload',
        '_sid': sid
    }
    data = {
        'path': remote_path,
        'create_parents': 'true'
    }
    
    if not os.path.exists(file_path):
        print(f"Error: El archivo local '{file_path}' no existe.")
        return

    files = {'file': (os.path.basename(file_path), open(file_path, 'rb'))}
    
    try:
        print(f"Subiendo '{os.path.basename(file_path)}' a '{remote_path}'...")
        response = requests.post(upload_url, params=params, data=data, files=files, verify=False)
        response.raise_for_status()
        result = response.json()
        if result.get('success'):
            print(f"¡Éxito! El archivo se ha subido correctamente.")
        else:
            error_code = result.get('error', {}).get('code')
            print(f"Error al subir el archivo (código {error_code})")
    except requests.exceptions.RequestException as e:
        print(f"Error en la subida: {e}")
    finally:
        files['file'][1].close()

def logout(base_url, sid):
    """Cierra la sesión de Synology."""
    logout_url = f"{base_url}/auth.cgi"
    params = {
        'api': 'SYNO.API.Auth',
        'version': '1',
        'method': 'logout',
        'session': 'FileStation',
        '_sid': sid
    }
    try:
        requests.get(logout_url, params=params, verify=False)
        print("Sesión cerrada.")
    except requests.exceptions.RequestException:
        pass

if __name__ == "__main__":
    load_dotenv() 

    parser = argparse.ArgumentParser(description="Sube un archivo a un Synology NAS.")
    parser.add_argument("local_file", help="Ruta completa al archivo local que quieres subir")
    parser.add_argument("remote_path", help="Ruta de destino en el Synology (ej: /home/MisArchivos)")
    parser.add_argument("--ip", default=os.getenv("SYNOLOGY_IP"), help="Dirección IP del Synology NAS (del .env)")
    parser.add_argument("--port", default=os.getenv("SYNOLOGY_PORT", 5000), type=int, help="Puerto de gestión del Synology (del .env)")
    parser.add_argument("--user", default=os.getenv("SYNOLOGY_USER"), help="Nombre de usuario del Synology (del .env)")

    args = parser.parse_args()

    if not all([args.ip, args.port, args.user]):
        print("Error: Faltan datos de conexión (IP, puerto o usuario). Asegúrate de que estén en el .env o pásalos como argumentos.")
        exit(1)

    password = os.getenv("SYNOLOGY_PASS") or getpass.getpass(prompt=f'Contraseña para el usuario {args.user}: ')
    
    protocol = 'https' if args.port == 5001 else 'http'
    base_url = f"{protocol}://{args.ip}:{args.port}/webapi"

    sid = get_sid(base_url, args.user, password)

    if sid:
        upload_file(base_url, sid, args.local_file, args.remote_path)
        logout(base_url, sid)
