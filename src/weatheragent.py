import requests
import base64
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_env = os.path.join(directorio_actual, ".env")
load_dotenv(ruta_env)

# Intentamos sacar la llave del .env, si no la encuentra (None), usamos el string directamente
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY") or "5355b7ec82b04b8389f155930252404"
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID") or "1611585d501f484f8e71ee0f6cd60277"
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET") or "d0fb833c48f1447cbbebfb3dcc2594c7"

# Validación estricta para evitar que el programa inicie ciego
if not WEATHER_API_KEY:
    raise ValueError("❌ ERROR CRÍTICO: No hay API Key para WeatherAPI.")

print(f"🛠️  DEBUG - Llave del clima lista para usar: {WEATHER_API_KEY[:5]}***")

# ==========================================
# 2. HERRAMIENTAS DEL AGENTE
# ==========================================

# --- HERRAMIENTA 1: CLIMA ---
@tool
def consultar_clima(ciudad: str) -> str:
    """Consulta el clima actual de una ciudad. Útil para saber si hace sol, llueve o hace frío."""
    print(f"\n[🌤️  CLIMA] Consultando clima en {ciudad}...")
    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": WEATHER_API_KEY, "q": ciudad, "lang": "es"}
    
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status() 
        datos = resp.json()
        
        temp = datos["current"]["temp_c"]
        cond = datos["current"]["condition"]["text"]
        return f"En {ciudad} hace {temp}°C y está {cond}."
    except Exception as e:
        error_msg = f"Error de conexión con WeatherAPI: {str(e)}"
        print(f"[❌ ERROR CLIMA] {error_msg}")
        return error_msg
    
# --- HERRAMIENTA 2: MÚSICA (Vía iTunes Search API - Gratis y sin auth) ---
@tool
def buscar_musica_por_animo(animo: str) -> str:
    """
    Busca una canción recomendada basada en un estado de ánimo o clima.
    Ejemplo de entrada: 'lluvia', 'sol', 'fiesta', 'música tranquila'.
    """
    print(f"[🎵 MÚSICA] Buscando recomendaciones para: '{animo}'...")
    
    # URL oficial pública de iTunes/Apple
    url = "https://itunes.apple.com/search"
    params = {
        "term": animo,
        "media": "music",
        "entity": "song",
        "limit": 1
    }
    
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        datos = resp.json()
        
        if datos["resultCount"] == 0:
            return "No encontré canciones para ese estado de ánimo."
            
        cancion = datos["results"][0]
        titulo = cancion["trackName"]
        artista = cancion["artistName"]
        url_link = cancion["trackViewUrl"]
        
        return f"Te recomiendo escuchar '{titulo}' de {artista}. Enlace: {url_link}"
    except Exception as e:
        error_msg = f"Error al buscar música: {str(e)}"
        print(f"[❌ ERROR MÚSICA] {error_msg}")
        return error_msg
    
# ==========================================
# 3. CONFIGURACIÓN DEL AGENTE
# ==========================================
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="gemma-4-e4b-it_gguf", 
    temperature=0.0
)

herramientas = [consultar_clima, buscar_musica_por_animo]
agente = create_react_agent(llm, tools=herramientas)

if __name__ == "__main__":
    print("🤖 Agente Clima-Musical listo (LM Studio + Spotify)")
    
    instrucciones = (
        "system", 
        "Eres un asistente conversacional útil.\n"
        "REGLA 1: Si el usuario pregunta por el clima, usa la herramienta de clima.\n"
        "REGLA 2: Si pide música, usa primero el clima y luego Spotify.\n"
        "REGLA CRÍTICA: UNA VEZ QUE USES UNA HERRAMIENTA Y OBTENGAS LOS DATOS, ES OBLIGATORIO QUE REDACTES UNA RESPUESTA FINAL EXPLICANDO LOS RESULTADOS AL USUARIO. NUNCA DEVUELVAS UN MENSAJE EN BLANCO."
    )

    while True:
        usuario = input("\nTú: ")
        if usuario.lower() in ["salir", "exit", "quit"]: 
            print("¡Hasta luego!")
            break
        
        if usuario.strip():
            # Invocamos al agente
            eventos = agente.invoke({"messages": [instrucciones, ("user", usuario)]})
            
            # Extraemos el último mensaje generado
            ultimo_mensaje = eventos['messages'][-1]
            respuesta = ultimo_mensaje.content
            
            # Validación: Si la respuesta está vacía, buscamos si el modelo falló al formatearla
            if not respuesta.strip():
                print("\n[⚠️ AVISO] El modelo recibió los datos del clima correctamente, pero no supo redactar la respuesta final.")
                print(f"Datos crudos devueltos por el modelo: {ultimo_mensaje.additional_kwargs}")
                print("-> SUGERENCIA: En LM Studio, intenta cambiar el modelo o subir la 'Temperature' a 0.3.")
            else:
                print(f"\nAgente: {respuesta}")