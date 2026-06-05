import asyncio
import websockets
import socketio
import numpy as np
from scipy.signal import butter, lfilter, iirnotch, lfilter_zi

# =========================================================
# CONFIGURACIÓN DE FILTROS EMG (Tus valores probados)
# =========================================================
FS = 500
OFFSET = 1795
b_band, a_band = butter(2, [20/(FS*0.5), 200/(FS*0.5)], btype='band')
b_notch, a_notch = iirnotch(60/(FS*0.5), 30)

# Estados iniciales
zi_notch = lfilter_zi(b_notch, a_notch)
zi_band = lfilter_zi(b_band, a_band)
env_anterior = 0

# =========================================================
# CLIENTE SOCKET.IO (Corregido: sin argumentos incompatibles)
# =========================================================
sio = socketio.AsyncClient()

async def conectar_nube():
    # Usamos 'polling' si WebSockets directos dan problemas con Render
    # Cambia tu línea 27 por esta versión simplificada:
    await sio.connect('https://monitoreo-emg.onrender.com', transports=['polling'])
    print("Conectado a la nube (Render)")

# =========================================================
# SERVIDOR WEBSOCKET (Conecta con ESP32)
# =========================================================
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
            await sio.emit('datos_procesados', {
                'valor': float(val_filt[0]),
                'envolvente': float(env)
            })
            
        except Exception as e:
            print(f"Error en procesamiento: {e}")

# =========================================================
# MAIN
# =========================================================
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