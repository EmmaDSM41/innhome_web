import json
import openai
from .models import Propiedad, Direccion
from django.conf import settings


# Configuración de tu clave de API de OpenAI
openai.api_key = settings.OPENAI_API_KEY

# Función para generar respuestas usando GPT-3.5-Turbo
def generar_respuesta_openai(mensaje, contexto=None):
    try:
        mensajes = [{"role": "user", "content": mensaje}]
        
        if contexto:
            for mensaje_previo in contexto:
                mensajes.insert(0, {"role": "user", "content": mensaje_previo})
        
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=mensajes,
            max_tokens=150,
            temperature=0.7
        )
        return respuesta.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error al generar respuesta con OpenAI: {e}")
        return "Lo siento, ocurrió un error al procesar tu solicitud."

# Función para buscar propiedades en la base de datos
def buscar_propiedades(contexto):
    ubicacion = contexto.get("ubicacion")
    habitaciones = contexto.get("habitaciones")
    baños = contexto.get("baños")

    # Filtrar propiedades por ubicación (ciudad en el modelo Direccion)
    if ubicacion:
        direcciones = Direccion.objects.filter(ciudad__iexact=ubicacion)
    else:
        direcciones = Direccion.objects.all()

    propiedades = Propiedad.objects.filter(direccion__in=direcciones)

    if habitaciones:
        propiedades = propiedades.filter(num_habitaciones=habitaciones)
    if baños:
        propiedades = propiedades.filter(num_banos=baños)

    if not propiedades.exists():
        return "No se encontraron propiedades que coincidan con tu búsqueda."

    respuesta = "Estas son algunas propiedades que coinciden con tu búsqueda:\n"
    for propiedad in propiedades[:5]:
        respuesta += (f"Nombre: {propiedad.nombre}, Precio: {propiedad.precio}, "
                      f"Dirección: {propiedad.direccion.calle}, Ciudad: {propiedad.direccion.ciudad}\n")
    return respuesta

# Función principal para procesar el mensaje del usuario
def procesar_mensaje(mensaje, request):
    contexto = request.session.get("contexto", {})

    if "cdmx" in mensaje:
        contexto["ubicacion"] = "CDMX"
    elif "lerma" in mensaje:
        contexto["ubicacion"] = "Lerma"
    
    if "habitaciones" in mensaje:
        contexto["habitaciones"] = int(''.join(filter(str.isdigit, mensaje)))
    if "baños" in mensaje:
        contexto["baños"] = int(''.join(filter(str.isdigit, mensaje)))
    if "precio" in mensaje:
        contexto["precio"] = int(''.join(filter(str.isdigit, mensaje)))

    request.session["contexto"] = contexto

    # Si tenemos suficiente información, hacemos la búsqueda en la base de datos
    if "ubicacion" in contexto:
        respuesta_bd = buscar_propiedades(contexto)
        if respuesta_bd:
            return respuesta_bd

    # Si falta información, pedimos al usuario más detalles utilizando OpenAI
    if "ubicacion" not in contexto:
        return generar_respuesta_openai("¿En qué ubicación estás buscando la propiedad?")
    elif "habitaciones" not in contexto:
        return generar_respuesta_openai("¿Cuántas habitaciones necesitas?")
    elif "baños" not in contexto:
        return generar_respuesta_openai("¿Cuántos baños necesitas?")
    elif "precio" not in contexto:
        return generar_respuesta_openai("¿Cuál es el precio máximo que estás dispuesto a pagar?")

    return "Solo puedo responder preguntas relacionadas con las propiedades disponibles en nuestra página."
