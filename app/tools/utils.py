import os
import json
import requests
import logging
import openai
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.config.settings import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def research(query: str) -> Dict[str, Any]:
    """Realiza búsquedas web usando Serper API"""
    url = "https://google.serper.dev/search"
    
    logger.info(f"Realizando búsqueda en tiempo real para: {query}")
    
    if not Config.SERPER_API_KEY:
        logger.error("No se encontró SERPER_API_KEY")
        return {"error": "Falta configurar SERPER_API_KEY"}

    headers = {
        'X-API-KEY': Config.SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Búsqueda en español
    spanish_payload = {
        "q": query,
        "gl": "es",
        "hl": "es"
    }
    
    try:
        logger.info("Enviando solicitud a Serper API...")
        response = requests.post(url, headers=headers, json=spanish_payload)
        
        if response.status_code == 200:
            results = response.json()
            logger.info(f"Búsqueda exitosa: {len(results.get('organic', []))} resultados encontrados")
            return {
                "spanish_results": results.get('organic', []),
                "total_results": len(results.get('organic', [])),
                "metadata": {
                    "query": query,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            logger.error(error_msg)
            return {"error": error_msg}
            
    except Exception as e:
        logger.error(f"Error en la búsqueda: {str(e)}")
        return {"error": str(e)}

def translate_to_english(text: str) -> str:
    """Traduce el texto al inglés usando OpenAI"""
    try:
        messages = [
            {"role": "system", "content": "You are a translator. Translate the following text to English, maintaining key terms and context."},
            {"role": "user", "content": f"Translate to English: {text}"}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
            api_key=Config.OPENAI_API_KEY
        )
        
        translated_text = response.choices[0].message.content.strip()
        logger.info(f"Texto traducido: {text} -> {translated_text}")
        return translated_text
        
    except Exception as e:
        logger.error(f"Error en la traducción: {str(e)}")
        return text

def scrape_website(url: str) -> str:
    """Extrae contenido de una página web en cualquier idioma"""
    try:
        logger.info(f"Intentando extraer contenido de: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Detectar codificación
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Eliminar elementos no deseados
        for element in soup(['script', 'style', 'iframe', 'nav', 'footer']):
            element.decompose()
            
        # Extraer texto
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'article'])
        text = ' '.join([elem.get_text().strip() for elem in text_elements])
        text = ' '.join(text.split())
        
        logger.info(f"Contenido extraído exitosamente: {len(text)} caracteres")
        
        # Detectar idioma
        detected_lang = detect_language(text[:100])
        
        return {
            'content': text[:5000],
            'language': detected_lang,
            'url': url,
            'length': len(text)
        }
        
    except Exception as e:
        logger.error(f"Error al extraer contenido: {str(e)}")
        return f"Error al extraer contenido: {str(e)}"

def detect_language(text: str) -> str:
    """Detecta el idioma del texto usando OpenAI"""
    try:
        messages = [
            {"role": "system", "content": "You are a language detector. Respond with only 'en' for English or 'es' for Spanish."},
            {"role": "user", "content": f"Detect language: {text}"}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
            api_key=Config.OPENAI_API_KEY
        )
        
        detected_lang = response.choices[0].message.content.strip().lower()
        return detected_lang if detected_lang in ['en', 'es'] else 'unknown'
        
    except Exception as e:
        logger.error(f"Error en la detección de idioma: {str(e)}")
        return 'unknown'

def write_content(topic: str, content_type: str = "article", 
                 research_results: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Genera contenido basado en un tema y resultados de investigación"""
    try:
        logger.info(f"Generando contenido para: {topic}")
        
        if research_results is None:
            research_results = research(topic)
        
        content = {
            "topic": topic,
            "type": content_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "research_summary": [],
            "sources": []
        }
        
        # Procesar resultados en español
        if "spanish_results" in research_results:
            for result in research_results["spanish_results"][:3]:
                content["research_summary"].append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", ""),
                    "language": "es"
                })
                content["sources"].append(result.get("link", ""))
        
        # Procesar resultados en inglés
        if "english_results" in research_results:
            for result in research_results["english_results"][:3]:
                content["research_summary"].append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", ""),
                    "language": "en"
                })
                content["sources"].append(result.get("link", ""))
                
        # Intentar extraer contenido adicional de las fuentes
        for source in content["sources"]:
            try:
                webpage_content = scrape_website(source)
                if isinstance(webpage_content, dict) and 'content' in webpage_content:
                    content["research_summary"].append({
                        "detailed_content": webpage_content['content'],
                        "language": webpage_content['language'],
                        "source": source
                    })
            except Exception as e:
                logger.warning(f"No se pudo extraer contenido detallado de {source}: {str(e)}")
        
        logger.info("Contenido generado exitosamente")
        return content
        
    except Exception as e:
        logger.error(f"Error generando contenido: {str(e)}")
        return {"error": f"Error generando contenido: {str(e)}"}

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analiza el sentimiento del texto usando OpenAI"""
    try:
        messages = [
            {"role": "system", "content": "Analyze the sentiment of the following text and respond with a JSON containing 'sentiment' (positive, negative, or neutral) and 'confidence' (0-1)."},
            {"role": "user", "content": text}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.1,
            api_key=Config.OPENAI_API_KEY
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.info(f"Análisis de sentimiento completado: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error en el análisis de sentimiento: {str(e)}")
        return {"sentiment": "unknown", "confidence": 0.0, "error": str(e)}