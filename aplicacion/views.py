from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
import json
from django.utils import timezone
from django.db import DatabaseError

# Importar los modelos nuevos
from .models import QuizAttempt, NivelUnlock
# NO NECESITAMOS AuthenticationForm aquí

# ¡IMPORTAMOS LOS FORMULARIOS!
from .forms import (
    EstudianteRegistroForm, 
    ProfesorRegistroForm,
    EstudianteLoginForm,  
    ProfesorLoginForm     
) 

# --- VISTAS DE NAVEGACIÓN ---

def index_view(request):
    """Muestra la página de bienvenida (index.html)."""
    return render(request, 'aplicacion/index.html')

def login_profesor_view(request):
    if request.method == 'POST':
        form = ProfesorLoginForm(request, data=request.POST) 
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.rol == 'PROFESOR':
                login(request, user)
                return redirect('perfil_profesor')
            else:
                form.add_error(None, "Credenciales inválidas o no eres profesor.")
    else:
        form = ProfesorLoginForm()
    
    return render(request, 'aplicacion/login_profesor.html', {'login_form': form})

def login_estudiante_view(request):
    if request.method == 'POST':
        form = EstudianteLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.rol == 'ESTUDIANTE':
                login(request, user)
                return redirect('perfil_estudiante')
            else:
                form.add_error(None, "Credenciales inválidas o no eres estudiante.")
    else:
        form = EstudianteLoginForm()
    
    return render(request, 'aplicacion/login_estudiante.html', {'login_form': form})

# (Eliminamos login_view redundante)

def registro_profesor_view(request):
    """Muestra y procesa el formulario de REGISTRO de Profesor."""
    if request.method == 'POST':
        form = ProfesorRegistroForm(request.POST)
        if form.is_valid():
            user = form.save() 
            login(request, user) 
            return redirect('perfil_profesor') 
    else:
        form = ProfesorRegistroForm()
        
    return render(request, 'aplicacion/registro_profesor.html', {'form': form})


def registro_estudiante_view(request):
    """Muestra y procesa el formulario de REGISTRO de Estudiante."""
    if request.method == 'POST':
        form = EstudianteRegistroForm(request.POST)
        if form.is_valid():
            user = form.save() 
            login(request, user) 
            # Asegurar que un usuario recién creado no tenga niveles desbloqueados
            try:
                # Eliminamos cualquier registro de NivelUnlock inesperado para este usuario
                NivelUnlock.objects.filter(user=user).exclude(level=1).delete()
            except Exception:
                # No detener el flujo si hay un problema al limpiar la tabla
                pass
            return redirect('perfil_estudiante') 
    else:
        form = EstudianteRegistroForm()
        
    return render(request, 'aplicacion/registro_estudiante.html', {'form': form})

def perfil_profesor_view(request):
    return render(request, 'aplicacion/perfil_profesor.html')


def perfil_estudiante_view(request):
    """Muestra el menú de niveles para el estudiante."""
    # Comprobar en la base de datos si el usuario ya desbloqueó el nivel 2
    unlocked_level_2 = False
    if request.user.is_authenticated:
        try:
            unlocked_level_2 = NivelUnlock.objects.filter(user=request.user, level=2).exists()
        except (DatabaseError, Exception) as e:
            # Si la tabla todavía no existe (migrations no aplicadas) o hay otro error de DB,
            # no rompemos la vista: devolvemos unlocked_level_2 = False como fallback.
            # Esto evita que la interfaz rompa al hacer clic en "Volver al Menú" antes de aplicar migrations.
            unlocked_level_2 = False
            # Opcional: podríamos loguear el error en un logger si se desea.

    return render(request, 'aplicacion/perfil_estudiante.html', {'unlocked_level_2': unlocked_level_2})


@login_required
def save_quiz_result(request):
    """Endpoint que recibe JSON con las respuestas/puntuación y lo guarda en la BD.

    Espera JSON: { score: int, level: int (opcional), answers: [...] }
    Si score > 8 entonces crea/asegura un NivelUnlock para level=2.
    Devuelve JSON { ok: true }
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST required')

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    score = int(payload.get('score', 0))
    level = int(payload.get('level', 1))
    answers = payload.get('answers', {})

    # Guardar intento de quiz
    attempt = QuizAttempt.objects.create(
        user=request.user,
        level=level,
        score=score,
        answers=answers,
    )

    # Si aplica, desbloquear Nivel 2
    try:
        if score > 8:
            NivelUnlock.objects.get_or_create(user=request.user, level=2)
    except Exception:
        # no bloquear el flujo si algo falla secundario
        pass

    return JsonResponse({'ok': True, 'attempt_id': attempt.id})

# --- VISTA DEL JUEGO (NUEVA VISTA) ---
def juego_capa_1_view(request):
    """Renderiza la actividad de arrastrar y soltar para el Nivel 1 (Capa de Aplicación)."""
    return render(request, 'aplicacion/juego_capa_1.html')


def juego_capa_2_view(request):
    """Plantilla placeholder para Nivel 2."""
    return render(request, 'aplicacion/juego_capa_2.html')