# flask_main.py
import os
import re
import time
import json
import qrcode
import requests
import threading
import subprocess
import unicodedata
from flask_cors import CORS
from flask import Flask, request, jsonify

from petitions import run_chatgpt
from router import verificar_ruta_almacenamiento
from dependencies import instalar_ngrok_debian, descargar_chrome_webdriver_debian

# Uso de utilidades
from utils import Sistema
consola = Sistema.Consola()
color = Sistema.Colores()
contador = Sistema.Contador()





'''
>>> Variable global para tracking del estado
'''
processing_status = {
    'is_processing': False,
    'current_prompt': None,
    'start_time': None
}





'''
>>> Funciones auxiliares
'''
def print_qr_code(url):
    """ Genera y muestra un QR code en la terminal """
    qr = qrcode.QRCode(version=1, box_size=1, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    
    # Crear el QR code con caracteres ASCII
    matrix = qr.get_matrix()
    for row in matrix:
        line = ''
        for cell in row:
            if cell:
                line += '██'  # Carácter lleno para módulos negros
            else:
                line += '  '  # Espacio para módulos blancos
        print(line)

def sanitize_text(text):
    """ Sanitización de texto """
    if not isinstance(text, str):
        return text
    
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def sanitize_json(data):
    """ Recorre recursivamente un diccionario o lista para sanitizar todos los strings """
    if isinstance(data, dict):
        return {key: sanitize_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_json(item) for item in data]
    elif isinstance(data, str):
        return sanitize_text(data)
    return data

def gestionar_ngrok(puerto=5000):
    """ Función para manejar Ngrok """
    try:
        # Matar cualquier proceso previo de ngrok en este puerto
        subprocess.run(["pkill", "-f", f"ngrok http {puerto}"], stderr=subprocess.DEVNULL)
        
        # Iniciar nueva instancia de ngrok
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", str(puerto)],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        print(f" - Ngrok iniciado en puerto {puerto}")
        time.sleep(3)
        
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            tunnels = response.json()
            for tunnel in tunnels['tunnels']:
                if tunnel['proto'] == 'https':
                    url = tunnel['public_url']
                    print(f" - URL Pública (Enlace): {url}")
                    print(" - URL Pública (QR Code):")
                    print_qr_code(url)
                    return tunnel['public_url']
        except Exception as e:
            print(f" - Error obteniendo URL de Ngrok: {e}")
    except Exception as e:
        print(f" - Error iniciando Ngrok: {e}")
    return None





'''
>>> Funciones de guardado y carga
'''
def write_petition(prompt):
    """ Escribe el prompt en el archivo JSON con el formato solicitado """
    json_r = os.path.join(verificar_ruta_almacenamiento(), 'petition.json')
    data = {"prompts": [prompt]}
    with open(json_r, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_last_json():
    """Carga el archivo JSON de conversación más reciente del directorio"""
    
    # Construir la ruta base
    base_folder = os.path.join(verificar_ruta_almacenamiento(), 'GPT', 'Conversations')
    
    # Obtener lista de archivos JSON con metadatos de última modificación
    archivos = []
    for archivo in os.listdir(base_folder):
        if archivo.endswith('.json'):
            ruta_archivo = os.path.join(base_folder, archivo)
            archivos.append((ruta_archivo, os.path.getmtime(ruta_archivo)))

    # Retorna un diccionario vacío si no hay archivos
    if len(archivos) == 0:
        return {}

    # Ordenar por fecha de modificación (más reciente primero)
    archivos.sort(key=lambda x: x[1], reverse=True)
    ultimo_json = archivos[0][0]

    # Intentar cargar el contenido del archivo JSON
    try:
        with open(ultimo_json, "r", encoding="utf-8") as json_data:
            datos_json = json.load(json_data)
            return sanitize_json(datos_json)
    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        return {}





'''
>>> Funciones de procesamiento
'''
def run_processing(prompts_file, save_path):
    """ Ejecuta la instalación de dependencias y automatización de ChatGPT en segundo plano """
    global processing_status
    
    try:
        instalar_ngrok_debian()
        descargar_chrome_webdriver_debian()
        
        run_chatgpt(
            prompts_file = prompts_file,
            save_path = save_path,
            clean_pastData = True
        )
        
        # Actualizar estado cuando termine
        processing_status['is_processing'] = False
        processing_status['current_prompt'] = None
        processing_status['start_time'] = None
        
    except Exception as e:
        print(f" - Error en procesamiento: {e}")
        
        # También actualizar estado en caso de error
        processing_status['is_processing'] = False
        processing_status['current_prompt'] = None
        processing_status['start_time'] = None





'''
>>> Configuración de Flask
'''
app = Flask(__name__)
#CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})
""" CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST"],
        "allow_headers": [
            "Content-Type",
            "Accept",
            "ngrok-skip-browser-warning",
            "User-Agent"
        ]
    }
}) """

@app.route('/execute', methods=['POST'])
def handle_prompt():
    global processing_status
    
    # Verificar si ya hay un procesamiento en curso
    if processing_status['is_processing']:
        return jsonify({
            "status": "wait",
            "message": "Hay un prompt siendo procesado actualmente",
            "current_prompt": processing_status['current_prompt'],
            "start_time": processing_status['start_time']
        }), 409
    
    # Obtener y sanitizar el prompt
    data = request.get_json()
    prompt = data.get('--prompt', '')
    sanitized_prompt = sanitize_text(prompt)
    
    # 1. Imprimir en consola
    print(color.color_verde() + f"\n [OK] Prompt recibido: '{sanitized_prompt}'" + color.color_reset())
    
    # 2. Escribir en JSON
    try:
        write_petition(sanitized_prompt)
        print(color.color_gris() + " [OK] Prompt guardado localmente" + color.color_reset())
    except Exception as e:
        print(color.color_rojo() + f" - Error escribiendo JSON: {e}" + color.color_reset())
        return jsonify({
            "status": "error",
            "message": "Error al guardar el prompt"
        }), 500
    
    # 3. Ejecutar el procesamiento en segundo plano
    try:
        # Actualizar estado global
        processing_status['is_processing'] = True
        processing_status['current_prompt'] = sanitized_prompt
        processing_status['start_time'] = time.time()
        
        # Configurar rutas
        prompts_file = os.path.join(verificar_ruta_almacenamiento(), 'petition.json')
        save_path = os.path.join(verificar_ruta_almacenamiento(), 'GPT')
        
        # Ejecutar en un hilo separado
        processing_thread = threading.Thread(
            target = run_processing,
            kwargs = {
                'prompts_file': prompts_file,
                'save_path': save_path
            }
        )
        processing_thread.start()
        
        print(color.color_gris() + " [OK] Procesamiento iniciado en segundo plano" + color.color_reset())
        
        return jsonify({
            "status": "processing",
            "received_prompt": sanitized_prompt,
            "message": "Prompt recibido y en procesamiento"
        })
    except Exception as e:
        processing_status['is_processing'] = False
        processing_status['current_prompt'] = None
        processing_status['start_time'] = None
        
        print(color.color_rojo() + f" - Error al iniciar procesamiento: {e}" + color.color_reset())
        return jsonify({
            "status": "error",
            "message": "Error al iniciar el procesamiento"
        }), 500





'''
>>> Definición de endpoints
'''
@app.route('/status', methods=['GET'])
def check_status():
    """ Endpoint para verificar el estado del procesamiento """
    return jsonify({
        "is_processing": processing_status['is_processing'],
        "current_prompt": processing_status['current_prompt'],
        "start_time": processing_status['start_time']
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    """ Endpoint para obtener todos los datos de la última conversación """
    chatgpt_data = load_last_json()
    if not chatgpt_data:
        return jsonify({
            "status": "error",
            "message": "No hay datos disponibles"
        }), 404
    return jsonify(chatgpt_data)

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """ Endpoint para obtener solo las conversaciones """
    chatgpt_data = load_last_json()
    conversations = chatgpt_data.get("conversations", [])
    if not conversations:
        return jsonify({
            "status": "error",
            "message": "No hay respuestas disponibles"
        }), 404
    return jsonify(conversations)

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """ Endpoint para obtener solo la metadata """
    chatgpt_data = load_last_json()
    metadata = chatgpt_data.get("metadata", {})
    if not metadata:
        return jsonify({
            "status": "error",
            "message": "No hay metadata disponible"
        }), 404
    return jsonify(metadata)





'''
>>> Inicializar servidor
'''
if __name__ == '__main__':
    #consola.limpiar_consola()
    
    # Iniciar Ngrok en segundo plano
    ngrok_thread = threading.Thread(target=gestionar_ngrok)
    ngrok_thread.daemon = True
    ngrok_thread.start()
    
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=False)