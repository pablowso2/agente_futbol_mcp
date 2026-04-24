import warnings
# Esto ocultará el mensaje molesto de Pydantic
warnings.filterwarnings("ignore", category=UserWarning)

print("Paso 1: Iniciando script...")

try:
    print("Paso 2: Intentando importar el grafo...")
    from graph import app
    print("Paso 3: Grafo importado correctamente.")
except Exception as e:
    print(f"❌ Error silencioso al importar el grafo: {e}")

from langchain_core.messages import HumanMessage

def main():
    print("Paso 6: Entrando a la función principal...")
    print("🤖 Agente Deportivo (Llama 3.1 Local) Iniciado. (Escribe 'salir' para terminar)")
    print("-" * 70)
    
    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("¡Nos vemos!")
            break
            
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        try:
            for event in app.stream(inputs, stream_mode="values"):
                last_message = event["messages"][-1]
                
                if last_message.type == "ai":
                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        print(f"⚙️  Llamando al MCP: {last_message.tool_calls[0]['name']}...")
                    elif last_message.content:
                        print(f"🤖 Agente: {last_message.content}")
                        
        except Exception as e:
            print(f"❌ Ocurrió un error en la ejecución: {e}")

print("Paso 4: Leyendo la comprobación de inicio...")

if __name__ == "__main__":
    print("Paso 5: ¡Arrancando el programa!")
    main()