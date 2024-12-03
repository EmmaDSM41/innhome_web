from django.urls import path
from . import views
from .views import home, crear_cita

urlpatterns = [
    path('home', home, name='home'),  # Ruta principal
    path('propiedades', views.listar_propiedades, name='listar_propiedades'),
    path('sobre_nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('propiedad/<int:propiedad_id>/', views.detalle_propiedad, name='detalle_propiedad'),
    path('crear_cita/<int:propiedad_id>/', views.crear_cita, name='crear_cita'),
    path('contacto/', views.contactar, name='contactar'),
    path('get_recommendations/', views.get_recommendations, name='get_recommendations'),
    path('agregar_favorito/<int:propiedad_id>/', views.agregar_favorito, name='agregar_favorito'),
    path('ver_favoritos/', views.ver_favoritos, name='ver_favoritos'),
    path('eliminar_favorito/<int:propiedad_id>/', views.eliminar_favorito, name='eliminar_favorito'),
    path('propiedad/<int:propiedad_id>/', views.detalle_propiedad, name='detalle_propiedad'),


 


]

