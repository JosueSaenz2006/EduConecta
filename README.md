# EduConecta — Práctica de Comunicación entre Procesos

## Integrantes
- Edwin Alejandro Angamarca Avendaño
- Josué Gabriel Sáenz Arias

## Asignatura
Sistemas Distribuidos

## Descripción general
EduConecta es una práctica universitaria orientada a la comunicación entre procesos y al diseño de una arquitectura distribuida. El repositorio incluye tres implementaciones funcionales en Python: un chat TCP con sockets e hilos, un servicio XML-RPC con control de errores y una mini API REST para gestión de tareas TODO.

Además, el proyecto incluye una propuesta de arquitectura distribuida para EduConecta, donde se seleccionan mecanismos de comunicación adecuados para distintos componentes del sistema: WebSocket, REST, Kafka / Message Broker y gRPC.

## Estructura del repositorio
Árbol sugerido de entregables:

```text
ACTIVIDAD 2.1/
  servidor_chat.py
  cliente_chat.py
ACTIVIDAD 2.2/
  servidor_rpc.py
  cliente_rpc.py
ACTIVIDAD 2.3/
  app.py
  requirements.txt
diagrama/
  DISTRIBUIDOS.drawio.png
README.md
```

Nota: si existen carpetas generadas automáticamente como `__pycache__`, no forman parte de los entregables principales.

## Actividad 2.1 — Chat TCP con sockets
Esta actividad implementa un mini-chat usando sockets TCP. El servidor escucha en `127.0.0.1:65432`, acepta varios clientes y crea un hilo independiente para atender a cada uno. Cuando un cliente envía un mensaje, el servidor lo registra con timestamp, IP y puerto, y lo retransmite a los demás clientes conectados mediante broadcast. El mensaje `SALIR` permite cerrar la conexión de forma limpia.

Se deben usar tres terminales: una para el servidor y dos para clientes.

Terminal 1:

```powershell
cd "ACTIVIDAD 2.1"
py servidor_chat.py
```

Terminal 2:

```powershell
cd "ACTIVIDAD 2.1"
py cliente_chat.py
```

Terminal 3:

```powershell
cd "ACTIVIDAD 2.1"
py cliente_chat.py
```

## Actividad 2.2 — XML-RPC con cálculo de IMC
Esta actividad implementa un servidor XML-RPC que expone la función remota `calcular_imc(peso_kg, altura_m)`. La función calcula el IMC, retorna su categoría y maneja errores cuando el peso, la altura o el tipo de dato no son válidos. También expone `historial()`, que retorna los últimos 5 cálculos válidos guardados en memoria mientras el servidor está ejecutándose.

Se deben usar dos terminales: una para el servidor RPC y otra para el cliente de pruebas.

Terminal 1:

```powershell
cd "ACTIVIDAD 2.2"
py servidor_rpc.py
```

Terminal 2:

```powershell
cd "ACTIVIDAD 2.2"
py cliente_rpc.py
```

## Actividad 2.3 — API REST con FastAPI
Esta actividad implementa una mini API REST para gestionar tareas TODO. La aplicación usa FastAPI y guarda los datos en memoria mediante un diccionario. Cada tarea contiene `id`, `titulo`, `descripcion` y `estado`. El estado inicial es `pendiente`, y el endpoint `PUT /tareas/{id}` cambia la tarea a `completada`.

Instalación y ejecución:

```powershell
cd "ACTIVIDAD 2.3"
py -m pip install -r requirements.txt
py -m uvicorn app:app --reload
```

Luego se puede abrir la documentación automática de FastAPI en:

```text
http://127.0.0.1:8000/docs
```

Endpoints implementados:

- `GET /tareas`: lista todas las tareas.
- `GET /tareas/{id}`: consulta una tarea por ID.
- `POST /tareas`: crea una tarea con `titulo` y `descripcion`.
- `PUT /tareas/{id}`: marca una tarea como completada.
- `DELETE /tareas/{id}`: elimina una tarea por ID.

## Comandos de prueba para API REST
Crear 3 tareas:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/tareas" -Method Post -ContentType "application/json" -Body '{"titulo":"Estudiar REST","descripcion":"Repasar los metodos GET, POST, PUT y DELETE"}' | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://127.0.0.1:8000/tareas" -Method Post -ContentType "application/json" -Body '{"titulo":"Completar informe","descripcion":"Agregar capturas de la API REST"}' | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://127.0.0.1:8000/tareas" -Method Post -ContentType "application/json" -Body '{"titulo":"Subir repositorio","descripcion":"Publicar el codigo en GitHub"}' | ConvertTo-Json -Depth 5
```

Listar tareas:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/tareas" -Method Get | ConvertTo-Json -Depth 5
```

Consultar tarea por ID:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/tareas/2" -Method Get | ConvertTo-Json -Depth 5
```

Completar tarea:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/tareas/2" -Method Put | ConvertTo-Json -Depth 5
```

Eliminar tarea:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/tareas/1" -Method Delete | ConvertTo-Json -Depth 5
```

Probar error 404:

```powershell
try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/tareas/999" -Method Get
} catch {
    Write-Host "Codigo HTTP:" $_.Exception.Response.StatusCode.value__
    Write-Host "Respuesta:"
    Write-Host $_.ErrorDetails.Message
}
```

Probar error 400:

```powershell
try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/tareas" -Method Post -ContentType "application/json" -Body '{"titulo":"","descripcion":"Descripcion cualquiera"}'
} catch {
    Write-Host "Codigo HTTP:" $_.Exception.Response.StatusCode.value__
    Write-Host "Respuesta:"
    Write-Host $_.ErrorDetails.Message
}
```

## Parte 3 — Arquitectura EduConecta
La arquitectura propuesta para EduConecta selecciona mecanismos distintos según la necesidad de comunicación de cada componente:

- **WebSocket para chat en vivo:** permite baja latencia y comunicación bidireccional entre cliente y servidor.
- **REST para catálogo:** ofrece simplicidad, compatibilidad con aplicaciones web/móviles y fácil integración con clientes HTTP.
- **Kafka / Message Broker para notificaciones:** desacopla productores y consumidores, y permite comunicación asíncrona entre servicios.
- **gRPC para microservicios internos:** ofrece tipado fuerte, alto rendimiento y soporte para entornos con Python y Java.

## Uso responsable de IA
Durante la Parte 1 no se utilizó IA, porque el enunciado lo prohibía.

Desde la Parte 2 se utilizó IA como apoyo para estructurar código, revisar errores, generar comandos de prueba, documentar y organizar el proyecto.

El código fue ejecutado, probado y ajustado manualmente por los integrantes. La IA no reemplazó la validación práctica; solo funcionó como apoyo técnico.

## Evidencias
Las capturas de pantalla requeridas están incluidas en el informe Word. El repositorio contiene el código fuente de las actividades implementadas.

## Repositorio
https://github.com/JosueSaenz2006/EduConecta.git
