"""Cliente XML-RPC con llamadas de prueba para la Actividad 2.2."""
# El cliente se conecta al servidor XML-RPC, realiza varias llamadas a calcular_imc
# con diferentes pesos y alturas, e imprime los resultados de forma clara.
import xmlrpc.client

# Configuración del host y puerto del servidor XML-RPC.
HOST = "127.0.0.1" # El cliente se conecta al servidor local (localhost).
PORT = 8000 # El puerto debe coincidir con el puerto en el que el servidor está escuchando.

# Funciones auxiliares para mostrar resultados de forma clara.
def imprimir_resultado(numero, peso, altura, resultado): # numero es el numero de prueba, peso y altura son los datos de entrada, resultado es la respuesta del servidor.
    """Muestra una respuesta de calcular_imc de forma clara."""
    print(f"Prueba {numero}: calcular_imc({peso}, {altura})")# Imprime el numero de prueba y los datos de entrada.

    # El resultado es un diccionario con las claves: 'ok' (booleano), 'mensaje' (string), 'imc' (float) y 'categoria' (string).
    if resultado["ok"]:
        print(f"  OK: {resultado['mensaje']}")
        print(f"  IMC: {resultado['imc']}")
        print(f"  Categoria: {resultado['categoria']}")
    else:
        print(f"  ERROR: {resultado['mensaje']}")

    print()

# El cliente también puede solicitar el historial de calculos validos al servidor y mostrarlo.
def imprimir_historial(registros):
    """Muestra los ultimos calculos validos guardados por el servidor."""
    print("Historial de ultimos calculos validos:")
    # El historial es una lista de diccionarios con las claves: 'peso_kg', 'altura_m', 'imc' y 'categoria'.
    if not registros:
        print("  No hay calculos validos registrados.")
        return
    # Se muestra cada registro con su indice, peso, altura, imc y categoria.
    for indice, registro in enumerate(registros, start=1):
        print(
            f"  {indice}. peso={registro['peso_kg']} kg, "
            f"altura={registro['altura_m']} m, "
            f"IMC={registro['imc']}, "
            f"categoria={registro['categoria']}"
        )

# La función principal del cliente inicia la conexión con el servidor, realiza las pruebas y muestra los resultados.
def iniciar_cliente():
    """Conecta con el servidor RPC y ejecuta llamadas de prueba."""
    # ServerProxy crea el objeto que representa al servidor remoto.
    servidor = xmlrpc.client.ServerProxy(f"http://{HOST}:{PORT}/")

    # Incluye casos correctos y casos de error para evidenciar el control.
    pruebas = [
        (70, 1.75),      # Caso valido: Normal
        (82, 1.70),      # Caso valido: Sobrepeso
        (95, 1.60),      # Caso valido: Obesidad
        (45, 1.70),      # Caso valido: Bajo peso
        (0, 1.75),       # Error: peso cero
        (70, -1.75),     # Error: altura negativa
        ("setenta", 1.75),  # Error: dato no numerico
    ]

    print("Cliente XML-RPC - Pruebas de calculo de IMC")
    print("=" * 48)
    print()
    # Se realizan las llamadas a calcular_imc para cada caso de prueba y se imprime el resultado.
    for numero, (peso, altura) in enumerate(pruebas, start=1):
        resultado = servidor.calcular_imc(peso, altura)
        imprimir_resultado(numero, peso, altura, resultado)

    # El historial se consulta al final para mostrar solo calculos validos.
    registros = servidor.historial()
    imprimir_historial(registros)

# El bloque if __name__ == "__main__" asegura que iniciar_cliente() se ejecute solo si este script 
# se ejecuta directamente, no si se importa como módulo.
if __name__ == "__main__":
    iniciar_cliente()
