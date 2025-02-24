# router.py
import os
import platform





'''
>>> Funciones utilitarias
'''
def clear_clipboard():
    """ Limpia el contenido del portapapeles de forma multiplataforma usando herramientas nativas. """
    system = platform.system()

    if system == "Windows":
        # Comando para limpiar el portapapeles en Windows
        os.system("echo off | clip")
    elif system == "Darwin":  # macOS
        # Comando para limpiar el portapapeles en macOS
        os.system("pbcopy < /dev/null")
    elif system == "Linux":
        # Comando para limpiar el portapapeles en Linux (requiere xclip o xsel)
        os.system("xclip -selection clipboard < /dev/null 2>/dev/null || xsel --clear --clipboard")
    else:
        raise NotImplementedError(f"No se soporta la limpieza del portapapeles en el sistema operativo: {system}")





'''
>>> Rutas de almacenamiento general
'''
def verificar_ruta_almacenamiento():
    storage_path = os.path.join('Storage')
    
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    return storage_path





'''
>>> Rutas para almacenamiento de información y datasets
'''
def verificar_ruta_data():
    data_path = os.path.join('DATA')
    
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    return data_path