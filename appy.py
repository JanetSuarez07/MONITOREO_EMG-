import asyncio
import websockets
import socketio

# Cliente para hablar con la Nube (Render)
sio = socketio.AsyncClient()
# Variable para guardar la conexión con el ESP32
socket_esp32 = None 

async def handler(websocket, path):
    global socket_esp32
    socket_esp32 = websocket
    print("¡ESP32 conectado al puente!")
    
    async for message in websocket:
        try:
            # Recibimos el valor ya procesado por el ESP32
            valor_procesado = int(message)
            # Reenviamos a Render
            if sio.connected:
                await sio.emit('datos_procesados', {'valor': valor_procesado})
        except Exception as e:
            print(f"Error procesando mensaje del ESP32: {e}")

@sio.on('cambiar_umbral')
async def al_recibir_umbral(data):
    # Cuando la web manda el comando, se lo pasamos al ESP32
    if socket_esp32:
        comando = f"UMBRAL:{data['valor']}"
        await socket_esp32.send(comando)
        print(f"Comando enviado al ESP32: {comando}")

async def conectar_nube():
    print("Intentando conectar a la nube...")
    await sio.connect('https://monitoreo-emg.onrender.com', transports=['websocket'])
    print("¡Conexión establecida con éxito!")

async def main():
    await conectar_nube()
    # Servidor local para que el ESP32 se conecte
    async with websockets.serve(handler, "0.0.0.0", 8000):
        print("Puente activo. Esperando ESP32 en puerto 8000...")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Servidor puente detenido.")