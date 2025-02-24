# utils.py
import os
import time
import psutil
import platform
import colorama
from time import perf_counter_ns





class Sistema:
    class Procesador:
        def nucleos_ideales(self):
            # Obtener la cantidad total de núcleos disponibles en la computadora
            cantidad_total_nucleos = os.cpu_count()
            
            # Obtener el porcentaje de uso de la CPU
            uso_cpu = psutil.cpu_percent()
            
            # Definir la cantidad ideal como la mitad de los núcleos disponibles
            cantidad_ideal_nucleos = cantidad_total_nucleos // 2
            
            # Ajustar la cantidad ideal según el porcentaje de uso de la CPU
            if uso_cpu > 70:
                cantidad_ideal_nucleos -= 1
            elif uso_cpu < 30:
                cantidad_ideal_nucleos += 1
            
            # Asegurarse de que la cantidad ideal esté en un rango razonable
            cantidad_ideal_nucleos = max(1, min(cantidad_total_nucleos, cantidad_ideal_nucleos))
            return int(cantidad_ideal_nucleos)
    class Consola:
        def limpiar_consola(self):
            if platform.system() == 'Windows':
                return os.system('cls')
            else:
                return os.system('clear')
    class Colores:
        def color_blanco(self):
            return colorama.Fore.LIGHTWHITE_EX + colorama.Style.BRIGHT
        def color_gris(self):
            return colorama.Fore.LIGHTBLACK_EX + colorama.Style.BRIGHT
        def color_rojo(self):
            return colorama.Fore.LIGHTRED_EX + colorama.Style.BRIGHT
        def color_verde(self):
            return colorama.Fore.LIGHTGREEN_EX + colorama.Style.BRIGHT
        def color_azul(self):
            return colorama.Fore.LIGHTBLUE_EX + colorama.Style.BRIGHT
        def color_amarillo(self):
            return colorama.Fore.LIGHTYELLOW_EX + colorama.Style.BRIGHT
        def color_magenta(self):
            return colorama.Fore.LIGHTMAGENTA_EX + colorama.Style.BRIGHT
        def color_cyan(self):
            return colorama.Fore.LIGHTCYAN_EX + colorama.Style.BRIGHT
        def color_reset(self):
            return colorama.Fore.RESET + colorama.Style.RESET_ALL
    class Contador:
        def __init__(self):
            self.contadores = {}
            
        def iniciar_contador(self, nombre='default'):
            """Inicia un nuevo contador con el nombre especificado"""
            self.contadores[nombre] = perf_counter_ns()
            return self
            
        def finalizar_contador(self, nombre='default'):
            """Finaliza el contador especificado e imprime el tiempo transcurrido"""
            if nombre not in self.contadores:
                raise ValueError(f" - ERROR EN CONTADOR: No existe un contador con el nombre {nombre}")
                
            # Colores customizados
            w = colorama.Back.LIGHTBLACK_EX + colorama.Fore.LIGHTWHITE_EX + colorama.Style.BRIGHT
            c0 = colorama.Back.LIGHTYELLOW_EX + colorama.Fore.BLACK + colorama.Style.BRIGHT
            c1 = colorama.Back.LIGHTWHITE_EX + colorama.Fore.BLACK + colorama.Style.BRIGHT
            c2 = colorama.Back.LIGHTMAGENTA_EX + colorama.Fore.WHITE + colorama.Style.BRIGHT
            r = colorama.Back.RESET + colorama.Fore.RESET + colorama.Style.RESET_ALL
            
            # Calculamos el tiempo transcurrido en nanosegundos
            tiempo_final = perf_counter_ns()
            total_ns = tiempo_final - self.contadores[nombre]
            total = total_ns / 1_000_000_000  # Convertimos a segundos
            
            # Cálculos más precisos usando divisiones enteras
            dias = int(total // 86400)
            horas = int((total % 86400) // 3600)
            minutos = int((total % 3600) // 60)
            segundos = int(total % 60)
            
            # Cálculos para fracciones de segundo usando el valor en nanosegundos
            milisegundos = int((total_ns % 1_000_000_000) // 1_000_000)
            microsegundos = int((total_ns % 1_000_000) // 1_000)
            nanosegundos = int(total_ns % 1_000)
            
            # Cálculos teóricos para unidades más pequeñas
            picosegundos = int((total_ns * 1_000) % 1_000)
            femtosegundos = int((total_ns * 1_000_000) % 1_000)
            attosegundos = int((total_ns * 1_000_000_000) % 1_000)
            
            # Imprimimos directamente el resultado con el formato deseado
            print(f" {w}[ Tiempo de finalización ➤ '{nombre}' ]{r} " + c0 + f'{dias}d:{horas}h:{minutos}m:{segundos}s:{milisegundos}ms' + 
                  c1 + f':{microsegundos}μs:{nanosegundos}ns:{picosegundos}ps' + 
                  c2 + f':{femtosegundos}fs:{attosegundos}as' + r)
            
            # Limpiamos el contador usado
            del self.contadores[nombre]
        def glosario_de_medidas(self):
            # Color customizado
            print(colorama.Back.LIGHTBLACK_EX + colorama.Fore.LIGHTGREEN_EX + colorama.Style.BRIGHT)
            print("[ Medidas de tiempo ]")
            print(" - d: Se refiere a días.                          ")
            print(" - h: Se refiere a horas.                         ")
            print(" - m: Se refiere a minutos.                       ")
            print(" - s: Se refiere a segundos.                      ")
            print(" - ms: Se refiere a milisegundos.                 ")
            print(" - μs: Se refiere a microsegundos.                ")
            print(" - ns: Se refiere a nanosegundos.                 ")
            print(" - ps: Se refiere a picosegundos.                 ")
            print(" - fs: Se refiere a femtosegundos.                ")
            print(" - as: Se refiere a attosegundos (medida aprox.). ")
            print(colorama.Back.RESET + colorama.Fore.RESET + colorama.Style.RESET_ALL)
            return ''