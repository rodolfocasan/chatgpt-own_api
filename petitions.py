# petitions.py
import os
import sys
import json
import logging
from datetime import datetime

from chatGPT.req import ChatGPTAutomation

from router import clear_clipboard
from router import verificar_ruta_almacenamiento

# Uso de utilidades
from utils import Sistema
consola = Sistema.Consola()
color = Sistema.Colores()
contador = Sistema.Contador()





'''
>>> Definición de funciones
'''
def run_chatgpt(prompts_file: str, save_path: str, clean_pastData: bool = False) -> dict:
    # Se limpia el portapapeles antes que cualquier cosa
    clear_clipboard()
    
    # Configuración de logging
    logging.basicConfig(
        level = logging.INFO,
        format = '%(asctime)s - %(levelname)s - %(message)s',
        handlers = [
            logging.FileHandler(os.path.join(save_path, 'chatgpt_automata.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    try:
        # Define las rutas de Chrome - podrías querer hacerlas configurables también
        chrome_path = "/usr/bin/google-chrome"
        #chrome_driver_path = os.path.join('Storage', 'Drivers', 'chromedriver-linux64', 'chromedriver')
        chrome_driver_path = "Storage/Drivers/chromedriver-linux64/chromedriver"
        
        # Verifica que las rutas existan
        for path in [chrome_driver_path, chrome_path, prompts_file]:
            if not os.path.exists(path):
                raise FileNotFoundError(f" - Archivo requerido no encontrado: {path}")
        
        # Genera un nombre de archivo único basado en la marca de tiempo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_folder = os.path.join(save_path, 'Conversations')
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        
        # Limpieza de datos si se solicita
        if clean_pastData:
            for file_name in os.listdir(out_folder):
                if file_name.startswith("chat_session_") and file_name.endswith(".json"):
                    file_path = os.path.join(out_folder, file_name)
                    os.remove(file_path)
            logging.info(f"Archivos existentes en '{out_folder}' eliminados por clean_pastData=True")
            
        output_file = os.path.join(out_folder, f"chat_session_{timestamp}.json")
        
        # Carga los prompts desde un archivo JSON
        try:
            with open(prompts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                prompts = data.get('prompts', [])
        except Exception as e:
            logging.error(f"Error cargando prompts: {str(e)}")
            return {}
            
        if not prompts:
            logging.error("No se encontraron prompts en el archivo de entrada")
            return {}
            
        logging.info(f"Se cargaron {len(prompts)} prompts para procesar")
        logging.info("Inicializando la automatización de ChatGPT...")
        
        # Inicializa la automatización
        sessions_folder = os.path.join(verificar_ruta_almacenamiento(), 'GPT', 'Sessions')
        
        chatgpt = ChatGPTAutomation(
            chrome_path = chrome_path,
            chrome_driver_path = chrome_driver_path,
            sessions_path = sessions_folder
        )
        
        try:
            # Procesa todos los prompts y guarda en JSON
            logging.info("Iniciando el procesamiento de prompts...")
            conversation_data = chatgpt.process_prompts(
                prompts= prompts,
                save_path = output_file
            )
            
            logging.info(f"Todos los prompts se procesaron exitosamente")
            logging.info(f"Conversación guardada en: {output_file}")
            
            # Imprime resumen
            num_conversations = len(conversation_data["conversations"])
            logging.info(f"Total de conversaciones procesadas: {num_conversations}")
            return conversation_data
        except Exception as e:
            logging.error(f"Error durante el procesamiento de prompts: {str(e)}")
            raise
        finally:
            logging.info("Limpiando recursos...")
            chatgpt.quit()
    except Exception as e:
        logging.error(f"Error fatal: {str(e)}")
        raise
    finally:
        # Siempre limpiar el portapapeles al finalizar
        clear_clipboard()
    return {}