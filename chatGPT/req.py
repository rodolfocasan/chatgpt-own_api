# chatGPT/req.py
import os
import sys
import time
import json
import socket
import psutil
import threading
import subprocess
from datetime import datetime
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC

# Uso de utilidades
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.join(current_directory, '..')
sys.path.append(parent_directory)
from utils import Sistema
consola = Sistema.Consola()
color = Sistema.Colores()
contador = Sistema.Contador()





class ChatGPTAutomation:
    # Métodos de inicialización y configuración
    def __init__(self, chrome_path: str, chrome_driver_path: str, sessions_path: str):
        """ Inicializa la instancia de automatización de ChatGPT """
        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path
        self.sessions_path = sessions_path
        self.current_session = None
        self.driver = None
        self.cookie = None
        self.chrome_process = None
        
        # Lista de sesiones disponibles y usadas
        self.available_sessions = self._get_available_sessions()
        self.used_sessions = set()
        
        self.conversation_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "sessions_used": []
            },
            "conversations": []
        }
    
    def _get_available_sessions(self) -> List[str]:
        """ Obtiene la lista de sesiones disponibles y ordenadas """
        sessions = []
        for d in os.listdir(self.sessions_path):
            if os.path.isdir(os.path.join(self.sessions_path, d)) and d.startswith('session_'):
                sessions.append(d)
        return sorted(sessions)
    
    def _initialize_session(self, session_id: str, port: int) -> None:
        """ Inicializa una sesión específica de Chrome """
        session_path = os.path.join(self.sessions_path, session_id)
        url = "https://chat.openai.com"
        
        def open_chrome():
            chrome_args = [
                self.chrome_path,
                f"--remote-debugging-port={port}",
                f"--user-data-dir={session_path}",
                url
            ]
            self.chrome_process = subprocess.Popen(chrome_args)

        chrome_thread = threading.Thread(target=open_chrome)
        chrome_thread.start()
        time.sleep(2.34)
    
    def setup_webdriver(self, port):
        """ Inicialización de WebDriver """
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = self.chrome_driver_path
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            return webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(color.color_rojo() + f" - Error configurando WebDriver: {str(e)}" + color.color_reset())
            raise
    
    @staticmethod
    def find_available_port():
        """ Encuentra un puerto disponible """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]
    
    
    
    # Métodos relacionados con la gestión de sesiones
    def get_cookie(self):
        """ Obtiene el valor de la cookie de sesión de autenticación """
        try:
            cookies = self.driver.get_cookies()
            cookie = []
            for elem in cookies:
                if elem["name"] == '__Secure-next-auth.session-token':
                    cookie.append(elem)
            if cookie:
                return cookie[0]['value']
            return None
        except Exception as e:
            print(color.color_rojo() + f" - Error obteniendo cookie: {str(e)}" + color.color_reset())
            return None
        
    def _switch_to_next_session(self) -> bool:
        """ Cambia a la siguiente sesión disponible (retorna 'False' si no hay más sesiones disponibles) """
        # Cierra la sesión actual si existe
        if self.driver:
            self.quit()
        
        # Mata solo el proceso de Chrome de la sesión actual
        self._kill_specific_chrome_process()

        # Busca la siguiente sesión disponible
        remaining_sessions = []
        for s in self.available_sessions:
            if s not in self.used_sessions:
                remaining_sessions.append(s)
                
        if not remaining_sessions:
            return False

        # Toma la primera sesión disponible
        self.current_session = remaining_sessions[0]
        self.used_sessions.add(self.current_session)
        
        # Registra la sesión en los metadatos
        if self.current_session not in self.conversation_data["metadata"]["sessions_used"]:
            self.conversation_data["metadata"]["sessions_used"].append(self.current_session)
        
        try:
            # Inicia la nueva sesión
            port = self.find_available_port()
            self._initialize_session(self.current_session, port)
            print(color.color_blanco() + f"\n[ Iniciando sesión: {self.current_session} ]" + color.color_reset())
            
            # Configurar el webdriver
            self.driver = self.setup_webdriver(port)
            self.driver.maximize_window()
            
            # Esperar a que la página cargue
            if not self._wait_for_page_load():
                print(color.color_rojo() + " - Error: Timeout esperando que la página cargue" + color.color_reset())
                # En caso de error, marcamos esta sesión como usada y probamos con la siguiente
                return self._switch_to_next_session()
                
            time.sleep(2.34)
            self.cookie = self.get_cookie()
            return True
        except Exception as e:
            # En caso de error, intentamos con la siguiente sesión
            print(color.color_rojo() + f" - Error iniciando sesión {self.current_session}: {str(e)}" + color.color_reset())
            return self._switch_to_next_session()
    
    def _kill_specific_chrome_process(self):
        """ Mata solo el proceso de Google Chrome asociado a la sesión actual """
        try:
            if self.chrome_process:
                # Se obtiene el proceso padre
                parent = psutil.Process(self.chrome_process.pid)
                
                # Se obtiene la línea de comando del proceso para verificar que sea la sesión correcta
                cmd_line = ' '.join(parent.cmdline())
                
                # Se obtiene solo los hijos directamente relacionados con esta sesión
                if self.current_session and self.current_session in cmd_line:
                    children = parent.children(recursive=True)
                    
                    # Se mata los procesos hijos de esta sesión específica
                    for child in children:
                        try:
                            child_cmd = ' '.join(child.cmdline())
                            if self.current_session in child_cmd:
                                child.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    
                    # Se mata el proceso padre de esta sesión
                    try:
                        parent.kill()
                    except psutil.NoSuchProcess:
                        pass
                    print(color.color_amarillo() + f"\n[ Proceso de Chrome de la sesión {self.current_session} terminado ]" + color.color_reset())
                else:
                    print(color.color_amarillo() + f"\n[ No se encontró el proceso de Chrome para la sesión {self.current_session} ]" + color.color_reset())
        except Exception as e:
            print(color.color_rojo() + f" - Error al matar proceso de Chrome específico: {str(e)}" + color.color_reset())
    
    def quit(self):
        """ Cierra el navegador y finaliza la sesión actual de WebDriver """
        try:
            print(f" - Cerrando sesión {self.current_session}...")
            if hasattr(self, 'driver') and self.driver:
                self.driver.close()
                self.driver.quit()
        except Exception as e:
            print(color.color_rojo() + f" - Error cerrando sesión {self.current_session}: {str(e)}" + color.color_reset())
        finally:
            # Se asegura de matar solo el proceso de Chrome de esta sesión
            self._kill_specific_chrome_process()
    
    
    
    # Métodos de interacción con la página web de ChatGPT
    def start_new_chat(self):
        """ Inicia una nueva conversación en ChatGPT haciendo clic en el botón de 'Nuevo Chat' o recargando la página si falla """
        try:
            new_chat_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.flex.py-3"))
            )
            new_chat_button.click()
            time.sleep(2.34)
        except Exception as e:
            print(color.color_rojo() + f" - Error iniciando nuevo chat: {str(e)}" + color.color_reset())
            self.driver.get("https://chat.openai.com/")
            time.sleep(2.34)
    
    def send_prompt_to_chatgpt(self, prompt):
        """ Envía el prompt a ChatGPT con sistema de reintentos y manejo de captcha """
        max_retries = 7
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Verificar captcha antes de cada intento
                if self._check_for_captcha():
                    continue
                    
                textarea = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.ID, "prompt-textarea"))
                )
                
                if not textarea.is_enabled():
                    print(color.color_azul() + " - 'Textarea' no habilitado, esperando..." + color.color_reset())
                    time.sleep(5)
                    continue
                
                textarea.clear()
                textarea.send_keys(prompt)
                time.sleep(1)
                
                send_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='send-button']"))
                )
                send_button.click()
                return
                    
            except Exception as e:
                print(color.color_rojo() + f" - Error enviando prompt (intento {retry_count + 1}): {str(e)}" + color.color_reset())
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(5)
                else:
                    raise
    
    def wait_for_complete_response(self) -> str:
        """ Espera a que la respuesta esté completa monitoreando su longitud """
        print(color.color_cyan() + "Esperando respuesta completa..." + color.color_reset())
        
        same_length_count = 0
        last_length = 0
        max_wait_time = 180  # Tiempo máximo de espera en segundos: 3 minutos
        start_time = time.time()
        
        while True:
            current_time = time.time()
            if current_time - start_time > max_wait_time:
                print(color.color_magenta() + " [ Tiempo máximo de espera excedido ]" + color.color_reset())
                break
                
            try:
                response_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.markdown")
                if not response_elements:
                    time.sleep(1)
                    continue
                    
                current_response = response_elements[-1].text
                current_length = len(current_response)
                
                print(color.color_cyan() + f" - Longitud de la respuesta actual: {current_length}" + color.color_reset())
                
                if current_length == last_length:
                    same_length_count += 1
                    print(color.color_verde() + f" - Conteo de misma longitud: {same_length_count}" + color.color_reset())
                    
                    if same_length_count >= 5: # 5 verificaciones de longitud de respuesta
                        print(color.color_blanco() + " - La respuesta parece estar completa" + color.color_reset())
                        return current_response
                else:
                    same_length_count = 0
                    
                last_length = current_length
            except Exception as e:
                print(color.color_rojo() + f" - Error mientras se esperaba la respuesta: {str(e)}" + color.color_reset())
            time.sleep(1)        
        return self.get_final_response()
    
    def get_final_response(self) -> str:
        """ Obtiene el último mensaje de respuesta de ChatGPT de la interfaz web """
        try:
            response_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.markdown")
            if response_elements:
                return response_elements[-1].text
        except Exception as e:
            print(color.color_rojo() + f" - Error obteniendo respuesta final: {str(e)}" + color.color_reset())
        return ""
    
    def send_prompt_and_get_response(self, prompt: str) -> str:
        """ Envía un prompt y espera la respuesta completa """
        try:
            self.send_prompt_to_chatgpt(prompt)
            return self.wait_for_complete_response()
        except Exception as e:
            print(color.color_rojo() + f" - Ocurrió un error: {str(e)}" + color.color_reset())
            return ""
    
    def _check_for_captcha(self) -> bool:
        """ Verifica si hay un captcha de Cloudflare presente """
        try:
            # Busca elementos típicos del captcha de Cloudflare (según documentación)
            captcha_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "iframe[src*='challenge'], div[class*='challenge'], #challenge-form")
            
            if captcha_elements:
                print(color.color_amarillo() + "\n[ CAPTCHA detectado ]" + color.color_reset())
                input("[ Presiona ENTER para confirmar la solución del Captcha ]")
                return True
            return False
        except Exception:
            return False
    
    def _wait_for_page_load(self, timeout: int = 30) -> bool:
        """ Espera a que la página se cargue completamente y maneja captchas cambiando de sesión """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Verifica si hay CAPTCHA
                captcha_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "iframe[src*='challenge'], div[class*='challenge'], #challenge-form")
                
                if captcha_elements:
                    print(color.color_amarillo() + "\n[ CAPTCHA detectado - Cambiando a siguiente sesión ]" + color.color_reset())
                    
                    # Cierra la sesión actual
                    self.quit()
                    time.sleep(2.34)
                    self.driver = None
                    self.chrome_process = None
                    
                    # Intenta cambiar a la siguiente sesión
                    if self._switch_to_next_session():
                        print(color.color_verde() + f"\n[ Cambiado exitosamente a sesión: {self.current_session} ]" + color.color_reset())
                        # Reinicia el contador de tiempo para la nueva sesión
                        start_time = time.time()
                        continue
                    else:
                        print(color.color_rojo() + "\n[ No hay más sesiones disponibles ]" + color.color_reset())
                        return False
                    
                # Verifica si el textarea está presente (página cargada correctamente)
                textarea = self.driver.find_element(By.ID, "prompt-textarea")
                if textarea.is_displayed():
                    return True
                    
            except NoSuchElementException:
                # El elemento no se encuentra, continuamos esperando
                pass
            except Exception as e:
                print(color.color_amarillo() + f"\n[ Error durante la carga de página: {str(e)} ]" + color.color_reset())
                # No salimos del bucle por otros tipos de errores, seguimos intentando
            time.sleep(1)
        return False
    
    
    
    # Métodos de procesamiento de datos
    def _sanitize_text(self, text: str) -> str:
        """ Limpia el texto para guardarlo en JSON manteniendo caracteres especiales """
        if not text:
            return ""
        
        # Reemplazar múltiples espacios en blanco con uno solo
        text = ' '.join(text.split())
        
        # Eliminar caracteres de control excepto saltos de línea específicos
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
        
        # Convertir saltos de línea múltiples en uno solo
        text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
        return text
    
    def _sanitize_json_data(self, data):
        """ Sanitiza recursivamente todos los campos de texto en la estructura de datos """
        if isinstance(data, dict):
            return {k: self._sanitize_json_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_json_data(item) for item in data]
        elif isinstance(data, str):
            return self._sanitize_text(data)
        else:
            return data

    def save_conversation_json(self, file_path: str):
        """ Guarda los datos de la conversación en un archivo JSON con sanitización """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Sanitizar todos los datos antes de guardar
            sanitized_data = self._sanitize_json_data(self.conversation_data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sanitized_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(color.color_rojo() + f"Error guardando conversación: {str(e)}" + color.color_reset())
            raise
    
    
    
    # Procesamiento principal
    def process_prompts(self, prompts: List[str], save_path: str = None) -> Dict:
        """ Procesa una lista de prompts intentando mantenerlos en una misma conversación """
        current_prompt_index = 0
        total_prompts = len(prompts)
        thread_failed = False
        
        while current_prompt_index < total_prompts:
            if not self.current_session or self.driver is None:
                if not self._switch_to_next_session():
                    print(color.color_amarillo() + "\n[ No hay más sesiones disponibles ]" + color.color_reset())
                    break
                
                # Si cambiamos de sesión, iniciamos nueva conversación
                print(color.color_verde() + f"\n[ Usando sesión: {self.current_session} ]" + color.color_reset())
                self.start_new_chat()
                thread_failed = False
            try:
                # Si el hilo falló anteriormente, intentamos nueva conversación
                if thread_failed:
                    print(color.color_amarillo() + "\n[ Intentando procesar prompt fallido en nueva conversación ]" + color.color_reset())
                    self.start_new_chat()
                    thread_failed = False
                
                while current_prompt_index < total_prompts:
                    prompt = self._sanitize_text(prompts[current_prompt_index])
                    print(color.color_cyan() + f"\n - Procesando prompt {current_prompt_index + 1}/{total_prompts}" + color.color_reset())
                    
                    response = self.send_prompt_and_get_response(prompt)
                    
                    # Si detectamos límite diario o respuesta vacía
                    if not response.strip() or "daily message limit" in response.lower():
                        print(color.color_rojo() + f"\n[ Sesión {self.current_session} agotada - Cerrando sesión ]" + color.color_reset())
                        
                        # Guardamos progreso antes de cerrar
                        if save_path:
                            self.save_conversation_json(save_path)
                        
                        # Cerramos sesión y forzamos cambio
                        self.quit()
                        time.sleep(2.34)
                        raise Exception("Sesión agotada - Límite diario alcanzado")
                    
                    conversation = {
                        "timestamp": datetime.now().isoformat(),
                        "session": self._sanitize_text(self.current_session),
                        "prompt": prompt,
                        "response": self._sanitize_text(response)
                    }
                    self.conversation_data["conversations"].append(conversation)
                    
                    if save_path:
                        self.save_conversation_json(save_path)
                        print(color.color_amarillo() + f" - Progreso guardado después del prompt {current_prompt_index + 1}" + color.color_reset())
                    
                    current_prompt_index += 1
                    
                    if current_prompt_index < total_prompts:
                        time.sleep(3)
                        
            except Exception as e:
                print(color.color_rojo())
                print(f"\n[ Error en el hilo de conversación: {str(e)} ]")
                print(" - Intentando recuperar el flujo...")
                print(color.color_reset())
                
                thread_failed = True
                
                # Si el error persiste después de intentar nueva conversación
                if thread_failed and "daily message limit" not in str(e):
                    print(color.color_rojo() + "\n[ Error persistente - Cambiando de sesión ]" + color.color_reset())
                    self.quit()
                    time.sleep(2.34)
                    self.driver = None
                    self.chrome_process = None
                continue
        return self.conversation_data