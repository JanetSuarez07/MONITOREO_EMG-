from flask import Flask, render_template
from flask_socketio import SocketIO
import os

app = Flask(__name__)
# ping_timeout=60 mantiene la conexión estable aunque el internet sea inestable
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60)

@app.route('/')
def index():
    return render_template('index.html')

# 1. Recibe los datos del puente (appy.py) y los envía a la Web
@socketio.on('datos_procesados')
def handle_data(data):
    # 'nueva_senal' es lo que escucha tu script.js
    socketio.emit('nueva_senal', data)

# 2. Recibe el cambio de umbral de la Web y lo envía al puente (appy.py)
@socketio.on('cambiar_umbral')
def handle_umbral(data):
    print(f"Reenviando nuevo umbral al puente: {data}")
    # Esto es lo que llega al @sio.on('cambiar_umbral') de tu appy.py
    socketio.emit('cambiar_umbral', data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)