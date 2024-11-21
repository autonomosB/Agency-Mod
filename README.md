# Go Chile Agency Bot

Bot de asistencia para estrategias de marketing digital y análisis de datos.

## Características
- Búsqueda en tiempo real usando Serper API
- Sistema de agentes múltiples para análisis y recomendaciones
- Soporte bilingüe (español e inglés)
- Generación de estrategias personalizadas

## Instalación

1. Clonar el repositorio:
bash
git clone https://github.com/tu-usuario/go-chile-bot.git
cd go-chile-bot

2. Crear entorno virtual:

bash
python -m venv venv
source venv/bin/activate # En Windows: venv\Scripts\activate


3. Instalar dependencias:
bash
pip install -r requirements.txt

4. Configurar variables de entorno:
Crear archivo `.env` con:

text
OPENAI_API_KEY=tu_api_key
SERPER_API_KEY=tu_api_key

## Uso
bash
python run.py

## Estructura del Proyecto

go-chile-bot/
├── app/
│ ├── init.py
│ ├── api/
│ ├── agents/
│ ├── config/
│ └── tools/
├── tests/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── run.py


## Contribuir
1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request