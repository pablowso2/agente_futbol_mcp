import requests

# Tu API Key configurada como variable
WEATHER_API_KEY = "5355b7ec82b04b8389f155930252404"

def consultar_clima(ciudad):
    """
    Consulta el clima actual de una ciudad usando WeatherAPI.
    """
    # El endpoint específico para el clima actual
    url = "http://api.weatherapi.com/v1/current.json"
    
    # Parámetros que exige la API
    parametros = {
        "key": WEATHER_API_KEY,
        "q": ciudad,
        "lang": "es" # Para que la descripción del clima venga en español
    }
    
    try:
        # Hacemos la petición GET a la API
        respuesta = requests.get(url, params=parametros)
        
        # Validamos si la petición fue exitosa (código 200)
        respuesta.raise_for_status()
        
        # Convertimos la respuesta a un diccionario JSON
        datos = respuesta.json()
        
        # Extraemos la información que nos interesa
        nombre_ciudad = datos["location"]["name"]
        pais = datos["location"]["country"]
        temperatura = datos["current"]["temp_c"]
        condicion = datos["current"]["condition"]["text"]
        
        # Imprimimos el resultado
        print("\n--- Reporte del Clima ---")
        print(f"Ubicación: {nombre_ciudad}, {pais}")
        print(f"Temperatura: {temperatura}°C")
        print(f"Condición: {condicion.capitalize()}")
        print("-------------------------\n")
        
    except requests.exceptions.HTTPError as err_http:
        print(f"\n❌ Error HTTP: Verifica que la ciudad exista o que el API Key sea correcto. Detalles: {err_http}")
    except Exception as e:
        print(f"\n❌ Ocurrió un error inesperado: {e}")

# ==========================================
# Ejecución del Agente
# ==========================================
if __name__ == "__main__":
    print("¡Hola! Soy tu Agente del Clima en Python ⛅")
    
    while True:
        entrada = input("¿De qué ciudad quieres saber el tiempo? (Escribe 'salir' para terminar): ")
        
        if entrada.lower() == 'salir':
            print("¡Hasta luego!")
            break
            
        if entrada.strip():
            consultar_clima(entrada)
        else:
            print("Por favor, ingresa un nombre de ciudad válido.")