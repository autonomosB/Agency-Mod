import os
from dotenv import load_dotenv
import requests
import json

# Cargar variables de entorno
load_dotenv()

def test_serper_api():
    # Obtener API key
    api_key = os.getenv('SERPER_API_KEY')
    print(f"API Key encontrada: {'Sí' if api_key else 'No'}")
    print(f"Longitud de la API key: {len(api_key) if api_key else 0}")
    
    # Configurar la solicitud
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        "q": "test query",
        "gl": "es",
        "hl": "es"
    }
    
    try:
        print("\nEnviando solicitud de prueba...")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"\nCódigo de estado: {response.status_code}")
        print(f"Headers de respuesta: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\nRespuesta exitosa!")
            results = response.json()
            print(json.dumps(results, indent=2))
        else:
            print(f"\nError en la respuesta: {response.text}")
            
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_serper_api()