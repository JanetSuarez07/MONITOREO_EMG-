import asyncio
import websockets
import socketio

sio = socketio.AsyncClient()
socket_esp32 = None 

async def handler(websocket): # 'path' no es necesario en versiones recientes de websockets
    global socket_esp32
    socket_esp32 = websocket
    print("¡ESP32 conectado localmente al puente!")
    
    async for message in websocket:
        try:
            valor_procesado = int(message)
            if sio.connected:
                await sio.emit('datos_procesados', {'valor': valor_procesado})
        except Exception as e:
            print(f"Error procesando mensaje del ESP32: {e}")

@sio.on('cambiar_umbral')
async def al_recibir_umbral(data):
    if socket_esp32:
        comando = f"UMBRAL:{data['valor']}"
        await socket_esp32.send(comando)
        print(f"Comando enviado al ESP32: {comando}")

async def conectar_nube():
    print("Intentando conectar a la nube...")
    try:
        # Añadimos un agente de usuario para que no parezca un bot bloqueado
        headers = {'User-Agent': 'Mozilla/5.0'}
        await sio.connect('https://monitoreo-emg.onrender.com', headers=headers)
        print("¡Conexión establecida con éxito!")
    except Exception as e:
        print(f"Error: {e}")
        
async def main():
    # Iniciamos la conexión a la nube y el servidor local en paralelo
    await conectar_nube()
    async with websockets.serve(handler, "0.0.0.0", 8000):
        print("Puente activo. Esperando ESP32 en puerto 8000...")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Servidor puente detenido.")