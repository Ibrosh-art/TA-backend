import json
import os
from django.core.management.base import BaseCommand
from translations.models import Translation

class Command(BaseCommand):
    help = 'Import translations from React i18next locale files'

    def add_arguments(self, parser):
        parser.add_argument('base_path', type=str, help='Path to locales directory (e.g. src/locales)')

    def handle(self, *args, **options):
        base_path = options['base_path']
        lang_codes = ['en', 'ru', 'kz', 'ar']
        sections = ['common', 'legal', 'stats']  # Ваши разделы

        for section in sections:
            section_path = os.path.join(base_path, section)
            if not os.path.exists(section_path):
                self.stdout.write(self.style.WARNING(f"Section {section} not found, skipping"))
                continue

            for lang in lang_codes:
                file_path = os.path.join(section_path, f"{lang}.json")
                if not os.path.exists(file_path):
                    continue

                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        prefix = f"{section}."  # Добавляем префикс раздела
                        self.process_translations(data, lang, prefix)
                        self.stdout.write(self.style.SUCCESS(
                            f"Processed {lang} translations from {section}"
                        ))
                    except json.JSONDecodeError as e:
                        self.stdout.write(self.style.ERROR(
                            f"Error parsing {file_path}: {str(e)}"
                        ))

    def process_translations(self, data, lang, prefix=""):
        for key, value in data.items():
            if isinstance(value, dict):
                # Если значение - объект (для вложенных переводов)
                for sub_key, sub_value in value.items():
                    full_key = f"{prefix}{key}.{sub_key}"
                    self.create_translation(full_key, lang, sub_value)
            else:
                # Обычный перевод
                full_key = f"{prefix}{key}"
                self.create_translation(full_key, lang, value)

    def create_translation(self, key, lang, value):
        # Для модели с полями value_ru, value_en и т.д.
        translation, created = Translation.objects.get_or_create(key=key)
        
        # Динамически устанавливаем поле по языку
        field_name = f'value_{lang}'
        if hasattr(translation, field_name):
            setattr(translation, field_name, value)
            translation.save()
        else:
            self.stdout.write(self.style.WARNING(
                f"No field {field_name} for key {key}"
            ))

        # Альтернатива для старой модели:
        # Translation.objects.update_or_create(
        #     key=key,
        #     language=lang,
        #     defaults={'value': value}
        # )