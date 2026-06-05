from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
# El '*' permite que tu appy.py local pueda conectarse desde cualquier lugar
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print("Un cliente (tu appy.py) se ha conectado.")

@socketio.on('datos_procesados')
def handle_datos(data):
    # Aquí recibirás los datos de tu appy.py
    print(f"Recibiendo: {data}")
    # Opcional: Emitir a un dashboard web si tienes uno
    socketio.emit('actualizar_frontend', data)

if __name__ == '__main__':
    # Render asigna automáticamente el puerto en la variable de entorno PORT
    # pero si falla, usaremos 10000 por defecto
    import os
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)