"""Servidor XML-RPC para calcular IMC con control de errores."""
# El servidor expone dos funciones remotas: calcular_imc, que recibe peso y altura, valida los datos, 
# calcula el IMC, clasifica la categoria y guarda los calculos validos en un historial; 
# e historial, que retorna los ultimos 5 calculos validos. 
# 
# El servidor maneja errores de formato y valores invalidos devolviendo respuestas claras al cliente sin lanzar excepciones.
from xmlrpc.server import SimpleXMLRPCServer


HOST = "127.0.0.1" # El servidor se ejecuta en localhost, lo que significa que solo acepta conexiones desde la misma máquina.
PORT = 8000 # Puerto en el que el servidor escucha las solicitudes XML-RPC

# Historial en memoria: se pierde al detener el servidor, como pide la practica.
historial_calculos = []

# Funciones auxiliares para validar datos, clasificar el IMC y construir respuestas de error. Estas funciones ayudan a mantener el código organizado y facilitan el control de errores en la función calcular_imc.
def es_numero(valor):
    """Valida que el dato recibido sea numerico y no booleano."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)

# La función clasificar_imc se encarga de determinar la categoria del IMC calculado según los rangos establecidos por la Organización Mundial de la Salud (OMS). Esto permite que el cliente reciba una respuesta completa con el valor del IMC y su categoria correspondiente.
def clasificar_imc(imc):
    """Retorna la categoria segun el valor del IMC."""
    if imc < 18.5:
        return "Bajo peso"
    if imc < 25:
        return "Normal"
    if imc < 30:
        return "Sobrepeso"
    return "Obesidad"

#  La función respuesta_error construye un diccionario con la estructura de respuesta esperada por el cliente, 
# pero con los campos indicando que ocurrió un error. Esto permite que el cliente maneje los errores de forma clara 
# sin tener que lidiar con excepciones o respuestas inesperadas.
def respuesta_error(mensaje):
    """Construye una respuesta de error sin lanzar excepciones al cliente."""
    return {
        "ok": False,
        "imc": 0.0,
        "categoria": "Error",
        "mensaje": mensaje,
    }

# La función calcular_imc es la función remota que el cliente invoca para calcular el IMC. 
# Esta función realiza varias validaciones para asegurarse de que los datos recibidos sean correctos, 
# y en caso de error, devuelve una respuesta clara sin lanzar excepciones. 
# Si los datos son válidos, calcula el IMC, clasifica la categoria, guarda el calculo en el historial 
# y retorna la respuesta con el resultado.
def calcular_imc(peso_kg, altura_m):
    """Funcion remota que calcula el IMC y guarda los calculos validos."""
    # Seccion revisada y optimizada con apoyo de IA (GPT-5.5) para que los
    # errores del cliente se devuelvan como diccionarios y no como excepciones.
    if not es_numero(peso_kg) or not es_numero(altura_m):
        return respuesta_error("El peso y la altura deben ser valores numericos.")

# Se validan los valores de peso y altura para asegurarse de que sean mayores que cero, 
# ya que un peso o altura no positivos no tienen sentido en el contexto del cálculo del IMC. 
# Si alguno de los valores es inválido, se devuelve una respuesta de error con un mensaje claro 
# indicando el problema.
    if peso_kg <= 0:
        return respuesta_error("El peso debe ser mayor que cero.")

# Se validan los valores de peso y altura para asegurarse de que sean mayores que cero, 
# ya que un peso o altura no positivos no tienen sentido en el contexto del cálculo del IMC. 
# Si alguno de los valores es inválido, se devuelve una respuesta de error con un mensaje claro 
# indicando el problema.
    if altura_m <= 0:
        return respuesta_error("La altura debe ser mayor que cero.")

    imc = peso_kg / (altura_m ** 2)
    imc_redondeado = round(imc, 2)
    categoria = clasificar_imc(imc)

    resultado = {
        "ok": True,
        "imc": imc_redondeado,
        "categoria": categoria,
        "mensaje": "Calculo realizado correctamente.",
    }

    historial_calculos.append({
        "peso_kg": peso_kg,
        "altura_m": altura_m,
        "imc": imc_redondeado,
        "categoria": categoria,
    })

    # Conserva solo los ultimos 5 calculos validos solicitados por historial().
    if len(historial_calculos) > 5:
        historial_calculos.pop(0)

    return resultado


def historial():
    """Funcion remota que retorna los ultimos 5 calculos validos."""
    return historial_calculos[-5:]


def iniciar_servidor():
    """Crea el servidor XML-RPC y publica las funciones remotas."""
    # SimpleXMLRPCServer expone funciones Python para que el cliente las invoque
    # como si fueran metodos remotos.
    servidor = SimpleXMLRPCServer(
        (HOST, PORT),
        allow_none=False,
        logRequests=True
    )
    servidor.register_function(calcular_imc, "calcular_imc")
    servidor.register_function(historial, "historial")

    print(f"Servidor XML-RPC escuchando en http://{HOST}:{PORT}")
    print("Funciones disponibles: calcular_imc(peso_kg, altura_m), historial()")

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    iniciar_servidor()
