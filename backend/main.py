# backend/main.py
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import numpy as np
import cv2
from PIL import Image
from ultralytics import YOLO
import logging
from pydantic import BaseModel
from typing import Optional
import sqlite3
import json
from datetime import datetime

from backend.config import settings

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title=settings.app_name,
    description="API de control de aforo con YOLOv8",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== MODELOS PYDANTIC =====================

class CountPeopleResponse(BaseModel):
    people_count: int
    max_allowed: int
    status: str  # "OK", "WARNING", "CRITICAL"
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "people_count": 8,
                "max_allowed": 10,
                "status": "OK",
                "timestamp": "2024-01-15T10:30:00"
            }
        }

class ThresholdUpdateRequest(BaseModel):
    max_allowed: int
    establishment_id: Optional[str] = "default"
    
    class Config:
        json_schema_extra = {
            "example": {
                "max_allowed": 15,
                "establishment_id": "sala-1"
            }
        }

class ThresholdResponse(BaseModel):
    establishment_id: str
    max_allowed: int
    updated_at: str

# ===================== INICIALIZACIÓN DEL MODELO =====================

model = None

@app.on_event("startup")
async def load_model():
    global model
    try:
        logger.info(f"Cargando modelo YOLOv8-nano desde {settings.model_path}")
        model = YOLO(settings.model_path)  # Descarga automáticamente si no existe
        logger.info("✅ Modelo YOLOv8-nano cargado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error al cargar modelo: {e}")
        raise RuntimeError(f"No se pudo cargar el modelo: {e}")

# ===================== DATABASE (SQLITE SIMPLE) =====================

def init_db():
    """Inicializa base de datos para almacenar límites de aforo"""
    conn = sqlite3.connect("aforo.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS thresholds (
            establishment_id TEXT PRIMARY KEY,
            max_allowed INTEGER,
            updated_at TIMESTAMP
        )
    ''')
    # Insertar valor por defecto
    c.execute('''
        INSERT OR IGNORE INTO thresholds (establishment_id, max_allowed, updated_at)
        VALUES (?, ?, ?)
    ''', ("default", settings.default_max_capacity, datetime.now().isoformat()))
    conn.commit()
    conn.close()

init_db()

def get_max_capacity(establishment_id: str = "default") -> int:
    """Obtiene el límite de aforo de la base de datos"""
    conn = sqlite3.connect("aforo.db")
    c = conn.cursor()
    c.execute("SELECT max_allowed FROM thresholds WHERE establishment_id = ?", (establishment_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else settings.default_max_capacity

# ===================== FUNCIONES DE PROCESAMIENTO =====================

def process_image(image_bytes: bytes) -> int:
    """
    Procesa imagen y retorna cantidad de personas detectadas.
    
    Args:
        image_bytes: Imagen en bytes
        
    Returns:
        int: Número de personas detectadas
    """
    try:
        # Convertir bytes a imagen
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)
        
        # Convertir BGR si es necesario
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Inferencia
        results = model(image_array, conf=settings.confidence_threshold, verbose=False)
        
        # Contar personas (clase 0 en COCO)
        people_count = 0
        for r in results:
            for c in r.boxes.cls:
                if int(c) == 0:  # Clase "person" en COCO
                    people_count += 1
        
        logger.info(f"Personas detectadas: {people_count}")
        return people_count
        
    except Exception as e:
        logger.error(f"Error procesando imagen: {e}")
        raise

# ===================== ENDPOINTS =====================

@app.get("/", tags=["Health"])
async def root():
    """Endpoint de prueba"""
    return {
        "message": "✅ Aforo API está en línea",
        "docs": "/docs",
        "health": "OK"
    }

@app.get("/health", tags=["Health"])
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.post("/api/v1/count-people", response_model=CountPeopleResponse, tags=["Aforo"])
async def count_people(
    file: UploadFile = File(..., description="Imagen para procesar (JPG/PNG)"),
    establishment_id: str = "default"
) -> CountPeopleResponse:
    """
    Procesa una imagen y cuenta la cantidad de personas.
    
    **Parámetros:**
    - `file`: Imagen en formato JPG o PNG
    - `establishment_id`: ID del establecimiento (opcional, default: "default")
    
    **Retorna:**
    - `people_count`: Número de personas detectadas
    - `max_allowed`: Límite de aforo configurado
    - `status`: "OK" (dentro del límite), "WARNING" (90%+), "CRITICAL" (superado)
    - `timestamp`: Hora del procesamiento
    """
    
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo YOLOv8 no está cargado"
        )
    
    try:
        # Validar tipo de archivo
        if file.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=400,
                detail="Solo se aceptan imágenes JPG o PNG"
            )
        
        # Leer imagen
        contents = await file.read()
        
        # Procesar
        people_count = process_image(contents)
        max_allowed = get_max_capacity(establishment_id)
        
        # Determinar estado
        if people_count > max_allowed:
            status_str = "CRITICAL"
        elif people_count >= (max_allowed * 0.9):
            status_str = "WARNING"
        else:
            status_str = "OK"
        
        return CountPeopleResponse(
            people_count=people_count,
            max_allowed=max_allowed,
            status=status_str,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en count-people: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen: {str(e)}"
        )

@app.put("/api/v1/threshold", response_model=ThresholdResponse, tags=["Configuración"])
async def update_threshold(request: ThresholdUpdateRequest) -> ThresholdResponse:
    """
    Actualiza el límite de aforo máximo permitido.
    
    **Parámetros:**
    - `max_allowed`: Nuevo límite (debe ser > 0)
    - `establishment_id`: ID del establecimiento (opcional)
    
    **Retorna:**
    - `establishment_id`: ID del establecimiento actualizado
    - `max_allowed`: Nuevo límite
    - `updated_at`: Fecha/hora de actualización
    """
    
    if request.max_allowed <= 0:
        raise HTTPException(
            status_code=400,
            detail="El límite debe ser mayor a 0"
        )
    
    try:
        conn = sqlite3.connect("aforo.db")
        c = conn.cursor()
        
        # Upsert (insertar o actualizar)
        c.execute('''
            INSERT OR REPLACE INTO thresholds (establishment_id, max_allowed, updated_at)
            VALUES (?, ?, ?)
        ''', (request.establishment_id, request.max_allowed, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Threshold actualizado: {request.establishment_id} → {request.max_allowed}")
        
        return ThresholdResponse(
            establishment_id=request.establishment_id,
            max_allowed=request.max_allowed,
            updated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error actualizando threshold: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando threshold: {str(e)}"
        )

@app.get("/api/v1/thresholds", tags=["Configuración"])
async def get_thresholds():
    """Obtiene todos los límites configurados"""
    try:
        conn = sqlite3.connect("aforo.db")
        c = conn.cursor()
        c.execute("SELECT establishment_id, max_allowed, updated_at FROM thresholds")
        results = c.fetchall()
        conn.close()
        
        return {
            "thresholds": [
                {
                    "establishment_id": r[0],
                    "max_allowed": r[1],
                    "updated_at": r[2]
                }
                for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================== ERROR HANDLERS =====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Excepción no controlada: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
