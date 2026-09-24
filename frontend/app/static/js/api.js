// frontend/app/static/js/api.js

/**
 * Actualiza el threshold (límite de aforo) en FastAPI
 */
async function updateThreshold() {
    try {
        const maxAllowed = parseInt(document.getElementById('thresholdInput').value);
        
        if (isNaN(maxAllowed) || maxAllowed <= 0) {
            showMessage('Por favor ingresa un número válido mayor a 0', 'error');
            return;
        }
        
        addLog('⚙️ Actualizando límite de aforo...');
        
        const response = await fetch('/api/update-threshold/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                max_allowed: maxAllowed,
                establishment_id: 'default'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        addLog(`✅ Límite actualizado a ${result.max_allowed}`);
        document.getElementById('maxAllowed').textContent = result.max_allowed;
        showMessage(`✅ Límite actualizado a ${result.max_allowed} personas`, 'success');
        
    } catch (error) {
        addLog(`❌ Error actualizando threshold: ${error.message}`);
        showMessage(`Error: ${error.message}`, 'error');
    }
}

/**
 * Obtiene el threshold actual
 */
async function getThreshold() {
    try {
        const response = await fetch('/api/get-thresholds/');
        const data = await response.json();
        
        if (data.thresholds && data.thresholds.length > 0) {
            return data.thresholds[0].max_allowed;
        }
        return null;
        
    } catch (error) {
        console.error('Error obteniendo threshold:', error);
        return null;
    }
}

/**
 * Obtiene el histórico de detecciones (si está disponible)
 */
async function getDetectionHistory() {
    try {
        // endpoint no implementado aún en Django urls
        return null;
    } catch (error) {
        console.error('Error obteniendo histórico:', error);
        return null;
    }
}

/**
 * Verifica salud del servidor
 */
async function checkAPIHealth() {
    try {
        const response = await fetch('/health/');
        const data = await response.json();
        return data.status === 'ok';
        
    } catch (error) {
        console.error('API Health check failed:', error);
        return false;
    }
}

/**
 * Envía un evento de auditoría
 */
async function logEvent(eventType, details) {
    try {
        // endpoint no implementado aún
    } catch (error) {
        console.error('Error logging event:', error);
    }
}

/**
 * Obtiene estadísticas del sistema
 */
async function getStats() {
    try {
        // endpoint no implementado aún
        return null;
    } catch (error) {
        console.error('Error obteniendo stats:', error);
        return null;
    }
}

// Inicializar checks al cargar
window.addEventListener('load', async () => {
    // Verificar salud
    const apiHealthy = await checkAPIHealth();
    if (!apiHealthy) {
        addLog('⚠️ No se puede conectar al backend');
    } else {
        addLog('✅ Backend disponible');
    }
    
    // Cargar configuración
    const threshold = await getThreshold();
    if (threshold) {
        document.getElementById('maxAllowed').textContent = threshold;
        document.getElementById('thresholdInput').value = threshold;
        addLog(`⚙️ Límite cargado: ${threshold} personas`);
    }
});
