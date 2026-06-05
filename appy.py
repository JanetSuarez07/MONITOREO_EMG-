import asyncio
import websockets
import socketio
import numpy as np
from scipy.signal import butter, lfilter, iirnotch, lfilter_zi

# Configuración de Filtros
FS = 500
OFFSET = 1795
b_band, a_band = butter(2, [20/(FS*0.5), 200/(FS*0.5)], btype='band')
b_notch, a_notch = iirnotch(60/(FS*0.5), 30)

zi_notch = lfilter_zi(b_notch, a_notch)
zi_band = lfilter_zi(b_band, a_band)
env_anterior = 0

sio = socketio.AsyncClient()

async def conectar_nube():
    print("Intentando conectar a la nube...")
    try:
        await sio.connect(
            'https://monitoreo-emg.onrender.com', 
            socketio_path='/socket.io', 
            transports=['polling']
        )
        print("¡Conexión establecida con éxito!")
    except Exception as e:
        print(f"Error al conectar: {e}")

async def handler(websocket):
    global zi_notch, zi_band, env_anterior
    print("¡ESP32 conectado vía WebSocket!")

    async for message in websocket:
        try:
            val = int(message)
            cruda = val - OFFSET
            
            # Procesamiento
            val_notch, zi_notch = lfilter(b_notch, a_notch, [cruda], zi=zi_notch)
            val_filt, zi_band = lfilter(b_band, a_band, val_notch, zi=zi_band)
            
            rectificada = abs(val_filt[0])
            env = 0.02 * rectificada + 0.98 * env_anterior
            env_anterior = env
            
            # Enviar a Render
            try:
                if sio.connected:
                    await sio.emit('datos_procesados', {
                        'valor': float(val_filt[0]),
                        'envolvente': float(env)
                    })
            except Exception as e:
                print(f"Error al enviar a la nube: {e}")
            
        except Exception as e:
            print(f"Error en procesamiento: {e}")

async def main():
    await conectar_nube()
    async with websockets.serve(handler, "0.0.0.0", 8000):
        print("Esperando datos del ESP32 en puerto 8000...")
        await asyncio.Future() 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Servidor detenido.")