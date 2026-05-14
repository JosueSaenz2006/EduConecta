"""Servidor TCP para un mini-chat con multiples clientes usando hilos."""
# El servidor acepta conexiones de clientes, recibe mensajes y los retransmite a todos los clientes conectados. Cada cliente se atiende en un hilo separado para permitir la concurrencia. El servidor también registra cada mensaje con un timestamp y la dirección del cliente emisor.
import socket # socket se usa para crear el servidor TCP y manejar las conexiones con los clientes.
import threading # threading se usa para crear hilos que permitan atender a varios clientes simultáneamente sin bloquear el servidor principal.
from datetime import datetime # datetime se usa para registrar la fecha y hora de cada mensaje recibido, lo que ayuda a mantener un registro ordenado de las conversaciones.

# Configuración del host y puerto del servidor TCP.
HOST = "127.0.0.1" # El servidor se ejecuta en el localhost, lo que significa que solo aceptará conexiones 
# desde la misma máquina. Para aceptar conexiones desde otras máquinas, se podría usar "


PORT = 65432 # El puerto en el que el servidor escuchará las conexiones entrantes. 
# Este puerto debe estar libre y no ser utilizado por otros servicios en la máquina.

# Diccionario compartido entre hilos: socket del cliente -> direccion (IP, puerto).
clientes = {}

# El Lock evita que varios hilos modifiquen la lista de clientes al mismo tiempo.
bloqueo_clientes = threading.Lock()

# Funciones auxiliares para imprimir mensajes, registrar mensajes con timestamp y eliminar clientes de forma segura.
def imprimir(texto):
    """Imprime texto; si Windows no acepta la flecha, usa salida UTF-8."""
     # Algunas consolas de Windows no imprimen ciertos caracteres Unicode, como la flecha "→".
     # Si ocurre un error de codificación, se crea una salida UTF-8 para imprimir el texto correctamente. 
     # Esto asegura que los mensajes se muestren de forma clara en cualquier sistema operativo
    try:
        print(texto, flush=True)
    except UnicodeEncodeError:
        # Algunas consolas de Windows no imprimen la flecha del formato pedido.
        salida_utf8 = open(1, "w", encoding="utf-8", closefd=False)
        print(texto, file=salida_utf8, flush=True)

# La función registrar_mensaje se encarga de registrar cada mensaje recibido con un timestamp y 
# la dirección del cliente emisor. Esto ayuda a mantener un registro ordenado de las conversaciones y 
# facilita la depuración en caso de problemas.
def registrar_mensaje(direccion, mensaje):
    """Registra cada mensaje con timestamp, IP y puerto del cliente emisor."""
    # El timestamp se formatea como "YYYY-MM-DD HH:MM:SS" para una lectura clara y ordenada.
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # La dirección es una tupla (IP, puerto) que se descompone para mostrar la información del cliente emisor.
    ip, puerto = direccion
    # Se imprime el mensaje con el formato: "[timestamp] IP:puerto → 'mensaje'". 
    # Esto proporciona un registro claro de quién dijo qué y cuándo.
    imprimir(f"[{timestamp}] {ip}:{puerto} → '{mensaje}'")

# La función eliminar_cliente se encarga de quitar un cliente de la estructura compartida y 
# cerrar su socket de forma segura. Esto es importante para liberar recursos y 
# evitar que el servidor intente enviar mensajes a clientes que ya no están conectados.
def eliminar_cliente(cliente):
    """Quita un cliente de la estructura compartida y cierra su socket."""
    # La eliminacion se protege porque puede ocurrir desde cualquier hilo.
    with bloqueo_clientes:
        direccion = clientes.pop(cliente, None)
    # Si el cliente estaba registrado, se imprime un mensaje indicando que se ha desconectado, 
    # mostrando su dirección IP y puerto.
    if direccion is not None:
        ip, puerto = direccion
        print(f"Cliente desconectado: {ip}:{puerto}")
    # Se intenta cerrar el socket del cliente. Si el cliente ya se ha desconectado, 
    # esto puede generar un OSError, que se captura para evitar que el programa falle.
    try:
        cliente.close() # Cerrar el socket libera los recursos asociados a esa conexión. 
        # Si el cliente ya se ha desconectado
    # y el socket ya está cerrado, se genera un OSError, que se captura para evitar que el programa falle.
    except OSError:
        pass

