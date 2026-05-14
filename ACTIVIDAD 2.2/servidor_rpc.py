"""Servidor XML-RPC para calcular IMC con control de errores."""

from xmlrpc.server import SimpleXMLRPCServer


HOST = "127.0.0.1"
PORT = 8000

# Historial en memoria: se pierde al detener el servidor, como pide la practica.
historial_calculos = []


def es_numero(valor):
    """Valida que el dato recibido sea numerico y no booleano."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def clasificar_imc(imc):
    """Retorna la categoria segun el valor del IMC."""
    if imc < 18.5:
        return "Bajo peso"
    if imc < 25:
        return "Normal"
    if imc < 30:
        return "Sobrepeso"
    return "Obesidad"


def respuesta_error(mensaje):
    """Construye una respuesta de error sin lanzar excepciones al cliente."""
    return {
        "ok": False,
        "imc": 0.0,
        "categoria": "Error",
        "mensaje": mensaje,
    }


def calcular_imc(peso_kg, altura_m):
    """Funcion remota que calcula el IMC y guarda los calculos validos."""
    # Seccion revisada y optimizada con apoyo de IA (GPT-5.5) para que los
    # errores del cliente se devuelvan como diccionarios y no como excepciones.
    if not es_numero(peso_kg) or not es_numero(altura_m):
        return respuesta_error("El peso y la altura deben ser valores numericos.")

    if peso_kg <= 0:
        return respuesta_error("El peso debe ser mayor que cero.")

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
