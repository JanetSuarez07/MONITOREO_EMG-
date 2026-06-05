from flask import Flask, render_template
from flask_socketio import SocketIO
import os

app = Flask(__name__, template_folder='.')
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('datos_procesados')
def handle_data(data):
    socketio.emit('nueva_senal', data)

@socketio.on('control_sistema')
def handle_control(data):
    print(f"Control recibido: {data}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)