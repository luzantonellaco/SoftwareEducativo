from django.shortcuts import render, redirect  # type: ignore
from django.contrib.auth import authenticate, login # type: ignore
from django.contrib.auth.forms import AuthenticationForm # type: ignore # Se necesita solo para procesar login_view

# ¡IMPORTAMOS TODOS LOS 4 FORMULARIOS QUE HEMOS CREADO!
from .forms import (
    EstudianteRegistroForm, 
    ProfesorRegistroForm,
    EstudianteLoginForm,  # <-- ESTE CAMBIO IMPORTA EL LOGIN DE ESTUDIANTE
    ProfesorLoginForm     # <-- ESTE CAMBIO IMPORTA EL LOGIN DE PROFESOR
) 

# --- VISTAS DE NAVEGACIÓN (LAS QUE YA TENÍAS) ---

def index_view(request):
    """Muestra la página de bienvenida (index.html)."""
    return render(request, 'aplicacion/index.html')

def login_profesor_view(request):
    if request.method == 'POST':
        # CAMBIO CLAVE AQUÍ: Usar tu formulario personalizado
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
        # CAMBIO CLAVE AQUÍ: Usar tu formulario personalizado para GET
        form = ProfesorLoginForm()
    
    return render(request, 'aplicacion/login_profesor.html', {'login_form': form})

def login_estudiante_view(request):
    if request.method == 'POST':
        # CAMBIO CLAVE AQUÍ: Usar tu formulario personalizado
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
        # CAMBIO CLAVE AQUÍ: Usar tu formulario personalizado para GET
        form = EstudianteLoginForm()
    
    return render(request, 'aplicacion/login_estudiante.html', {'login_form': form})

# --- VISTAS DE PROCESAMIENTO (LAS QUE FALTABAN) ---

def login_view(request):
    """
    Procesa el formulario de LOGIN (de profesor o estudiante)
    y redirige según el ROL.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST) 
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Redirección basada en el ROL
                if user.rol == 'PROFESOR':
                    # Fallará hasta que creemos esta URL
                    return redirect('perfil_profesor') 
                elif user.rol == 'ESTUDIANTE':
                    # Fallará hasta que creemos esta URL
                    return redirect('perfil_estudiante') 
            else:
                form.add_error(None, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()


    return render(request, 'aplicacion/login_estudiante.html', {'login_form': form})


def registro_profesor_view(request):
    """Muestra y procesa el formulario de REGISTRO de Profesor."""
    if request.method == 'POST':
        form = ProfesorRegistroForm(request.POST)
        if form.is_valid():
            user = form.save() # El form.save() (de forms.py) se encarga de todo
            login(request, user) # Iniciar sesión automáticamente
            return redirect('perfil_profesor') # Redirigir al perfil
    else:
        form = ProfesorRegistroForm()
        
    return render(request, 'aplicacion/registro_profesor.html', {'form': form})


def registro_estudiante_view(request):
    """Muestra y procesa el formulario de REGISTRO de Estudiante."""
    if request.method == 'POST':
        form = EstudianteRegistroForm(request.POST)
        if form.is_valid():
            user = form.save() # El form.save() (de forms.py) se encarga de todo
            login(request, user) # Iniciar sesión automáticamente
            return redirect('perfil_estudiante') # Redirigir al perfil
    else:
        form = EstudianteRegistroForm()
        
    return render(request, 'aplicacion/registro_estudiante.html', {'form': form})

def perfil_profesor_view(request):
    return render(request, 'aplicacion/perfil_profesor.html')


def perfil_estudiante_view(request):
    return render(request, 'aplicacion/perfil_estudiante.html')