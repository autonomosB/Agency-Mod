from flask import Blueprint, request, jsonify, render_template
from app.agents.agent_config import AgentFactory
from app.tools.utils import research
from datetime import datetime
from typing import List, Dict, Any
import logging
import traceback

logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/analyze', methods=['POST'])
def analyze_task():
    try:
        logger.info("Recibiendo nueva solicitud de análisis")
        
        if not request.is_json:
            logger.error("La solicitud no contiene JSON")
            return jsonify({'error': 'La solicitud debe ser JSON'}), 400
            
        data = request.get_json()
        logger.info(f"Datos recibidos: {data}")
        
        brand_task = data.get('brand_task')
        user_task = data.get('user_task')

        if not brand_task or not user_task:
            logger.warning("Solicitud incompleta: faltan campos requeridos")
            return jsonify({'error': 'Faltan campos requeridos'}), 400

        # Realizar búsqueda en tiempo real
        search_query = f"{brand_task} {user_task}"
        logger.info(f"Iniciando búsqueda para: {search_query}")
        search_results = research(search_query)
        
        if "error" in search_results:
            logger.error(f"Error en la búsqueda: {search_results['error']}")
            return jsonify({'error': f"Error en la búsqueda: {search_results['error']}"}), 500

        # Crear instancia de agentes con los resultados de la búsqueda
        agents = AgentFactory.create_agents(brand_task, user_task)
        
        # Preparar el mensaje inicial incluyendo los resultados de la búsqueda
        initial_message = f"""
        Analiza y proporciona estrategias para: {user_task}
        Contexto de la empresa/marca: {brand_task}
        
        Resultados de la investigación en tiempo real:
        
        Resultados en español:
        {format_search_results(search_results.get('spanish_results', []))}
        
        Resultados en inglés:
        {format_search_results(search_results.get('english_results', []))}
        
        Por favor, proporciona:
        1. Análisis de la situación actual basado en la investigación
        2. Estrategias recomendadas
        3. Plan de acción detallado
        4. Métricas de éxito sugeridas
        """
        
        logger.info("Iniciando conversación con los agentes")
        chat_response = agents["user_proxy"].initiate_chat(
            agents["manager"],
            message=initial_message,
        )
        
        # Procesar y formatear la respuesta
        formatted_response = {
            'status': 'success',
            'brand_task': brand_task,
            'user_task': user_task,
            'search_results': search_results,
            'response': chat_response,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info("Análisis completado exitosamente")
        return jsonify(formatted_response)
    
    except Exception as e:
        logger.error(f"Error durante el análisis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': f"Error en el servidor: {str(e)}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 500

def format_search_results(results: List[Dict]) -> str:
    """Formatea los resultados de búsqueda para incluirlos en el mensaje"""
    formatted = []
    for i, result in enumerate(results, 1):
        formatted.append(f"{i}. {result.get('title', 'Sin título')}")
        formatted.append(f"   URL: {result.get('link', 'No disponible')}")
        formatted.append(f"   Resumen: {result.get('snippet', 'No disponible')}\n")
    return "\n".join(formatted) if formatted else "No se encontraron resultados."

@main.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar el estado de la API"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }), 200
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return jsonify({'error': str(e)}), 500