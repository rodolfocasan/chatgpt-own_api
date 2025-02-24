# dependencies.py
import os
import shutil
import zipfile
import requests
import subprocess
from tqdm import tqdm

from router import verificar_ruta_almacenamiento

# Uso de utilidades
from utils import Sistema
color = Sistema.Colores()
consola = Sistema.Consola()
contador = Sistema.Contador()





'''
>>> Funciones auxiliares
'''
# Obtiene la versión de Google Chrome instalada.
def obtener_version_chrome():
    try:
        chrome_version = subprocess.check_output(['google-chrome', '--version'])
        return chrome_version.decode('utf-8').strip().split()[-1]
    except subprocess.CalledProcessError:
        print(color.color_rojo())
        raise Exception(f" (ERROR) No se pudo detectar la versión de Google Chrome. Asegúrate de que esté instalado.{color.color_reset()}")

# Obtiene la versión del chromedriver instalado.
def obtener_version_chromedriver(chromedriver_path):
    try:
        result = subprocess.check_output([chromedriver_path, '--version'])
        version = result.decode('utf-8').split()[1] # El formato típico es: "ChromeDriver XX.X.XXXX.XX ..."
        return version
    except (subprocess.CalledProcessError, IndexError, FileNotFoundError):
        return None

# Verifica si Ngrok está instalado en el sistema
def verificar_ngrok_instalado():
    try:
        subprocess.run(['which', 'ngrok'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

# Verifica si el Ngrok Authtoken está configurado correctamente
def verificar_ngrok_authtoken():
    try:
        # Comando para verificar la configuración del authtoken
        result = subprocess.run(['ngrok', 'config', 'check'], 
                                capture_output=True, text=True, check=True)
        
        # Buscar en la salida si hay alguna indicación de problemas con el authtoken
        if "no config file found" in result.stdout.lower():
            return False
        
        # Intentar hacer un comando que requiera autenticación
        verify_result = subprocess.run(['ngrok', 'credits'], capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False




'''
>>> Instalación de drivers y dependencias
'''
def descargar_chrome_webdriver_debian():
    """
    Descarga e instala el chromedriver que coincide exactamente con la versión de Google Chrome instalada en Debian.
    - Retorna la ruta del chromedriver instalado, o None si ocurre un error.
    """
    
    consola.limpiar_consola()
    print(color.color_amarillo())
    print("[ Descarga de driver (Google Chrome) ]")
    try:
        # Ruta donde se almacenará el webdriver
        save_path = os.path.join(verificar_ruta_almacenamiento(), 'Drivers')
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        
        chromedriver_path = os.path.join(save_path, 'chromedriver-linux64', 'chromedriver')
        chrome_version = obtener_version_chrome()
        print(f" - Versión de Google Chrome detectada: {chrome_version}")
        
        # Verificar si existe un chromedriver y su versión
        if os.path.exists(chromedriver_path):
            driver_version = obtener_version_chromedriver(chromedriver_path)
            if driver_version:
                if driver_version == chrome_version:
                    print(color.color_magenta() + f" - El chromedriver instalado (versión {driver_version}) coincide con Chrome. No es necesario actualizar." + color.color_reset())
                    return chromedriver_path
                else:
                    print(color.color_cyan() + f"( Discrepancia de versiones detectada )")
                    print(color.color_azul())
                    print(f" - Versión de Google Chrome: {chrome_version}")
                    print(f" - Versión de Chromedriver : {driver_version}")
                    print(color.color_rojo() + " [!!] Eliminando versión anterior para descargar la correcta..." + color.color_reset())
                    shutil.rmtree(os.path.join(save_path, 'chromedriver-linux64'))
            else:
                print(color.color_rojo())
                print(" [!!] No se pudo verificar la versión del chromedriver existente. Se procederá a reinstalar.")
                if os.path.exists(os.path.join(save_path, 'chromedriver-linux64')):
                    shutil.rmtree(os.path.join(save_path, 'chromedriver-linux64'))
                print(color.color_reset())
        
        # Construir la URL con la versión exacta
        url_chromedriver = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/linux64/chromedriver-linux64.zip"
        
        try:
            # Verificar si el archivo existe antes de intentar descargarlo
            response = requests.head(url_chromedriver)
            if response.status_code == 404:
                raise Exception(f"{color.color_rojo()} [!!] No se encontró el chromedriver para la versión {chrome_version}. Es posible que esta versión exacta no esté disponible en el repositorio. {color.color_reset()}")
            
            # Ruta completa donde se guardará el zip
            zip_path = os.path.join(save_path, 'chromedriver.zip')
            
            # Iniciar la descarga con barra de progreso
            print(color.color_verde())
            print(f" - Descargando chromedriver desde: {url_chromedriver}")
            response = requests.get(url_chromedriver, stream=True)
            response.raise_for_status()
            
            # Obtener el tamaño total del archivo
            total_size = int(response.headers.get('content-length', 0))
            
            # Crear la barra de progreso
            progress_bar = tqdm(
                total = total_size,
                unit = 'iB',
                unit_scale = True,
                desc = 'Progreso de descarga'
            )
            
            # Guardar el archivo zip mostrando el progreso
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        size = f.write(chunk)
                        progress_bar.update(size)
            progress_bar.close()
            
            # Extraer el archivo
            print(color.color_gris())
            print("Extrayendo archivos...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(save_path)
            
            # Establecer permisos de ejecución
            os.chmod(chromedriver_path, 0o755)
            
            # Limpiar el archivo zip
            os.remove(zip_path)
            
            print(color.color_amarillo() + f"Chromedriver instalado exitosamente en: {chromedriver_path}" + color.color_reset())
            return chromedriver_path
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"{color.color_rojo()} [!!] Error al descargar chromedriver: {str(e)} {color.color_reset()}")
    except Exception as e:
        print(f"{color.color_rojo()} [!!] Error durante la instalación del chromedriver: {str(e)} {color.color_reset()}")
        return None


def instalar_ngrok_debian():
    """
    Instala Ngrok en un sistema Debian y configura el authtoken.
    - Retorna True si la instalación y configuración son exitosas, False en caso contrario.
    """
    try:
        consola.limpiar_consola()
        print(color.color_amarillo())
        print("[ Instalación de Ngrok ]")

        # Verificar si Ngrok ya está instalado
        if verificar_ngrok_instalado():
            # Verificar si el authtoken ya está configurado
            if verificar_ngrok_authtoken():
                print(color.color_verde() + " - Ngrok ya está instalado y configurado correctamente" + color.color_reset())
                return True
            else:
                print(color.color_amarillo() + " - Ngrok está instalado, pero requiere configuración de authtoken" + color.color_reset())
        
        # Si no está instalado o requiere configuración, proceder con la instalación
        # Agregar la clave GPG de Ngrok
        try:
            subprocess.run([
                'sudo', 'bash', '-c', 
                'curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null'
            ], check=True)
            print(color.color_verde() + " - Clave GPG de Ngrok agregada correctamente" + color.color_reset())
        except subprocess.CalledProcessError:
            print(color.color_rojo() + " [!!] Error al agregar la clave GPG de Ngrok" + color.color_reset())
            return False

        # Agregar el repositorio de Ngrok
        try:
            subprocess.run([
                'sudo', 'bash', '-c', 
                'echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list'
            ], check=True)
            print(color.color_verde() + " - Repositorio de Ngrok agregado correctamente" + color.color_reset())
        except subprocess.CalledProcessError:
            print(color.color_rojo() + " [!!] Error al agregar el repositorio de Ngrok" + color.color_reset())
            return False

        # Actualizar lista de paquetes
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            print(color.color_verde() + " - Lista de paquetes actualizada" + color.color_reset())
        except subprocess.CalledProcessError:
            print(color.color_rojo() + " [!!] Error al actualizar la lista de paquetes" + color.color_reset())
            return False

        # Instalar Ngrok
        try:
            subprocess.run(['sudo', 'apt', 'install', '-y', 'ngrok'], check=True)
            print(color.color_verde() + " - Ngrok instalado correctamente" + color.color_reset())
        except subprocess.CalledProcessError:
            print(color.color_rojo() + " [!!] Error al instalar Ngrok" + color.color_reset())
            return False

        # Solicitar y configurar el authtoken
        print(color.color_magenta())
        print("\n[ Configuración de Ngrok ]")
        print(" - Por favor, ingrese su Ngrok Authtoken desde https://dashboard.ngrok.com/get-started/your-authtoken")
        
        max_intentos = 3
        for intento in range(max_intentos):
            authtoken = input(color.color_cyan() + " Authtoken: " + color.color_reset()).strip()
            
            if not authtoken:
                print(color.color_rojo() + " [!!] El authtoken no puede estar vacío. Intente nuevamente." + color.color_reset())
                continue

            try:
                # Configurar el authtoken
                subprocess.run(['ngrok', 'config', 'add-authtoken', authtoken], check=True)
                
                # Verificar que el authtoken se configuró correctamente
                if verificar_ngrok_authtoken():
                    print(color.color_verde() + " - Authtoken configurado y verificado exitosamente" + color.color_reset())
                    break
                else:
                    print(color.color_rojo() + " [!!] Error: El authtoken no se configuró correctamente" + color.color_reset())
                    
                    if intento == max_intentos - 1:
                        print(color.color_rojo() + " [!!] Número máximo de intentos alcanzado. Instalación cancelada." + color.color_reset())
                        return False
                    
                    retry = input(color.color_amarillo() + " ¿Desea intentar de nuevo? (s/n): " + color.color_reset()).lower()
                    if retry != 's':
                        return False
            except Exception as error_log:
                print(color.color_rojo())
                print("[ Ocurrió un error ]")
                print(error_log + color.color_reset())

        print(color.color_amarillo() + "\n[ Instalación de Ngrok completada ]" + color.color_reset())
        return True
    except Exception as e:
        print(color.color_rojo() + f" [!!] Error inesperado durante la instalación de Ngrok: {str(e)}" + color.color_reset())
        return False