# La función broadcast se encarga de enviar un mensaje a todos los clientes conectados excepto al emisor.
def broadcast(mensaje, emisor):
    """Envia el mensaje a todos los clientes conectados excepto al emisor."""
    # Seccion revisada y optimizada con apoyo de IA (GPT-5.5) para mejorar
    # claridad en concurrencia y manejo de sockets desconectados.
    with bloqueo_clientes:
        # Se copia la lista para no recorrer el diccionario mientras cambia.
        clientes_actuales = list(clientes.items())

    for cliente, direccion in clientes_actuales:
        if cliente != emisor:
            try:
                cliente.sendall(mensaje.encode("utf-8"))
            except OSError:
                eliminar_cliente(cliente)

# La función atender_cliente se ejecuta en un hilo separado para cada cliente conectado. 
# Se encarga de recibir mensajes de ese cliente, registrarlos y retransmitirlos a los demás clientes. 
# Si el cliente envía "SALIR" o se desconecta, la función termina y el cliente se elimina de la lista de clientes activos.
def atender_cliente(cliente, direccion):
    """Recibe mensajes de un cliente dentro de su propio hilo."""
    ip, puerto = direccion
    print(f"Cliente conectado: {ip}:{puerto}")
    # El cliente se registra antes de iniciar el bucle de recepción para que pueda recibir mensajes desde el principio.
    try:
        while True:
            datos = cliente.recv(1024)

            # Si recv no recibe datos, el cliente cerro la conexion.
            if not datos:
                break

            mensaje = datos.decode("utf-8").strip()
            registrar_mensaje(direccion, mensaje)

            # SALIR no se retransmite: solo finaliza la conexion del cliente.
            if mensaje.upper() == "SALIR":
                break

            mensaje_chat = f"{ip}:{puerto} dice: {mensaje}"
            broadcast(mensaje_chat, cliente)

    # Si el cliente se desconecta abruptamente, recv() genera una ConnectionResetError, que se captura para eliminar al cliente de forma segura.
    except ConnectionResetError:
        print(f"Conexion perdida con {ip}:{puerto}") # Esto indica que el cliente se desconectó sin enviar "SALIR", lo que puede ocurrir si cierra la aplicación o pierde la conexión a internet.
    # Cualquier otro error de socket también se captura para evitar que el hilo falle y para eliminar al cliente de forma segura.
    finally:
        eliminar_cliente(cliente)

# La función iniciar_servidor configura el socket TCP del servidor, lo pone a escuchar en el puerto especificado y acepta conexiones entrantes. Por cada nuevo cliente, se inicia un hilo separado que ejecuta la función atender_cliente para manejar la comunicación con ese cliente.
def iniciar_servidor():
    """Configura el socket TCP del servidor y acepta clientes."""
    # El socket se crea con AF_INET para IPv4 y SOCK_STREAM para TCP.
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    # SO_REUSEADDR permite reutilizar el puerto inmediatamente después de cerrar el servidor, lo que facilita las pruebas sin tener que esperar a que el sistema libere el puerto.
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # El servidor se vincula a la dirección y puerto especificados y comienza a escuchar conexiones entrantes.
    servidor.bind((HOST, PORT))
    # El servidor se pone a escuchar con un backlog de 5 conexiones, lo que significa que puede tener hasta 5 conexiones en espera antes de rechazar nuevas conexiones. Esto es suficiente para un chat simple, pero se podría ajustar según las necesidades.
    servidor.listen()

    print(f"Servidor escuchando en {HOST}:{PORT}")

    try:
        while True:
            cliente, direccion = servidor.accept()

            # Cada nuevo socket se registra antes de iniciar su hilo.
            with bloqueo_clientes:
                clientes[cliente] = direccion

            # Un hilo por cliente permite atender mensajes simultaneamente.
            hilo = threading.Thread(
                target=atender_cliente,
                args=(cliente, direccion),
                daemon=True
            )
            hilo.start()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        servidor.close()

        with bloqueo_clientes:
            clientes_actuales = list(clientes.keys())

        for cliente in clientes_actuales:
            eliminar_cliente(cliente)


if __name__ == "__main__":
    iniciar_servidor()
