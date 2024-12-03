from django.shortcuts import render, redirect
from .models import Propiedad
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.contrib import messages
from .forms import ContactMessageForm
from django import forms
from .forms import CitaForm
from .models import Propiedad, Cita
from django.contrib.auth.decorators import login_required
import openai
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Favorito
from .models import Propiedad, Comentario
from .forms import ComentarioForm
from django.views.decorators.csrf import csrf_exempt
import torch
from django.shortcuts import render
import json
from django.conf import settings
from .models import Propiedad, Direccion
import re
from django.urls import reverse

# Configurar la clave de OpenAI desde settings.py
openai.api_key = settings.OPENAI_API_KEY

# Función para restablecer los filtros
def reset_filters():
    return {
        'ciudad': None,
        'habitaciones': None,
        'banos': None,
        'precio_min': None,
        'precio_max': None,
        'busqueda_completada': False
    }

# Estado inicial de los filtros
filtros = reset_filters()

# Función para corrección básica de errores de ortografía
def corregir_errores(user_message):
    correcciones = {
        'cmdx': 'cdmx',
        'avitaciones': 'habitaciones',
        'vaños': 'baños',
    }
    for error, correccion in correcciones.items():
        user_message = user_message.replace(error, correccion)
    return user_message

# Función para convertir cadenas de precios a números
def convertir_a_numero(cadena):
    cadena = cadena.lower().replace(',', '').replace(' ', '')
    try:
        if 'millon' in cadena or 'm' in cadena:
            return float(cadena.replace('millon', '').replace('m', '')) * 1_000_000
        elif 'mil' in cadena or 'k' in cadena:
            return float(cadena.replace('mil', '').replace('k', '')) * 1_000
        return float(cadena)
    except ValueError:
        raise ValueError("No se pudo convertir el valor ingresado a un número válido.")

@csrf_exempt
def get_recommendations(request):
    if request.method == 'POST':
        global filtros

        user_message = request.POST.get('user_message', '').strip().lower()
        if not user_message:
            return JsonResponse({'response': 'No recibí ningún mensaje. Inténtalo de nuevo.'})

        # Corrige posibles errores de ortografía
        user_message = corregir_errores(user_message)

        # Uso de OpenAI API para generar respuestas
        def usar_openai(prompt):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "Eres un asistente para ayudar a los usuarios a encontrar propiedades basadas en sus preferencias."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except openai.error.OpenAIError as e:
                return f"Ocurrió un error al procesar tu mensaje: {e}"

        response_text = ""

        # Reiniciar filtros si el usuario inicia una nueva búsqueda
        if any(keyword in user_message for keyword in ["quiero", "busco", "me gustaría", "estoy buscando", "ocupo"]):
            filtros = reset_filters()

        if not filtros['busqueda_completada']:
            # Detectar ciudad
            if filtros['ciudad'] is None:
                ciudad_keywords = ['cdmx', 'lerma', 'toluca', 'monterrey']
                for keyword in ciudad_keywords:
                    if keyword in user_message:
                        filtros['ciudad'] = keyword.capitalize()
                        response_text = f"Has seleccionado la ciudad {filtros['ciudad']}. ¿Cuántas habitaciones necesitas?"
                        break
                if filtros['ciudad'] is None:
                    return JsonResponse({'response': "¿En qué ciudad deseas buscar propiedades?"})

            # Detectar número de habitaciones
            elif filtros['habitaciones'] is None:
                match_habitaciones = re.search(r'(\d+)', user_message)
                if match_habitaciones:
                    filtros['habitaciones'] = int(match_habitaciones.group(1))
                    response_text = f"Entendido, {filtros['habitaciones']} habitaciones. ¿Cuántos baños necesitas?"
                else:
                    return JsonResponse({'response': "¿Cuántas habitaciones necesitas?"})

            # Detectar número de baños
            elif filtros['banos'] is None:
                match_banos = re.search(r'(\d+(\.\d+)?)', user_message)
                if match_banos:
                    filtros['banos'] = float(match_banos.group(1))
                    response_text = f"Perfecto, {filtros['banos']} baños. Ahora, ¿cuál es tu rango de precios?"
                else:
                    return JsonResponse({'response': "¿Cuántos baños necesitas?"})

            # Detectar rango de precios
            elif filtros['precio_min'] is None and filtros['precio_max'] is None:
                if any(keyword in user_message for keyword in ['no tengo', 'cualquier precio', 'sin rango']):
                    filtros['precio_min'] = 0
                    filtros['precio_max'] = 99999999
                    filtros['busqueda_completada'] = True
                    response_text = "Búsqueda completa. Aquí tienes las propiedades disponibles."
                else:
                    match_precio = re.search(r'de\s*([\d.,]+\s*[kKmM]?[ilones]*)\s*a\s*([\d.,]+\s*[kKmM]?[ilones]*)', user_message)
                    if match_precio:
                        try:
                            filtros['precio_min'] = convertir_a_numero(match_precio.group(1))
                            filtros['precio_max'] = convertir_a_numero(match_precio.group(2))
                            filtros['busqueda_completada'] = True
                            response_text = "Búsqueda completa. Aquí tienes las propiedades disponibles."
                        except ValueError:
                            return JsonResponse({'response': "No entendí tu rango de precios. Usa algo como 'de 150 mil a 3 millones'."})
                    else:
                        return JsonResponse({'response': "¿Cuál es tu rango de precios? Por ejemplo, 'de 100 mil a 3 millones'."})

        # Realizar búsqueda en la base de datos si los filtros están completos
        if filtros['busqueda_completada']:
            propiedades = Propiedad.objects.filter(
                direccion__ciudad__icontains=filtros['ciudad'],
                num_habitaciones=filtros['habitaciones'],
                num_banos=filtros['banos'],
                precio__gte=filtros['precio_min'],
                precio__lte=filtros['precio_max']
            )

            if propiedades.exists():
                response_text = "Aquí tienes las propiedades disponibles:<br>"
                response_text += "<br>".join(
                    [f"<a href='/propiedad/{prop.id}'>{prop.nombre} en {prop.direccion.ciudad} con {prop.num_habitaciones} habitaciones y {prop.num_banos} baños - Precio: {prop.precio} MXN</a>" for prop in propiedades]
                )
            else:
                response_text = "Lo siento, no encontré propiedades con esos filtros. ¿Te gustaría ajustar los parámetros?"

            # Reiniciar filtros para nueva consulta
            filtros = reset_filters()

        if not response_text:
            response_text = usar_openai(user_message)

        return JsonResponse({'response': response_text})

    return JsonResponse({'response': 'Método no permitido'}, status=405)


