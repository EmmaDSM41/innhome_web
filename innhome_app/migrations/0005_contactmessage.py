# Generated by Django 5.1.1 on 2024-10-07 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('innhome_app', '0004_propiedad_metros_cuadrados_propiedad_num_banos_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('asunto', models.CharField(max_length=200)),
                ('mensaje', models.TextField()),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]