// frontend/app/static/js/camera.js

let stream = null;
let isCapturing = false;
let faceDetectionInterval = null;
let modelsLoaded = false;

/**
 * Carga diferida de los modelos de detección para no bloquear la cámara
 */
async function loadFaceModels() {
    if (modelsLoaded) return true;
    try {
        if (typeof faceapi !== 'undefined') {
            await faceapi.nets.tinyFaceDetector.loadFromUri('https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model');
            modelsLoaded = true;
            addLog('🧠 Modelos de detección listos');
            return true;
        }
    } catch (err) {
        addLog(`⚠️ No se pudieron cargar los modelos locales: ${err.message}`);
    }
    return false;
}

/**
 * Encender cámara de forma inmediata
 */
async function startCamera() {
    try {
        addLog('🎬 Solicitando acceso a la cámara...');

        // 1. Obtener acceso al hardware de la cámara
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        });
        
        const video = document.getElementById('video');
        video.srcObject = stream;
        
        video.onloadedmetadata = async () => {
            try {
                await video.play();
            } catch (e) {
                console.warn('Auto-play intervenido por el navegador:', e);
            }

            isCapturing = true;
            
            // Actualizar botones de la interfaz
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('captureBtn').disabled = false;
            
            addLog('✅ Cámara encendida con éxito');

            // Cargar modelos en segundo plano e iniciar seguimiento
            loadFaceModels().then(() => {
                startLiveFaceTracking();
            });
        };

    } catch (error) {
        addLog(`❌ Error en la cámara: ${error.message}`);
        if (typeof showMessage === 'function') {
            showMessage(`Error al acceder a la cámara: ${error.message}`, 'error');
        }
    }
}

/**
 * Detección de rostros y actualización del contador en vivo
 */
function startLiveFaceTracking() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    if (!video || !canvas) return;

    const ctx = canvas.getContext('2d');

    if (faceDetectionInterval) clearInterval(faceDetectionInterval);

    faceDetectionInterval = setInterval(async () => {
        if (!isCapturing || video.paused || video.ended) return;

        // Sincronizar dimensiones del canvas con el video
        if (video.videoWidth && video.videoHeight) {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        }

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        if (typeof faceapi !== 'undefined' && modelsLoaded) {
            try {
                const detections = await faceapi.detectAllFaces(
                    video, 
                    new faceapi.TinyFaceDetectorOptions({
                        inputSize: 224,
                        scoreThreshold: 0.5
                    })
                );
                
                // Dibujar recuadros en canvas
                ctx.strokeStyle = '#00FF00';
                ctx.lineWidth = 3;
                ctx.font = 'bold 16px sans-serif';
                ctx.fillStyle = '#00FF00';

                detections.forEach(detection => {
                    const { x, y, width, height } = detection.box;
                    ctx.strokeRect(x, y, width, height);
                    ctx.fillText('Rostro', x, y > 15 ? y - 8 : 15);
                });

                // Actualizar número en pantalla
                const countDisplay = document.getElementById('peopleCount');
                if (countDisplay) {
                    countDisplay.textContent = detections.length;
                }
            } catch (err) {
                console.error("Error en ciclo de detección:", err);
            }
        }
    }, 100);
}

/**
 * Detener la cámara y reiniciar el lienzo
 */
function stopCamera() {
    try {
        isCapturing = false;

        if (faceDetectionInterval) {
            clearInterval(faceDetectionInterval);
            faceDetectionInterval = null;
        }

        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        
        const video = document.getElementById('video');
        if (video) video.srcObject = null;
        
        const canvas = document.getElementById('canvas');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }

        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('captureBtn').disabled = true;
        
        addLog('🛑 Cámara detenida');
    } catch (error) {
        addLog(`Error al detener: ${error.message}`);
    }
}

/**
 * Capturar foto para el backend (FastAPI)
 */
async function captureFrame() {
    if (!isCapturing || !stream) {
        if (typeof showMessage === 'function') {
            showMessage('La cámara no está activa', 'error');
        }
        return;
    }
    
    try {
        const video = document.getElementById('video');
        
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = video.videoWidth;
        tempCanvas.height = video.videoHeight;
        
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
        
        addLog('📸 Captura manual realizada. Enviando al servidor...');

        tempCanvas.toBlob(async (blob) => {
            if (blob) {
                await sendToAPI(blob);
            }
        }, 'image/jpeg', 0.95);
        
    } catch (error) {
        addLog(`❌ Error capturando: ${error.message}`);
    }
}

/**
 * Envío del fotograma a FastAPI
 */
async function sendToAPI(blob) {
    const captureBtn = document.getElementById('captureBtn');
    
    try {
        const formData = new FormData();
        formData.append('image', blob, 'frame.jpg');
        formData.append('establishment_id', 'default');
        
        if (captureBtn) captureBtn.disabled = true;
        
        const response = await fetch('/api/count-people/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const result = await response.json();
        
        if (result.error) {
            addLog(`❌ Error API: ${result.error}`);
        } else {
            addLog(`✅ Análisis API completado: ${result.people_count} persona(s)`);
            if (typeof updateUI === 'function') {
                updateUI(result);
            }
        }
        
    } catch (error) {
        addLog(`❌ Conexión fallida: ${error.message}`);
    } finally {
        if (captureBtn && isCapturing) {
            captureBtn.disabled = false;
        }
    }
}

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