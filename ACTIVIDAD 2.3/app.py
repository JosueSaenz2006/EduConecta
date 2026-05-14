"""Mini API REST TODO con FastAPI y almacenamiento en memoria."""
# Este código implementa una API REST para gestionar tareas pendientes. Permite crear, listar, obtener, completar y eliminar tareas. Las tareas se almacenan en un diccionario en memoria, lo que simplifica la implementación sin necesidad de una base de datos externa. La API maneja errores comunes como solicitudes con formato incorrecto o acceso a tareas inexistentes, proporcionando respuestas claras y consistentes.
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Configuración del host y puerto donde se ejecutará el servidor FastAPI.
app = FastAPI(title="Mini API REST TODO")

# Diccionario en memoria: id de la tarea -> datos de la tarea.
# No se usa base de datos externa para mantener el alcance de la practica.
tareas = {} # El diccionario tareas almacena las tareas creadas, donde la clave es el ID de la tarea y el valor es un diccionario con los detalles de la tarea (titulo, descripcion, estado).
siguiente_id = 1 # La variable siguiente_id se utiliza para asignar un ID único a cada nueva tarea creada. Se incrementa cada vez que se crea una tarea nueva.

# Funciones auxiliares para crear respuestas de error, validar campos de texto y leer el body JSON de las solicitudes.
def crear_error(codigo, mensaje):
    """Retorna un mensaje de error en formato JSON."""
    # Estructura validada con apoyo de IA para facilitar respuestas 400/404
    # claras y consistentes durante la sustentacion.
    return JSONResponse(
        status_code=codigo,
        content={"mensaje": mensaje}
    )

# La función validar_texto se encarga de verificar que un campo sea una cadena de texto no vacía. Esto es importante para asegurar que los datos ingresados por el usuario sean válidos antes de crear o actualizar una tarea.
def validar_texto(valor):
    """Valida que un campo sea texto y no este vacio."""
    return isinstance(valor, str) and valor.strip() != ""

# La función leer_body_json se encarga de leer el body de la solicitud y convertirlo a un diccionario de Python. 
# Si el body no es un JSON válido o no es un diccionario, la función retorna None, 
# lo que permite manejar estos casos como errores de formato en las rutas que crean o actualizan tareas.
async def leer_body_json(request):
    """Lee el body JSON y controla errores de formato."""
    try:
        datos = await request.json()
    except Exception:
        return None
    # Se valida que el body sea un diccionario, ya que se espera un objeto JSON con claves y valores. 
    # Si el body es un JSON válido pero no es un diccionario (por ejemplo, una lista o un valor primitivo), 
    # se considera un formato incorrecto y se retorna None para manejarlo como un error.
    if not isinstance(datos, dict):
        return None

    return datos

# Rutas de la API para listar tareas, obtener una tarea por ID, crear una nueva tarea, 
# completar una tarea y eliminar una tarea. Cada ruta maneja los casos de error correspondientes, 
# como solicitudes con formato incorrecto o acceso a tareas inexistentes, utilizando la función crear_error 
# ara retornar respuestas claras y consistentes.
@app.get("/tareas") # La ruta GET /tareas retorna una lista de todas las tareas almacenadas en el diccionario tareas.
def listar_tareas():
    """Retorna todas las tareas guardadas."""
    return list(tareas.values())

# app.get sirve para definir una ruta que responde a solicitudes HTTP GET. 
# En este caso, la ruta es /tareas/{id}, lo que significa que se espera un ID de tarea como parte de la URL. 
# La función obtener_tarea se encarga de buscar la tarea correspondiente a ese ID en el diccionario tareas y retornarla. 
# Si el ID no existe, se utiliza la función crear_error para retornar una respuesta con código 404 y 
# un mensaje indicando que la tarea solicitada no existe.
@app.get("/tareas/{id}")
def obtener_tarea(id: int):
    """Busca una tarea por su ID."""
    # Si el ID no existe se retorna 404, no una respuesta vacia.
    if id not in tareas:
        return crear_error(404, "La tarea solicitada no existe.")

    return tareas[id]

# La ruta POST /tareas permite crear una nueva tarea. 
# La función crear_tarea se encarga de leer el body de la solicitud, 
# validar que los campos titulo y descripcion sean texto no vacío, 
# y luego crear una nueva tarea con un ID único. Si el body no es un JSON válido 
# o si los campos no cumplen con las validaciones, se retorna una respuesta con código 400 
# y un mensaje de error correspondiente.
@app.post("/tareas")
async def crear_tarea(request: Request):
    """Crea una tarea nueva con estado inicial pendiente."""
    global siguiente_id

    # Se valida manualmente el body para responder 400 con mensajes propios.
    datos = await leer_body_json(request)
    if datos is None:
        return crear_error(400, "Debe enviar un body JSON valido.")

    titulo = datos.get("titulo")
    descripcion = datos.get("descripcion")

    if not validar_texto(titulo):
        return crear_error(400, "El campo titulo es obligatorio y no puede estar vacio.")

    if not validar_texto(descripcion):
        return crear_error(400, "El campo descripcion es obligatorio y no puede estar vacio.")
    # Si los datos son validos, se crea la tarea con un ID unico, 
    # se guarda en el diccionario tareas y se retorna la tarea creada.
    tarea = {
        "id": siguiente_id,
        "titulo": titulo.strip(), # strip() elimina los espacios en blanco al inicio y al final del texto, 
                                  # lo que ayuda a mantener los datos limpios y consistentes.
        "descripcion": descripcion.strip(),
        "estado": "pendiente",
    }
# La tarea se guarda en el diccionario tareas utilizando el siguiente_id como clave, 
# y luego se incrementa siguiente_id para asegurar que el próximo ID asignado sea único.
    tareas[siguiente_id] = tarea
    siguiente_id += 1

    return tarea

# La ruta PUT /tareas/{id} permite cambiar el estado de una tarea a completada.
# La función completar_tarea se encarga de verificar que la tarea con el ID especificado
@app.put("/tareas/{id}")
def completar_tarea(id: int):
    """Cambia el estado de una tarea a completada."""
    # El PUT de esta practica solo cambia el estado, no edita titulo ni descripcion.
    if id not in tareas:
        return crear_error(404, "La tarea solicitada no existe.")

    tareas[id]["estado"] = "completada"
    return tareas[id]

# La ruta DELETE /tareas/{id} permite eliminar una tarea por su ID.
@app.delete("/tareas/{id}")
def eliminar_tarea(id: int):
    """Elimina una tarea por su ID."""
    # Antes de eliminar se valida existencia para reportar 404 si corresponde.
    if id not in tareas:
        return crear_error(404, "La tarea solicitada no existe.")

    tarea_eliminada = tareas.pop(id)
    return {
        "mensaje": "Tarea eliminada correctamente.",
        "tarea": tarea_eliminada,
    }
