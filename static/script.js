
//  línea de conexión a esto:
const socket = io({
    transports: ['polling', 'websocket'], // Polling primero para asegurar conexión inicial
    reconnection: true,
    reconnectionAttempts: 10,
    timeout: 10000
});

document.addEventListener('DOMContentLoaded', () => {

    // 2. CONFIGURACIÓN DE LA GRÁFICA (Chart.js)
    const ctx = document.getElementById('emgChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array(50).fill(''),
            datasets: [{
                data: Array(50).fill(0),
                borderColor: '#0d6efd',
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            animation: false,
            scales: {
                y: { min: 0, max: 4095, grid: { color: '#e9ecef' } },
                x: { display: false }
            },
            plugins: { legend: { display: false } }
        }
    });

    // 3. REFERENCIAS Y ESTADOS INICIALES
    const btnIniciar = document.getElementById('btnIniciar');
    const btnDetener = document.getElementById('btnDetener');
    const slider = document.getElementById('umbralRange');
    const valUmbral = document.getElementById('valUmbral');
    const statusText = document.getElementById('status');

    // 4. LÓGICA DE EVENTOS DE RED (Socket.io)
    socket.on('connect', () => {
        console.log("Conectado al servidor de procesamiento.");
        statusText.innerText = "Estado: Conectado (Esperando inicio)";
    });

    socket.on('connect_error', () => {
        statusText.innerText = "Error: Servidor no disponible";
        statusText.style.color = "red";
    });

    // Recibe datos del sensor (Procesados por Python)
    socket.on('nueva_senal', (msg) => {
        if (msg.valor !== undefined) {
            chart.data.datasets[0].data.push(msg.valor);
            chart.data.datasets[0].data.shift();
            chart.update('none');
        }
    });

    // 5. GESTIÓN DE CONTROLES (Eventos del usuario)
    btnIniciar.addEventListener('click', () => {
        socket.emit('control_sistema', { estado: 'iniciar' });
        statusText.innerText = "Estado: Procesando señal EMG...";
        btnIniciar.disabled = true;
        btnDetener.disabled = false;
    });

    btnDetener.addEventListener('click', () => {
        socket.emit('control_sistema', { estado: 'detener' });
        statusText.innerText = "Estado: Detenido";
        btnIniciar.disabled = false;
        btnDetener.disabled = true;
    });

    slider.addEventListener('input', (e) => {
        const nuevoUmbral = e.target.value;
        valUmbral.innerText = nuevoUmbral;
        // Debounce: Podríamos añadir un pequeño retraso aquí si fuera necesario
        socket.emit('cambiar_umbral', { valor: nuevoUmbral });
    });

});