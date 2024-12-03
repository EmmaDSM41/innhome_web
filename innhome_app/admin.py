# innhome_app/admin.py

from django.contrib import admin
from .models import Propiedad, ImagenPropiedad, Usuario, Direccion, Cita

class ImagenPropiedadInline(admin.TabularInline):
    model = ImagenPropiedad
    extra = 1  # Permite agregar una nueva imagen al editar la propiedad

@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'direccion', 'vendedor')  # Campos a mostrar en la lista
    search_fields = ('nombre', 'vendedor__username')  # Permite buscar por nombre y vendedor
    list_filter = ('direccion', 'vendedor')  # Filtros en la lista
    inlines = [ImagenPropiedadInline]  # Agrega imágenes en línea

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('calle', 'ciudad', 'estado', 'codigo_postal')

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['propiedad', 'usuario', 'fecha_cita', 'hora_cita', 'estado']
    list_filter = ['estado', 'fecha_cita']

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'tipo_usuario', 'telefono')
    search_fields = ('username', 'email')  # Permite buscar por nombre de usuario y correo

# Si usas un modelo de usuario personalizado, asegúrate de registrarlo también
