from flask import Flask, render_template, jsonify

# Inicializamos la aplicación
app = Flask(__name__)

# Ruta principal: sirve tu archivo index.html
@app.route('/')
def index():
    return render_template('index.html')

# Ruta de ejemplo para los datos del EMG
# En el futuro, aquí podrías leer de un archivo o puerto serial
@app.route('/api/data')
def get_data():
    # Aquí iría la lógica para enviar la señal EMG
    # Por ahora enviamos un valor de ejemplo en formato JSON
    data = {
        "valor": 0.5,
        "status": "ok"
    }
    return jsonify(data)

# Configuración necesaria para ejecución local
if __name__ == '__main__':
    # Debug=True solo para desarrollo local
    app.run(debug=True, port=5000)