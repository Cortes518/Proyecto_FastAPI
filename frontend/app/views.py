# frontend/app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
import requests
import json
import base64
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# ===================== AUTENTICACIÓN =====================

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de login"""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña inválidos'
            })
    
    return render(request, 'login.html')

@require_http_methods(["GET", "POST"])
def register_view(request):
    """Vista de registro"""
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            return render(request, 'register.html', {
                'error': 'Las contraseñas no coinciden'
            })
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'El usuario ya existe'
            })
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            login(request, user)
            return redirect('dashboard')
        except Exception as e:
            logger.error(f"Error en registro: {e}")
            return render(request, 'register.html', {
                'error': 'Error al crear usuario'
            })
    
    return render(request, 'register.html')

@login_required(login_url='login')
def logout_view(request):
    """Logout"""
    logout(request)
    return redirect('login')

# ===================== DASHBOARD =====================

@login_required(login_url='login')
def dashboard(request):
    """Vista principal del dashboard"""
    context = {
        'fastapi_url': settings.FASTAPI_URL,
        'user': request.user,
    }
    return render(request, 'dashboard.html', context)

# ===================== API PROXY A FASTAPI =====================

@login_required(login_url='login')
@require_http_methods(["POST"])
def count_people(request):
    """
    Proxy POST a FastAPI /api/v1/count-people
    """
    try:
        logger.info(f"POST: {request.POST}")
        logger.info(f"FILES: {request.FILES}")
        
        if 'image' not in request.FILES:
            logger.error("No image in request.FILES")
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        image_file = request.FILES['image']
        establishment_id = request.POST.get('establishment_id', 'default')
        
        # Leer los bytes de la imagen
        image_bytes = image_file.read()
        logger.info(f"Image received, size: {len(image_bytes)} bytes, content_type: {image_file.content_type}")
        
        # Preparar multipart form data asegurando el content_type
        # Forzamos 'image/jpeg' para evitar que FastAPI lo rechace
        files = {'file': ('frame.jpg', image_bytes, 'image/jpeg')}
        data = {'establishment_id': establishment_id}
        
        # Llamar a FastAPI
        fastapi_url = f"{settings.FASTAPI_URL}/api/v1/count-people"
        logger.info(f"Sending to FastAPI: {fastapi_url}")
        response = requests.post(fastapi_url, files=files, data=data, timeout=30)
        
        logger.info(f"FastAPI Status: {response.status_code}")
        logger.info(f"FastAPI Response: {response.text}")
        
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            logger.error(f"FastAPI error: {response.text}")
            return JsonResponse({
                'error': 'Error en el servidor FastAPI',
                'details': response.text
            }, status=response.status_code)
    
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Timeout - servidor FastAPI no responde'}, status=504)
    except requests.exceptions.ConnectionError:
        return JsonResponse({'error': 'No se puede conectar al servidor FastAPI'}, status=503)
    except Exception as e:
        logger.error(f"Error en count_people: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required(login_url='login')
@require_http_methods(["PUT"])
def update_threshold(request):
    """
    Proxy PUT a FastAPI /api/v1/threshold
    """
    try:
        data = json.loads(request.body)
        
        if 'max_allowed' not in data:
            return JsonResponse({'error': 'max_allowed es requerido'}, status=400)
        
        establishment_id = data.get('establishment_id', 'default')
        
        # Llamar a FastAPI
        fastapi_url = f"{settings.FASTAPI_URL}/api/v1/threshold"
        response = requests.put(
            fastapi_url,
            json={
                'max_allowed': data['max_allowed'],
                'establishment_id': establishment_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({
                'error': 'Error actualizando threshold',
                'details': response.text
            }, status=response.status_code)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error(f"Error en update_threshold: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# ===================== CONFIGURACIÓN =====================

@login_required(login_url='login')
def settings_view(request):
    """Vista de configuración del aforo"""
    if request.method == "POST":
        try:
            max_allowed = int(request.POST.get('max_allowed', 10))
            
            # Llamar a FastAPI
            fastapi_url = f"{settings.FASTAPI_URL}/api/v1/threshold"
            response = requests.put(
                fastapi_url,
                json={'max_allowed': max_allowed, 'establishment_id': 'default'}
            )
            
            if response.status_code == 200:
                return render(request, 'settings.html', {
                    'success': 'Configuración actualizada correctamente',
                    'max_allowed': max_allowed
                })
            else:
                return render(request, 'settings.html', {
                    'error': 'Error al actualizar configuración'
                })
        except Exception as e:
            return render(request, 'settings.html', {
                'error': f'Error: {str(e)}'
            })
    
    context = {
        'fastapi_url': settings.FASTAPI_URL,
    }
    return render(request, 'settings.html', context)

@login_required(login_url='login')
def get_thresholds(request):
    """Obtiene los thresholds actuales desde FastAPI"""
    try:
        fastapi_url = f"{settings.FASTAPI_URL}/api/v1/thresholds"
        response = requests.get(fastapi_url, timeout=10)
        
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Error obteniendo thresholds'}, status=500)
    
    except Exception as e:
        logger.error(f"Error en get_thresholds: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# ===================== HEALTH CHECK =====================

def health(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'ok', 'service': 'Django Frontend'})
