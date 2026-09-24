// frontend/app/static/js/camera.js

let stream = null;
let isCapturing = false;

/**
 * Inicia la captura de la cámara usando getUserMedia
 */
async function startCamera() {
    try {
        addLog('🎬 Solicitando acceso a cámara...');
        
        // Solicitar acceso a cámara
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        });
        
        // Mostrar video en elemento <video>
        const video = document.getElementById('video');
        video.srcObject = stream;
        
        // Actualizar estado de botones
        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('captureBtn').disabled = false;
        
        isCapturing = true;
        addLog('✅ Cámara iniciada correctamente');
        
    } catch (error) {
        addLog(`❌ Error de cámara: ${error.message}`);
        
        if (error.name === 'NotAllowedError') {
            showMessage('Permiso denegado para acceder a la cámara', 'error');
        } else if (error.name === 'NotFoundError') {
            showMessage('No se encontró una cámara disponible', 'error');
        } else {
            showMessage(`Error: ${error.message}`, 'error');
        }
    }
}

/**
 * Detiene la captura de la cámara
 */
function stopCamera() {
    try {
        // Detener stream
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        
        // Limpiar video
        const video = document.getElementById('video');
        video.srcObject = null;
        
        // Actualizar botones
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('captureBtn').disabled = true;
        
        isCapturing = false;
        addLog('🛑 Cámara detenida');
        
    } catch (error) {
        addLog(`Error deteniendo cámara: ${error.message}`);
    }
}

/**
 * Captura un frame del video y lo envía a FastAPI
 */
async function captureFrame() {
    if (!isCapturing || !stream) {
        showMessage('La cámara no está activa', 'error');
        return;
    }
    
    try {
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        
        // Configurar canvas con dimensiones del video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Dibujar video en canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convertir a blob
        canvas.toBlob(async (blob) => {
            await sendToAPI(blob);
        }, 'image/jpeg', 0.95);
        
    } catch (error) {
        addLog(`❌ Error capturando frame: ${error.message}`);
        showMessage(`Error: ${error.message}`, 'error');
    }
}

/**
 * Envía la imagen al servidor Django/FastAPI
 */
async function sendToAPI(blob) {
    try {
        // Crear FormData
        const formData = new FormData();
        formData.append('image', blob, 'frame.jpg');
        formData.append('establishment_id', 'default');
        
        // Mostrar que está procesando
        document.getElementById('captureBtn').disabled = true;
        addLog('📤 Enviando imagen a FastAPI...');
        
        const response = await fetch('/api/count-people/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.error) {
            addLog(`❌ Error: ${result.error}`);
            showMessage(`Error: ${result.error}`, 'error');
        } else {
            addLog(`✅ Respuesta recibida: ${result.people_count} personas detectadas`);
            updateUI(result);
        }
        
    } catch (error) {
        addLog(`❌ Error enviando a API: ${error.message}`);
        showMessage(`Error de conexión: ${error.message}`, 'error');
        
    } finally {
        document.getElementById('captureBtn').disabled = false;
    }
}

/**
 * Obtener CSRF token de cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Auto-captura cada N segundos (opcional)
 */
let autoCaptureInterval = null;

function startAutoCapture(intervalSeconds = 5) {
    if (autoCaptureInterval) return;
    
    addLog(`🔄 Auto-captura activada cada ${intervalSeconds}s`);
    autoCaptureInterval = setInterval(() => {
        if (isCapturing) {
            captureFrame();
        }
    }, intervalSeconds * 1000);
}

function stopAutoCapture() {
    if (autoCaptureInterval) {
        clearInterval(autoCaptureInterval);
        autoCaptureInterval = null;
        addLog('⏸️ Auto-captura desactivada');
    }
}
