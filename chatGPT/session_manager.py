# chatGPT/session_manager.py
import os
import sys
import time
import socket
import threading

# Uso de utilidades
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.join(current_directory, '..')
sys.path.append(parent_directory)
from utils import Sistema
consola = Sistema.Consola()
color = Sistema.Colores()
contador = Sistema.Contador()





class ChatGPTSessionManager:
    def __init__(self, sessions_base_path: str, chrome_path: str):
        """ Inicializa el gestor de sesiones de ChatGPT """
        self.sessions_base_path = sessions_base_path
        self.chrome_path = chrome_path
        
        # Crea el directorio base si no existe
        if not os.path.exists(self.sessions_base_path):
            os.makedirs(self.sessions_base_path)

    @staticmethod
    def find_available_port():
        """ Encuentra un puerto disponible """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def launch_chrome_session(self, session_id: str):
        """ Lanza una nueva instancia de Chrome con un perfil específico """
        session_path = os.path.join(self.sessions_base_path, session_id)
        if not os.path.exists(session_path):
            os.makedirs(session_path)

        port = self.find_available_port()
        def open_chrome():
            chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port} --user-data-dir={session_path} https://chat.openai.com"
            os.system(chrome_cmd)

        chrome_thread = threading.Thread(target=open_chrome)
        chrome_thread.start()
        time.sleep(3)
        return port

    def create_new_session(self) -> tuple:
        """ Crea una nueva sesión y retorna su ID y puerto """
        # Encuentra el próximo número de sesión disponible
        existing_sessions = []
        for d in os.listdir(self.sessions_base_path):
            if os.path.isdir(os.path.join(self.sessions_base_path, d)) and d.startswith('session_'):
                existing_sessions.append(d)
        
        next_num = 1
        if existing_sessions:
            nums = []
            for s in existing_sessions:
                nums.append(int(s.split('_')[1]))
            next_num = max(nums) + 1

        session_id = f"session_{next_num:03d}"
        port = self.launch_chrome_session(session_id)
        return session_id, port

    def get_existing_sessions(self):
        """ Retorna una lista de las sesiones existentes """
        existing_sessions = []
        for d in os.listdir(self.sessions_base_path):
            if os.path.isdir(os.path.join(self.sessions_base_path, d)) and d.startswith('session_'):
                existing_sessions.append(d)
        return sorted(existing_sessions)

    def get_session_path(self, session_id: str) -> str:
        """ Obtiene la ruta completa de una sesión """
        path = os.path.join(self.sessions_base_path, session_id)
        if os.path.exists(path):
            return path
        raise ValueError(f"{color.color_rojo()} Sesión no encontrada: {session_id} {color.color_reset()}")



    '''
    >>> Función principal para añadir más sesiones de Google Chrome
    '''
    def create_sessions_interactive(self):
        """
        Función interactiva para crear sesiones de forma continua.
        El usuario decide cuándo dejar de crear sesiones nuevas.
        """
        while True:
            print(color.color_cyan())
            print("\n=== [ Creación de Sesiones de ChatGPT ] ===")
            print("¿Desea crear una nueva sesión?")
            user_input = input(" - Escriba 'y' para crear una nueva sesión, o 'n' para finalizar: ").lower().strip()
            
            if user_input == 'y':
                session_id, port = self.create_new_session()
                print(color.color_blanco())
                print(f"\n - Nueva sesión creada: {session_id}")
                print(f" - Puerto de depuración: {port}")
                print("\n[ Por favor, complete el inicio de sesión en la ventana de Chrome que se ha abierto ]")
                print(color.color_reset())
                
                # Espera a que el usuario confirme que ha iniciado sesión
                while True:
                    print(color.color_amarillo())
                    confirm = input(f" - ¿Ha completado el inicio de sesión? (y/n):").lower().strip()
                    if confirm == 'y':
                        print(" - Sesión configurada exitosamente")
                        break
                    elif confirm == 'n':
                        print(" - Esperando a que complete el inicio de sesión...")
                        time.sleep(5)
                    else:
                        print(" - Entrada inválida. Por favor escriba 'y' o 'n'")
                    print(color.color_reset())
                        
            elif user_input == 'n':
                existing = self.get_existing_sessions()
                print(color.color_magenta())
                print(f"\n - Finalizando creación de sesiones")
                print(f" - Total de sesiones existentes: {len(existing)}")
                print(f" - Sesiones: {', '.join(existing)}")
                print(color.color_reset())
                break
            else:
                print(color.color_rojo() + " - Entrada inválida. Por favor escriba 'y' o 'n'" + color.color_reset())
