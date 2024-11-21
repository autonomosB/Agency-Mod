import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-12345')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SERPER_API_KEY = os.getenv('SERPER_API_KEY')
    DEBUG_MODE = True  # Para ver logs detallados

    @staticmethod
    def get_openai_config():
        return [{
            "model": "gpt-3.5-turbo",
            "api_key": os.getenv('OPENAI_API_KEY'),
        }]