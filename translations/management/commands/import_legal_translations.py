# translations/management/commands/import_legal_translations.py
import json
import os
from django.core.management.base import BaseCommand
from translations.models import Translation

class Command(BaseCommand):
    help = 'Import translations ONLY from legal folder'

    def add_arguments(self, parser):
        parser.add_argument('base_path', type=str, help='Base path to locales directory')

    def handle(self, *args, **options):
        base_path = options['base_path']
        legal_path = os.path.join(base_path, 'legal')
        
        if not os.path.exists(legal_path):
            self.stdout.write(self.style.ERROR(f'Legal folder not found at: {legal_path}'))
            return

        lang_codes = ['en', 'ru', 'kz', 'ar']
        
        for lang in lang_codes:
            file_path = os.path.join(legal_path, f'{lang}.json')
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f'No {lang} translations in legal folder'))
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.import_legal_translations(data, lang)
                    self.stdout.write(self.style.SUCCESS(f'Imported {lang} legal translations'))
                except json.JSONDecodeError as e:
                    self.stdout.write(self.style.ERROR(f'Error parsing {file_path}: {str(e)}'))

    def import_legal_translations(self, data, lang):
        """Импорт переводов из legal-файлов без префиксов"""
        for key, value in data.items():
            if isinstance(value, dict):
                # Обработка вложенных структур
                for nested_key, nested_value in value.items():
                    full_key = f'{key}.{nested_key}'
                    self.save_translation(full_key, lang, nested_value)
            else:
                self.save_translation(key, lang, value)

    def save_translation(self, key, lang, value):
        """Сохранение перевода в базу"""
        # Для модели с полями value_ru, value_en и т.д.
        translation, created = Translation.objects.get_or_create(key=key)
        setattr(translation, f'value_{lang}', value)
        translation.save()