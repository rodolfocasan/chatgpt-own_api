# Automatización de ChatGPT con Selenium y API Casera

Este proyecto implementa una automatización de ChatGPT usando Selenium WebDriver y crea una API HTTP personalizada utilizando Flask y Ngrok. Permite enviar prompts a ChatGPT y obtener respuestas de manera automatizada, gestionando múltiples sesiones y manejando límites de uso.

## Características Principales

- Automatización completa de ChatGPT usando Selenium WebDriver
- API HTTP personalizada con Flask para enviar prompts y recibir respuestas
- Túnel seguro con Ngrok para acceso remoto
- Sistema de gestión de múltiples sesiones de Chrome
- Manejo automático de CAPTCHAs mediante cambio de sesión
- Guardado automático de conversaciones en formato JSON
- Sistema de reintentos y recuperación de errores
- Monitoreo del estado de procesamiento
- Generación de códigos QR para acceso rápido

## Requisitos del Sistema

- Python 3.x
- Google Chrome
- ChromeDriver
- Ngrok
- Conexión a Internet estable

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/rodolfocasan/chatgpt-own_api.git
cd chatgpt-own_api
```

2. Instala las dependencias:
```bash
pip3 install -r DOCs/requirements.txt
```

3. Configura las variables de entorno o rutas necesarias para:
   - Chrome
   - ChromeDriver
   - Directorio de sesiones
   - Directorios de almacenamiento

## Estructura del Proyecto

```
/
├── chatGPT/
│   └── req.py            # Clase principal de automatización
├── flask_main.py         # Servidor Flask y API
├── petitions.py          # Manejo de peticiones
├── router.py            # Gestión de rutas
├── dependencies.py      # Instalación de dependencias
└── utils/               # Utilidades y helpers
```

## Uso

### Iniciar el Servidor

```bash
python3 flask_main.py
```

El servidor generará automáticamente:
- URL local en puerto 5000
- URL pública de Ngrok
- Código QR para acceso rápido

### Endpoints Disponibles

#### POST /execute
Envía un nuevo prompt para procesamiento.

Ejemplo de respuesta:
```json
{
    "status": "processing",
    "received_prompt": "¿Cuál es la capital de Francia?",
    "message": "Prompt recibido y en procesamiento"
}
```

#### GET /status
Verifica el estado del procesamiento actual.

Ejemplo de respuesta:
```json
{
    "is_processing": true,
    "current_prompt": "¿Cuál es la capital de Francia?",
    "start_time": 1708732800.123
}
```

#### GET /api/data
Obtiene todos los datos de la última conversación.

Ejemplo de respuesta:
```json
{
    "metadata": {
        "timestamp": "2024-02-23T15:30:00",
        "sessions_used": ["session_1", "session_2"]
    },
    "conversations": [
        {
            "timestamp": "2024-02-23T15:30:00",
            "session": "session_1",
            "prompt": "¿Cuál es la capital de Francia?",
            "response": "La capital de Francia es París."
        }
    ]
}
```

#### GET /api/conversations
Obtiene solo las conversaciones.

Ejemplo de respuesta:
```json
[
    {
        "timestamp": "2024-02-23T15:30:00",
        "session": "session_1",
        "prompt": "¿Cuál es la capital de Francia?",
        "response": "La capital de Francia es París."
    }
]
```

#### GET /api/metadata
Obtiene solo los metadatos.

Ejemplo de respuesta:
```json
{
    "timestamp": "2024-02-23T15:30:00",
    "sessions_used": ["session_1", "session_2"]
}
```

## Características de Seguridad

- Manejo automático de sesiones agotadas
- Sanitización de inputs y outputs
- Gestión de errores y excepciones
- Sistema de reintentos configurable
- Guardado automático de progreso

## Manejo de Sesiones

El sistema gestiona múltiples sesiones de Chrome para:
- Evitar límites de uso
- Manejar CAPTCHAs automáticamente
- Mantener conversaciones independientes
- Recuperarse de errores de sesión

## Almacenamiento de Datos

Las conversaciones se almacenan en formato JSON con:
- Timestamps
- Metadatos de sesión
- Prompts y respuestas
- Información de estado

## ⚠️ Advertencia

Este proyecto está diseñado exclusivamente para fines éticos y de investigación. Es importante mencionar que intencionalmente se han dejado vulnerabilidades de seguridad como medida de protección contra usos malintencionados. No se recomienda su implementación en un ambiente de producción sin las debidas modificaciones y mejoras de seguridad.

El desarrollador no se hace responsable por el mal uso o las consecuencias que puedan derivar de la implementación de este código en un entorno de producción sin las adecuadas medidas de seguridad.

# Contacto

### Contacto Profesional
Para propuestas laborales y colaboraciones profesionales:
[https://rodolfocasan.github.io/web/job](https://rodolfocasan.github.io/job)

### Contacto General
Para consultas sobre el proyecto y otras inquietudes:
[https://rodolfocasan.github.io/web/](https://rodolfocasan.github.io/)

### YouTube
¡Sígueme en YouTube para más contenido sobre desarrollo y tecnología!
[https://www.youtube.com/@rodolfocasan](https://www.youtube.com/@rodolfocasan)
