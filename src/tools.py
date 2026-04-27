import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

# ==========================================
# 🧠 MOTOR CENTRAL DE CONEXIÓN MCP
# ==========================================
def _call_mcp(tool_name: str, arguments: dict):
    """Función centralizada para llamar a cualquier endpoint de tu servidor MCP."""
    url = os.getenv("MCP_URL")
    api_key = os.getenv("MCP_API_KEY")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        if "error" in data:
            return f"Error del MCP ({tool_name}): {data['error']}"
            
        content = data.get("result", {}).get("content", [])
        return str(content) if content else "Ejecutado correctamente, pero no devolvió datos."
        
    except requests.exceptions.RequestException as e:
        return f"Error de conexión con el servidor MCP al llamar {tool_name}: {str(e)}"

# ==========================================
# ⚽ TOOLS DE FÚTBOL
# ==========================================

@tool
def futbol_api_get_matches(date: str = None, status: str = None):
    """Fixture y Resultados. Filtros opcionales: date (YYYY-MM-DD), status (SCHEDULED, LIVE, FINISHED)."""
    args = {}
    if date: args["date"] = date
    if status: args["status"] = status
    return _call_mcp("futbol_api_get_matches", args)

@tool
def futbol_api_get_teams_teamId(teamId: str):
    """Perfil del Equipo."""
    return _call_mcp("futbol_api_get_teams_teamId", {"teamId": teamId})

@tool
def futbol_api_get_teams_teamId_roster(teamId: str):
    """Plantilla de Jugadores."""
    return _call_mcp("futbol_api_get_teams_teamId_roster", {"teamId": teamId})

@tool
def futbol_api_get_tournaments():
    """Listar Torneos disponibles."""
    return _call_mcp("futbol_api_get_tournaments", {})

@tool
def futbol_api_get_tournaments_tournamentId_standings(tournamentId: str):
    """Tabla de Posiciones de un torneo."""
    return _call_mcp("futbol_api_get_tournaments_tournamentId_standings", {"tournamentId": tournamentId})

# ==========================================
# 🌤️ TOOLS DE TIEMPO (CLIMA)
# ==========================================

@tool
def tiempo_api_get_current_city(city: str, units: str = None):
    """Obtener clima actual por ciudad (ej. madrid, london)."""
    args = {"city": city}
    if units: args["units"] = units
    return _call_mcp("tiempo_api_get_current_city", args)

@tool
def tiempo_api_get_forecast_lat_lon(lat: float, lon: float, days: int = None):
    """Pronóstico para coordenadas específicas."""
    args = {"lat": lat, "lon": lon}
    if days: args["days"] = days
    return _call_mcp("tiempo_api_get_forecast_lat_lon", args)

# ==========================================
# 🚆 TOOLS DE TRANSPORTE
# ==========================================

@tool
def transporte_mcp_get_horarios(origen: str, destino: str, fecha: str):
    """Consultar horarios de tren."""
    return _call_mcp("transporte_mcp_get_horarios", {"origen": origen, "destino": destino, "fecha": fecha})

@tool
def transporte_mcp_get_tickets_precios(origen: str, destino: str):
    """Consultar precios de tickets."""
    return _call_mcp("transporte_mcp_get_tickets_precios", {"origen": origen, "destino": destino})

# ==========================================
# 🎓 TOOLS DE ESTUDIANTES
# ==========================================

@tool
def student_mcp_post_students():
    """Register a new student."""
    return _call_mcp("student_mcp_post_students", {})

@tool
def student_mcp_get_students(academicLevel: str = None, status: str = None):
    """List students. Filtros opcionales: academicLevel, status."""
    args = {}
    if academicLevel: args["academicLevel"] = academicLevel
    if status: args["status"] = status
    return _call_mcp("student_mcp_get_students", args)

@tool
def student_mcp_post_courses():
    """Create a new course instance."""
    return _call_mcp("student_mcp_post_courses", {})

@tool
def student_mcp_post_courses_courseId_attendance(courseId: str):
    """Submit daily attendance for a course."""
    return _call_mcp("student_mcp_post_courses_courseId_attendance", {"courseId": courseId})

@tool
def student_mcp_post_courses_courseId_grades(courseId: str):
    """Submit grades for a course."""
    return _call_mcp("student_mcp_post_courses_courseId_grades", {"courseId": courseId})