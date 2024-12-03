from django import forms
from .models import ContactMessage, Cita
from .models import Comentario

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario', 'calificacion']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu comentario'}),
            'calificacion': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),  # Botones de radio para calificar de 1 a 5
        }

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['nombre', 'email', 'asunto', 'mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 4}),
        }
class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha_cita', 'hora_cita']
        widgets = {
            'fecha_cita': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_cita': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