def home(request):
    return render(request, 'index.html') 

def sobre_nosotros(request):
    return render(request, 'Sobre_nosotros.html')

def contactar(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            mensaje = form.save()  # Guarda el mensaje en la base de datos

            # Envía el correo
            try:
                send_mail(
                    mensaje.asunto,
                    f"Nombre: {mensaje.nombre}\nCorreo: {mensaje.email}\n\n{mensaje.mensaje}",
                    'al222111329@gmail.com',  # Tu dirección de correo como origen
                    ['al222111329@gmail.com'],  # Tu dirección como destinatario
                    fail_silently=False,
                    # reply_to=[mensaje.email],  # Comentar o eliminar si no es soportado
                )
                messages.success(request, '¡Tu mensaje ha sido enviado correctamente!')
            except Exception as e:
                messages.error(request, f'Error al enviar el correo: {str(e)}')

            return redirect('contactar')  # Redirige al formulario después de enviar
    else:
        form = ContactMessageForm()
    
    return render(request, 'Contacto.html', {'form': form})

def listar_propiedades(request):
    propiedades = Propiedad.objects.all()  # Obtiene todas las propiedades
    return render(request, 'listar_propiedades.html', {'propiedades': propiedades})

class ContactoForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    email = forms.EmailField()
    asunto = forms.CharField(max_length=100)
    mensaje = forms.CharField(widget=forms.Textarea)

def detalle_propiedad(request, propiedad_id):
    propiedad = get_object_or_404(Propiedad, id=propiedad_id)

    # Manejar formulario de contacto
    if request.method == 'POST' and 'contacto_form' in request.POST:
        form = ContactoForm(request.POST)
        if form.is_valid():
            # Aquí puedes manejar el envío de email o cualquier otra lógica
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']
            messages.success(request, 'Tu mensaje ha sido enviado correctamente.')
            return redirect('detalle_propiedad', propiedad_id=propiedad.id)
    else:
        form = ContactoForm()

    # Manejar formulario de comentario
    if request.method == 'POST' and 'comentario_form' in request.POST:
        comentario_form = ComentarioForm(request.POST)
        if comentario_form.is_valid():
            nuevo_comentario = comentario_form.save(commit=False)
            nuevo_comentario.propiedad = propiedad
            nuevo_comentario.usuario = request.user  # Asigna el usuario que realiza el comentario
            nuevo_comentario.save()
            messages.success(request, 'Tu comentario ha sido agregado.')
            return redirect('detalle_propiedad', propiedad_id=propiedad.id)
    else:
        comentario_form = ComentarioForm()

    # Obtener todos los comentarios y calificaciones de la propiedad
    comentarios = Comentario.objects.filter(propiedad=propiedad)

   # Calcular el rango de precios
    rango_minimo = propiedad.precio * 0.9  # 10% menos
    rango_maximo = propiedad.precio * 1.1   # 10% más

    # Filtrar propiedades similares por rango de precios
    propiedades_similares = Propiedad.objects.filter(precio__gte=rango_minimo, precio__lte=rango_maximo).exclude(id=propiedad.id)[:3]

    return render(request, 'detalle_propiedad.html', {
        'propiedad': propiedad,
        'form': form,
        'comentario_form': comentario_form,
        'comentarios': comentarios, 
        'propiedades_similares': propiedades_similares,
    })

@login_required
def crear_cita(request, propiedad_id):
    propiedad = get_object_or_404(Propiedad, id=propiedad_id)
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.propiedad = Propiedad.objects.get(id=propiedad_id)
            cita.usuario = request.user
            cita.email_usuario = request.user.email
            cita.save()

            # Enviar correo al usuario que agendó la cita
            send_mail(
                subject='Confirmación de cita',
                message=f'Estimado {request.user.username}, tu cita para la propiedad "{cita.propiedad.nombre}" ha sido agendada para el {cita.fecha_cita} a las {cita.hora_cita}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )

            # Enviar correo al agente inmobiliario (correo por defecto)
            send_mail(
                subject='Nueva cita agendada',
                message=f'Se ha agendado una nueva cita para la propiedad "{cita.propiedad.nombre}". Fecha: {cita.fecha_cita}, Hora: {cita.hora_cita}, Usuario: {request.user.username}.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['al222111329@gmail.com'],
                fail_silently=False,
            )

            # Mensaje de éxito
            messages.success(request, 'Cita agendada con éxito.')
            return render(request, 'crear_cita.html', {'form': form, 'propiedad': propiedad})

        else:
            # Mensaje de error
            messages.error(request, 'Error al agendar la cita. Por favor, verifica los datos.')
    else:
        form = CitaForm()

    return render(request, 'crear_cita.html', {'form': form, 'propiedad': propiedad})

@login_required
def agregar_favorito(request, propiedad_id):
    if request.method == 'POST':
        propiedad = get_object_or_404(Propiedad, id=propiedad_id)
        favorito, created = Favorito.objects.get_or_create(usuario=request.user, propiedad=propiedad)
        
        if not created:
            # Si ya existe el favorito, lo eliminamos (funcionalidad de "remover favorito")
            favorito.delete()
            agregado = False
        else:
            # Si no existe el favorito, lo agregamos
            agregado = True
        
        # Retornamos una respuesta JSON
        return JsonResponse({'agregado': agregado, 'cantidad_favoritos': Favorito.objects.filter(usuario=request.user).count()})
    return JsonResponse({'error': 'Acción no permitida'}, status=400)

@login_required
def ver_favoritos(request):
    favoritos = Favorito.objects.filter(usuario=request.user)
    return render(request, 'ver_favoritos.html', {'favoritos': favoritos})

@login_required
def favoritos_count(request):
    if request.user.is_authenticated:
        return {'favoritos_count': Favorito.objects.filter(usuario=request.user).count()}
    else:
        return {'favoritos_count': 0}

@login_required
def eliminar_favorito(request, propiedad_id):
    if request.method == 'POST':
        # Obtén al usuario que realiza la solicitud
        user = request.user
        # Obtén el objeto propiedad correspondiente
        propiedad = get_object_or_404(Propiedad, id=propiedad_id)

        # Busca el favorito del usuario que se desea eliminar
        try:
            favorito = user.favorito_set.get(propiedad=propiedad)
            favorito.delete()  # Elimina el favorito
            return JsonResponse({'eliminado': True})
        except Favorito.DoesNotExist:
            return JsonResponse({'eliminado': False})

    return JsonResponse({'eliminado': False})


def detalle_propiedad(request, propiedad_id):
    propiedad = get_object_or_404(Propiedad, id=propiedad_id)
    comentarios = Comentario.objects.filter(propiedad=propiedad)

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            nuevo_comentario = form.save(commit=False)
            nuevo_comentario.propiedad = propiedad
            nuevo_comentario.usuario = request.user
            nuevo_comentario.save()
            messages.success(request, 'Tu comentario ha sido añadido correctamente.')
            return redirect('detalle_propiedad', propiedad_id=propiedad_id)
    else:
        form = ComentarioForm()

    return render(request, 'detalle_propiedad.html', {
        'propiedad': propiedad,
        'comentarios': comentarios,
        'form': form,
    })


def chat_page(request):
    return render(request, 'chat.html')

