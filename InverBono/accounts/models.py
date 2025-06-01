from django.db import models

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

TIPOS_DOCUMENTO = [
    ('DNI', 'DNI'),
    ('CE', 'Carné de extranjería'),
    ('PAS', 'Pasaporte'),
]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    tipo_documento = models.CharField(max_length=3, choices=TIPOS_DOCUMENTO)
    documento = models.CharField(max_length=20, unique=True)
    celular = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombres', 'apellidos', 'tipo_documento', 'documento', 'celular', 'direccion']

    def __str__(self):
        return self.email
