# Generated by Django 5.1.1 on 2024-10-10 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('innhome_app', '0006_remove_cita_comentarios_cita_hora_cita_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cita',
            name='email_usuario',
            field=models.EmailField(default='default@example.com', max_length=254),
            preserve_default=False,
        ),
    ]