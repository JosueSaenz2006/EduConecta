"""Cliente TCP para participar en el mini-chat de la Actividad 2.1."""
# El cliente se conecta al servidor TCP, permite al usuario enviar mensajes por consola
import socket # y recibe mensajes del servidor en un hilo separado para no bloquear la entrada del usuario.
import threading # threading se usa para crear un hilo que se encargue de recibir mensajes del servidor sin bloquear la interacción del usuario en la consola.

# Configuración del host y puerto del servidor TCP al que se conectará el cliente.
HOST = "127.0.0.1" # El cliente se conecta al servidor local (localhost).
PORT = 65432 # El puerto debe coincidir con el puerto en el que el servidor está escuchando.

# La función recibir_mensajes se ejecuta en un hilo separado y se encarga de recibir mensajes del servidor y mostrarlos por consola. Esto permite que el usuario pueda seguir escribiendo mensajes sin interrupciones.
def recibir_mensajes(cliente):
    """Hilo receptor: imprime mensajes mientras el usuario sigue escribiendo."""
    # El cliente recibe datos del servidor en un bucle infinito. Si el servidor cierra la conexión, 
    # el cliente detecta que no hay datos y termina el hilo receptor.
    while True:
        # Se intenta recibir datos del servidor. Si el servidor cierra la conexión, 
        # recv() devuelve una cadena vacía, lo que indica que se debe salir del bucle.
        try:
            datos = cliente.recv(1024)
            # Si no se reciben datos, significa que el servidor ha cerrado la conexión, por lo que se sale del bucle.
            if not datos:
                print("\nConexion cerrada por el servidor.")
                break
            # Se decodifica el mensaje recibido y se imprime por consola. 
            # El mensaje se decodifica usando UTF-8, que es un estándar común para codificar texto.
            mensaje = datos.decode("utf-8")
            print(f"\n{mensaje}")
        # Si ocurre un error al intentar recibir datos (por ejemplo, si el servidor se desconecta abruptamente), 
        # se captura la excepción OSError y se sale del bucle.
        except OSError:
            break

# La función iniciar_cliente establece la conexión con el servidor, inicia el hilo receptor y permite al usuario enviar mensajes por consola. El cliente se desconecta al escribir "SALIR" o al interrumpir con Ctrl+C.
def iniciar_cliente():
    """Conecta el cliente al servidor y permite enviar mensajes por consola."""
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORT))

    print(f"Conectado al servidor {HOST}:{PORT}")
    print("Escribe mensajes y presiona Enter. Escribe SALIR para terminar.")

    # Este hilo evita que la lectura de mensajes bloquee la escritura del usuario.
    hilo_receptor = threading.Thread(
        target=recibir_mensajes,
        args=(cliente,),
        daemon=True
    )
    hilo_receptor.start()
    # El hilo receptor se marca como daemon para que se cierre automáticamente cuando el programa principal termine.
    try:
        while True:
            mensaje = input("> ")
            cliente.sendall(mensaje.encode("utf-8"))

            # SALIR se envia al servidor y luego se cierra el socket local.
            if mensaje.upper() == "SALIR":
                print("Desconectando...")
                break
    except KeyboardInterrupt:
        # Si el usuario interrumpe con Ctrl+C, se intenta enviar "SALIR" al servidor para cerrar la conexión de forma ordenada.
        try:
            cliente.sendall("SALIR".encode("utf-8"))
        except OSError:
            pass
    finally:
        cliente.close()

# El bloque if __name__ == "__main__" asegura que iniciar_cliente() se ejecute solo si este script
if __name__ == "__main__":
    iniciar_cliente()
