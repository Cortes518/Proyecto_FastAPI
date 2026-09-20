# 🎯 Sistema de Control de Aforo y Distanciamiento con YOLOv8

Aplicación web para monitoreo de ocupación en tiempo real usando detección de personas con YOLOv8-nano. Desarrollada con **FastAPI** (backend) y **Django** (frontend), deployable en Vercel.

---

## 📋 Características

✅ **Detección de Personas en Tiempo Real**: YOLOv8-nano con inferencia rápida
✅ **Captura de Cámara**: Acceso a cámara web vía `getUserMedia` API
✅ **Dashboard Interactivo**: UI responsive con estadísticas en vivo
✅ **Configuración de Aforo**: Actualizar límites dinámicamente
✅ **Autenticación**: Login/Register con JWT (FastAPI) o Sessions (Django)
✅ **API REST Documentada**: Swagger automático en `/docs`
✅ **Despliegue Serverless**: Configurado para Vercel
✅ **Trabajo en Pareja**: Guía de 8 commits independientes

---

## 🛠️ Stack Tecnológico

**Backend**:
- FastAPI 0.104+
- YOLOv8-nano (Ultralytics)
- SQLite / PostgreSQL
- JWT + Bcrypt para seguridad
- Pydantic para validación

**Frontend**:
- Django 4.2+
- HTML5 + CSS3
- Vanilla JavaScript (sin frameworks)
- getUserMedia API para cámara
- AJAX para comunicación con API

**Despliegue**:
- Vercel (Serverless Functions)
- GitHub (control de versiones)
- Python 3.9+

---

## 📦 Instalación

### 1. Clonar Repositorio

```bash
git clone <tu-repo-url>
cd proyecto-aforo
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus valores:
nano .env  # o abre en tu editor
```

**Variables importantes**:
```env
FASTAPI_ENV=development
SECRET_KEY=tu-clave-secreta-aqui
DJANGO_SECRET_KEY=otra-clave-para-django
DEBUG=True
FASTAPI_URL=http://localhost:8001
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Descargar Modelo YOLOv8

```bash
# Se descarga automáticamente al iniciar, pero puedes pre-descargarlo:
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

---

## 🚀 Ejecución Local

### Terminal 1: FastAPI Backend

```bash
cd backend
python -m uvicorn main:app --reload --port 8001
```

Acceder a:
- API: `http://localhost:8001`
- Docs (Swagger): `http://localhost:8001/docs`
- Health: `http://localhost:8001/health`

### Terminal 2: Django Frontend

```bash
cd frontend
python manage.py migrate
python manage.py runserver 8000
```

Acceder a:
- App: `http://localhost:8000`
- Admin: `http://localhost:8000/admin`

---

## 📱 Uso de la Aplicación

### 1. Registrarse / Iniciar Sesión

```
GET /login          → Página de login
POST /register      → Página de registro
```

### 2. Dashboard

```
GET /dashboard      → Interfaz principal
```

**Funcionalidad**:
- 📹 **Captura de Cámara**: Botones para iniciar/detener
- 📸 **Capturar Foto**: Envía frame a FastAPI
- 📊 **Estadísticas**: Muestra personas detectadas
- ⚙️ **Configurar Aforo**: Cambiar límite máximo
- 📋 **Log**: Historial de eventos

### 3. Endpoints FastAPI

#### Contar Personas

```bash
POST /api/v1/count-people
Content-Type: multipart/form-data

Parámetros:
- file: imagen (JPG/PNG)
- establishment_id: "default" (opcional)

Respuesta:
{
  "people_count": 8,
  "max_allowed": 10,
  "status": "OK",
  "timestamp": "2024-01-15T10:30:00"
}
```

**Estados**:
- `OK`: Dentro del límite
- `WARNING`: 90%+ del límite
- `CRITICAL`: Superado el límite

#### Actualizar Threshold

```bash
PUT /api/v1/threshold
Content-Type: application/json

{
  "max_allowed": 15,
  "establishment_id": "default"
}

Respuesta:
{
  "establishment_id": "default",
  "max_allowed": 15,
  "updated_at": "2024-01-15T10:30:00"
}
```

#### Obtener Thresholds

```bash
GET /api/v1/thresholds

Respuesta:
{
  "thresholds": [
    {
      "establishment_id": "default",
      "max_allowed": 10,
      "updated_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

## 🔐 Autenticación

### JWT en FastAPI (Opcional)

```python
# Solicitar token
POST /api/v1/login
{
  "username": "user",
  "password": "pass"
}

