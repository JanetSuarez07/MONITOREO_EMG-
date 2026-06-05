from flask import Flask
from flask_socketio import SocketIO
import os

app = Flask(__name__)
# Definimos el objeto socketio
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('datos_procesados')
def handle_data(data):
    print(f"Datos recibidos: {data}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)