# Generated by Django 4.2.8 on 2025-07-31 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='Уникальный идентификатор перевода (например: "header.title")', max_length=255, unique=True, verbose_name='Ключ перевода')),
                ('value_ru', models.TextField(blank=True, verbose_name='Русский перевод')),
                ('value_en', models.TextField(blank=True, verbose_name='Английский перевод')),
                ('value_kz', models.TextField(blank=True, verbose_name='Казахский перевод')),
                ('value_ar', models.TextField(blank=True, verbose_name='Арабский перевод')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Перевод',
                'verbose_name_plural': 'Переводы',
                'ordering': ['key'],
            },
        ),
    ]
