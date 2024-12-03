from django.db import models
from django.contrib.auth.models import AbstractUser, User

class UserQuery(models.Model):
    query_text = models.CharField(max_length=500)
    intent = models.CharField(max_length=100)
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.query_text} - {self.intent}"

class Direccion(models.Model):
    calle = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.calle}, {self.ciudad}, {self.estado}, {self.codigo_postal}"

class ContactMessage(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.asunto}"

class Propiedad(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    num_habitaciones = models.IntegerField(default=1)
    num_banos = models.DecimalField(max_digits=2, decimal_places=1, default=1)
    metros_cuadrados = models.IntegerField(default=50)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class ImagenPropiedad(models.Model):
    propiedad = models.ForeignKey(Propiedad, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='imagenes_propiedades/')

    def __str__(self):
        return f"Imagen de {self.propiedad.nombre}"

class Cita(models.Model):
    propiedad = models.ForeignKey('Propiedad', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    email_usuario = models.EmailField()
    fecha_cita = models.DateField()
    hora_cita = models.TimeField()
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada')])

    def __str__(self):
        return f"{self.usuario} - {self.propiedad.nombre} - {self.fecha_cita} {self.hora_cita}"

class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
    ]
    
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
    )

    def __str__(self):
        return self.username

class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'propiedad')

    def __str__(self):
        return f'{self.usuario.username} - {self.propiedad.nombre}'

class Comentario(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comentario = models.TextField()
    calificacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Calificación de 1 a 5
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comentario de {self.usuario.username} en {self.propiedad.titulo}'
