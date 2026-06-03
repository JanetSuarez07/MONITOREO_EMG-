import socket
import threading
import eventlet
from flask import Flask, render_template
from flask_socketio import SocketIO
import numpy as np

# =========================================================
# CONFIGURACIÓN DE RED Y SERVIDOR
# =========================================================
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuración UDP para el ESP32
UDP_IP = "0.0.0.0"       # Escucha en todas las interfaces
UDP_PORT = 8800        # Debe coincidir con el puerto en tu ESP32
esp32_address = None     # Se guardará automáticamente cuando el ESP32 hable

# =========================================================
# SERVIDOR UDP (HILO SEPARADO)
# =========================================================
def udp_receiver():
    global esp32_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Servidor UDP escuchando en puerto {UDP_PORT}...")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if not esp32_address:
                esp32_address = addr
                print(f"ESP32 conectado desde: {addr}")
            
            valor_raw = int(data.decode().strip())
            
            # --- AQUÍ APLICARÍAS TUS FILTROS SCIPY ---
            # Filtro sencillo de ejemplo:
            valor_procesado = valor_raw # Reemplaza por tu filtro: lfilter(...)
            
            # Envío a la web en tiempo real
            socketio.emit('nueva_senal', {'valor': valor_procesado})
            
        except Exception as e:
            print(f"Error en UDP: {e}")

# =========================================================
# COMUNICACIÓN BIDIRECCIONAL (SOCKET.IO)
# =========================================================
@socketio.on('cambiar_umbral')
def handle_umbral(data):
    if esp32_address:
        msg = f"UMBRAL:{data['valor']}"
        send_udp(msg)

@socketio.on('control_sistema')
def handle_control(data):
    if esp32_address:
        msg = f"CMD:{data['estado']}"
        send_udp(msg)

def send_udp(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), esp32_address)
    print(f"Enviado al ESP32: {message}")

# =========================================================
# SERVIDOR WEB (RUTAS)
# =========================================================
@app.route('/')
def index():
    return render_template('index.html') # Asegúrate de que index.html esté en la carpeta 'templates'

if __name__ == '__main__':
    # Iniciar el receptor UDP en un hilo independiente
    threading.Thread(target=udp_receiver, daemon=True).start()
    
    # Iniciar el servidor Socket.IO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)