# Usar en headers
Authorization: Bearer <token>
```

### Sessions en Django (Predeterminado)

Los datos de sesión se almacenan automáticamente después de login.

---

## 📁 Estructura de Carpetas

```
proyecto-aforo/
├── backend/                    # FastAPI
│   ├── __init__.py
│   ├── main.py                 # App principal (endpoints)
│   ├── config.py               # Configuración
│   ├── auth.py                 # JWT & seguridad
│   ├── models.py               # SQLAlchemy models
│   └── ml/
│       └── model.py            # YOLOv8 inference
│
├── frontend/                   # Django
│   ├── manage.py
│   ├── frontend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── app/
│       ├── views.py            # Vistas (login, dashboard)
│       ├── models.py           # Modelos Django
│       ├── urls.py
│       ├── templates/
│       │   ├── login.html
│       │   ├── dashboard.html
│       │   └── settings.html
│       └── static/
│           ├── css/
│           │   └── style.css
│           └── js/
│               ├── camera.js   # getUserMedia
│               └── api.js      # Llamadas AJAX
│
├── .env.example                # Plantilla de variables
├── .gitignore
├── vercel.json                 # Config serverless
├── requirements.txt
└── README.md
```

---

## 🧪 Pruebas

### Probar Backend

```bash
# Health check
curl http://localhost:8001/health

# Swagger
http://localhost:8001/docs
```

### Probar Captura de Cámara

1. Ir a `http://localhost:8000/dashboard`
2. Click en "Iniciar Cámara" (permitir acceso)
3. Click en "Capturar Foto"
4. Revisar resultados en panel derecho

### Test Unitarios

```bash
pytest backend/tests/
```

---

## 🚢 Despliegue en Vercel

### 1. Preparar Repositorio

```bash
# Asegurar que todo esté en Git
git add .
git commit -m "deploy: listo para Vercel"
git push origin main
```

### 2. Crear Proyecto en Vercel

```bash
npm i -g vercel
vercel
```

Seleccionar:
- Framework: **Other** (FastAPI + Django)
- Root directory: `.`

### 3. Configurar Variables de Entorno

En **Vercel Dashboard** → Settings → Environment Variables:

```
DJANGO_SECRET_KEY = tu-clave-secreta
SECRET_KEY = tu-clave-secreta-fastapi
DEBUG = False
FASTAPI_ENV = production
ALLOWED_HOSTS = tu-dominio.vercel.app
```

### 4. Deploy

```bash
vercel --prod
```

El sitio estará disponible en: `https://tu-proyecto.vercel.app`

---

## 🐛 Troubleshooting

### Problema: "No se puede conectar a la cámara"

```
Solución:
1. Verificar permisos en navegador
2. Usar HTTPS (Vercel lo hace automático)
3. Probar en navegador diferente
```

### Problema: "Modelo no carga"

```
Solución:
1. Descargar manualmente: python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
2. Verificar espacio en disco (500MB+)
3. Revisar logs de FastAPI
```

### Problema: "CORS error"

```
Solución:
Verificar en backend/config.py:
cors_origins = ["http://localhost:8000", "tu-dominio.com"]
```

### Problema: "JWT token inválido"

```
Solución:
1. Verificar SECRET_KEY en .env
2. Token expirado: hacer login nuevamente
3. Revisar algoritmo (debe ser HS256)
```

---

## 📊 Monitoreo y Logs

### FastAPI Logs

```bash
# Ver en terminal donde corre uvicorn
# Buscar mensajes como:
# ✅ Modelo YOLOv8-nano cargado exitosamente
# Personas detectadas: 8
```

### Django Logs

```bash
# Ver en terminal donde corre runserver
# Buscar errores 404, 500, etc.
```

### Vercel Logs

```bash
vercel logs [--live]
```

---

## 📚 Documentación API Completa

### Todos los Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Estado del servidor |
| POST | `/api/v1/count-people` | Detectar personas en imagen |
| PUT | `/api/v1/threshold` | Actualizar límite de aforo |
| GET | `/api/v1/thresholds` | Obtener límites configurados |
| GET | `/docs` | Documentación Swagger |

---

## 👥 Trabajo en Pareja

Ver `GUIA_COMMITS_PAREJA.md` para:
- Asignación de tareas
- Plan de 8 commits
- Cómo resolver conflictos de Git
- Distribución de trabajo backend/frontend

---

## 📝 Licencia

Proyecto educativo para SENA ADSO - 2024

---

## 🎓 Autores

- **Estudiante 1** (Backend): Cortes
- **Estudiante 2** (Frontend): [Tu Compañera]

**Ficha**: 3406211

---

## 📞 Soporte

Para problemas o dudas:
1. Revisar esta documentación
2. Consultar `GUIA_COMMITS_PAREJA.md`
3. Contactar con tu instructor: César Augusto Moreno Mena

---

**Última actualización**: Enero 2024
**Versión**: 1.0.0
