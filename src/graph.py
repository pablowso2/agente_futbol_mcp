import os
import warnings
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

# Ocultar advertencias de compatibilidad de Langchain/Pydantic
warnings.filterwarnings("ignore", category=UserWarning)

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# IMPORTAMOS TODAS LAS 14 HERRAMIENTAS DE tools.py
from tools import (
    futbol_api_get_matches,
    futbol_api_get_teams_teamId,
    futbol_api_get_teams_teamId_roster,
    futbol_api_get_tournaments,
    futbol_api_get_tournaments_tournamentId_standings,
    tiempo_api_get_current_city,
    tiempo_api_get_forecast_lat_lon,
    transporte_mcp_get_horarios,
    transporte_mcp_get_tickets_precios,
    student_mcp_post_students,
    student_mcp_get_students,
    student_mcp_post_courses,
    student_mcp_post_courses_courseId_attendance,
    student_mcp_post_courses_courseId_grades
)

load_dotenv()

# 1. Definimos el Estado (Memoria del agente)
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Lista completa de herramientas (El "arsenal" del Agente)
tools = [
    futbol_api_get_matches,
    futbol_api_get_teams_teamId,
    futbol_api_get_teams_teamId_roster,
    futbol_api_get_tournaments,
    futbol_api_get_tournaments_tournamentId_standings,
    tiempo_api_get_current_city,
    tiempo_api_get_forecast_lat_lon,
    transporte_mcp_get_horarios,
    transporte_mcp_get_tickets_precios,
    student_mcp_post_students,
    student_mcp_get_students,
    student_mcp_post_courses,
    student_mcp_post_courses_courseId_attendance,
    student_mcp_post_courses_courseId_grades
]

# 3. Inicialización del modelo Llama 3.1 local
llm = ChatOllama(
    model="llama3.1:latest",
    temperature=0.2,
    base_url=os.getenv("OLLAMA_BASE_URL")
)

# Enlazamos las herramientas al modelo para que sepa qué puede hacer
llm_with_tools = llm.bind_tools(tools)

# 4. Nodo de razonamiento del Chatbot
def chatbot_node(state: State):
    """Evalúa los mensajes del usuario y decide si responder o usar una herramienta."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 5. Construcción del Grafo
graph_builder = StateGraph(State)

# Añadimos los nodos principales
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("tools", ToolNode(tools=tools))

# Definimos el flujo inicial
graph_builder.add_edge(START, "chatbot")

# Flujo condicional: Si decide usar una tool, va al nodo 'tools', si no, termina.
graph_builder.add_conditional_edges("chatbot", tools_condition)

# Después de usar la herramienta, SIEMPRE vuelve al chatbot para analizar la respuesta
graph_builder.add_edge("tools", "chatbot")

# 6. Compilamos la aplicación
app = graph_builder.compile()