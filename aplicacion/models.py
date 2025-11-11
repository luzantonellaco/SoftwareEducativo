from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone

# Definimos los roles
ROL_CHOICES = (
    ('PROFESOR', 'Profesor'),
    ('ESTUDIANTE', 'Estudiante'),
    ('ADMIN','Administrador'),
)

class Usuario(AbstractUser):
    """Modelo de Usuario Personalizado para añadir el campo rol."""
    
    # Campo para distinguir el tipo de usuario
    rol = models.CharField(
        max_length=20, 
        choices=ROL_CHOICES, 
        default='ESTUDIANTE',
        verbose_name='Rol de Usuario'
    )

    # Campos específicos para Estudiante
    alias = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name='Alias (Estudiante)'
    )
    
    # Campos específicos para Profesor
    correo_institucional = models.EmailField(
        max_length=254, 
        unique=True, 
        blank=True, 
        null=True, 
        verbose_name='Correo Institucional (Profesor)'
    )
    
    # Campos que ya existen en AbstractUser:
    # username, first_name, last_name, email, password, etc.
    
    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"
        
    class Meta:
        verbose_name = 'Usuario del Sistema'
        verbose_name_plural = 'Usuarios del Sistema'

    def save(self, *args, **kwargs):
        # Si es superusuario, se fuerza el rol ADMIN
        if self.is_superuser:
            self.rol = 'ADMIN'
        super().save(*args, **kwargs)


class NivelUnlock(models.Model):
    """Registra niveles desbloqueados por usuario para persistencia."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='unlocked_levels')
    level = models.PositiveIntegerField()
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'level')
        ordering = ['-unlocked_at']

    def __str__(self):
        return f"{self.user.username} - Nivel {self.level}"


class QuizAttempt(models.Model):
    """Guarda intentos de quizzes con las respuestas para auditoría o revisión."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    level = models.PositiveIntegerField(default=1)
    score = models.IntegerField()
    answers = models.JSONField(default=dict)  # estructura: [{id:..., type:..., answer:...}, ...]
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Nivel {self.level} - {self.score} pts - {self.created_at.isoformat()}"