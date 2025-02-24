# tool_sessionCreator.py
import os
import sys

from router import verificar_ruta_almacenamiento

from chatGPT.session_manager import ChatGPTSessionManager





if __name__ == '__main__':
    # Rutas
    chrome_path = "/usr/bin/google-chrome"
    save_route = os.path.join(verificar_ruta_almacenamiento(), 'GPT')
    sessions_path = os.path.join(save_route, 'Sessions')
    
    # Crear directorios si no existen
    for path in [save_route, sessions_path]:
        if not os.path.exists(path):
            os.makedirs(path)
    
    try:
        # Inicializar gestor de sesiones
        session_manager = ChatGPTSessionManager(
            sessions_base_path = sessions_path,
            chrome_path = chrome_path
        )
        
        # Iniciar proceso interactivo de creación de sesiones
        session_manager.create_sessions_interactive()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)