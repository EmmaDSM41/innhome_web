# Generated by Django 5.1.1 on 2024-10-01 23:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('innhome_app', '0002_usuario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='propiedad',
            name='imagenes',
        ),
        migrations.CreateModel(
            name='ImagenPropiedad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='imagenes_propiedades/')),
                ('propiedad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='innhome_app.propiedad')),
            ],
        ),
    ]
