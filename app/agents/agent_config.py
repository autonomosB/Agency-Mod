from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from app.config.settings import Config
from app.tools.utils import research, write_content, scrape_website, analyze_sentiment
import logging

logger = logging.getLogger(__name__)

class AgentFactory:
    @staticmethod
    def create_agents(brand_task: str, user_task: str):
        try:
            logger.info(f"Creando agentes para: {brand_task} - {user_task}")
            
            llm_config = {
                "seed": 42,
                "config_list": Config.get_openai_config(),
                "temperature": 0.7,
            }

            # Crear User Proxy Agent
            user_proxy = UserProxyAgent(
                name="User_Proxy",
                system_message="Un proxy para interactuar con el usuario y coordinar las tareas.",
                human_input_mode="NEVER",
                code_execution_config={"use_docker": False},
                llm_config=llm_config
            )

            # Crear Research Agent
            researcher = AssistantAgent(
                name="Agency_Researcher",
                llm_config=llm_config,
                system_message=f'''
                Como Investigador Principal para {brand_task}, tu tarea es:
                1. Investigar sobre {user_task} usando fuentes actualizadas
                2. Analizar la competencia y tendencias del mercado
                3. Proporcionar datos y estadísticas relevantes
                4. Identificar oportunidades y amenazas
                ''',
                function_map={
                    "research": research,
                    "scrape_website": scrape_website,
                    "analyze_sentiment": analyze_sentiment
                }
            )

            # Crear Content Writer Agent
            writer = AssistantAgent(
                name="Agency_Writer",
                llm_config=llm_config,
                system_message=f'''
                Como Redactor Creativo para {brand_task}, tu tarea es:
                1. Crear contenido persuasivo y relevante sobre {user_task}
                2. Adaptar el mensaje al público objetivo
                3. Incorporar datos de la investigación en el contenido
                4. Optimizar el contenido para SEO
                ''',
                function_map={"write_content": write_content}
            )

            # Crear Project Manager Agent
            manager = AssistantAgent(
                name="Agency_Manager",
                llm_config=llm_config,
                system_message=f'''
                Como Gerente de Proyecto para {brand_task}, tu tarea es:
                1. Coordinar el equipo para resolver {user_task}
                2. Asegurar que las soluciones sean prácticas y efectivas
                3. Priorizar tareas y recursos
                4. Proporcionar un plan de acción claro
                '''
            )

            # Configurar Group Chat
            groupchat = GroupChat(
                agents=[user_proxy, manager, researcher, writer],
                messages=[],
                max_round=20
            )

            # Configurar Group Chat Manager
            chat_manager = GroupChatManager(
                groupchat=groupchat,
                llm_config=llm_config
            )

            logger.info("Agentes creados exitosamente")
            return {
                "user_proxy": user_proxy,
                "manager": chat_manager,
                "groupchat": groupchat
            }

        except Exception as e:
            logger.error(f"Error creando agentes: {str(e)}")
            raise