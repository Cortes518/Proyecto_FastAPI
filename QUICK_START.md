# ⚡ Quick Start - Empezar en 5 Minutos

## 🎯 Objetivo

Tener la aplicación corriendo localmente en tu máquina para empezar a desarrollar.

---

## Step 1️⃣: Clonar y Configurar (2 min)

```bash
# Clonar repo
git clone <tu-url-github>
cd proyecto-aforo

# Crear entorno virtual
python -m venv venv

# Activar entorno (elige tu SO):
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## Step 2️⃣: Variables de Entorno (1 min)

```bash
# Copiar plantilla
cp .env.example .env

# Editar .env (abre con tu editor favorito)
# Cambiar:
# DEBUG=True
# SECRET_KEY=desarrollo123
# DJANGO_SECRET_KEY=desarrollo456
```

---

## Step 3️⃣: Ejecutar Servidores (2 min)

**Abre DOS terminales** en la carpeta `proyecto-aforo`:

### Terminal 1️⃣: FastAPI Backend
```bash
python -m uvicorn backend.main:app --reload --port 8001
```

Verás:
```
✅ Uvicorn running on http://127.0.0.1:8001
```

### Terminal 2️⃣: Django Frontend
```bash
cd frontend
python manage.py migrate
python manage.py runserver 8000
```

Verás:
```
✅ Django running on http://127.0.0.1:8000
```

---

## ✅ Verificar que Funciona

1. **Frontend Django**: http://localhost:8000
   - Deberías ver pantalla de login
   - Haz click en "Regístrate aquí"
   - Crea un usuario de prueba

2. **API Swagger**: http://localhost:8001/docs
   - Deberías ver documentación interactiva
   - Prueba el endpoint GET `/health`

3. **Dashboard**: http://localhost:8000/dashboard
   - Inicia sesión con tu usuario
   - Click "Iniciar Cámara"
   - Click "Capturar Foto"
   - Deberías ver personas detectadas

---

## 🚨 Si Algo No Funciona

### Error: "ModuleNotFoundError: No module named 'fastapi'"

```bash
# Asegúrate de estar en el entorno virtual activado
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Reinstala dependencias
pip install -r requirements.txt
```

### Error: "Port 8001 already in use"

```bash
# Cambiar puerto
python -m uvicorn backend.main:app --reload --port 8002
```

### Error: "No module named 'django'"

```bash
# Reinstala desde requirements
pip install Django==4.2.7 djangorestframework==3.14.0
```

### Error: "Cámara no funciona"

```bash
# Asegúrate de estar en HTTPS o localhost
# En desarrollo localhost:8000 funciona sin HTTPS
# Si usas otro dominio, necesitas HTTPS
```

---

## 📝 Primeros Pasos de Desarrollo

### Para Cortes (Backend):

1. Revisa `backend/main.py` - aquí están los endpoints
2. Modifica/agrega lógica en `backend/ml/model.py`
3. Actualiza esquemas en `backend/schemas.py`
4. Prueba en http://localhost:8001/docs

### Para Compañera (Frontend):

1. Revisa `frontend/app/templates/dashboard.html` - interfaz
2. Modifica estilos en `frontend/app/static/css/style.css`
3. Actualiza JS en `frontend/app/static/js/camera.js`
4. Prueba en http://localhost:8000/dashboard

---

## 🔄 Git Workflow Diario

```bash
# Al empezar sesión:
git pull origin desarrollo
git checkout -b mi-rama-feature

# Después de hacer cambios:
git add .
git commit -m "feat: descripción de cambios"
git push origin mi-rama-feature

# Abrir Pull Request en GitHub
```

---

## 💡 Tips Útiles

- **Recarga automática**: Ambos servidores (uvicorn y Django) recargan automáticamente cuando cambias archivos
- **Debug en navegador**: F12 para abrir DevTools, pestaña Console
- **Ver logs de FastAPI**: Mira la terminal del puerto 8001
- **Ver logs de Django**: Mira la terminal del puerto 8000
- **Limpiar caché**: `python manage.py collectstatic --clear`

---

## 📞 Preguntas Frecuentes

**P: ¿Por qué dos servidores?**
R: FastAPI es el backend (Python con ML), Django es el frontend (web UI).

**P: ¿Puedo usar solo uno?**
R: No, necesitas ambos para que funcione la aplicación.

**P: ¿Cómo cambio el puerto?**
R: Usa `--port XXXX` en uvicorn o `runserver XXXX` en Django.

**P: ¿Qué pasa con mi .env?**
R: Nunca commitees .env en Git. Está en .gitignore.

---

## 🎓 Próximos Pasos

1. Leer `GUIA_COMMITS_PAREJA.md` para entender los 8 commits
2. Hacer el Commit 1 (estructura base)
3. Empezar a desarrollar según tu asignación (backend o frontend)

---

**¿Listo para empezar?** 🚀

Próximo comando: `git checkout -b commit-1-init`
