import json
import os
from django.core.management.base import BaseCommand
from translations.models import TranslationNamespace, TranslationKey, TranslationText

class Command(BaseCommand):
    help = 'Load translations from JSON files into database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            help='Path to locales directory',
            default='../frontend/src/locales'
        )
    
    def handle(self, *args, **options):
        base_path = options['path']
        languages = ['ru', 'en', 'ar', 'kz']
        namespaces = ['common', 'legal', 'stats']
        
        for ns in namespaces:
            namespace, _ = TranslationNamespace.objects.get_or_create(name=ns)
            
            for lang in languages:
                file_path = os.path.join(base_path, ns, f'{lang}.json')
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.process_data(namespace, lang, data)
                    
                    self.stdout.write(self.style.SUCCESS(f'Successfully loaded {ns}/{lang}.json'))
                except FileNotFoundError:
                    self.stdout.write(self.style.WARNING(f'File not found: {ns}/{lang}.json'))
                except json.JSONDecodeError:
                    self.stdout.write(self.style.ERROR(f'Invalid JSON in {ns}/{lang}.json'))
    
    def process_data(self, namespace, language, data, parent_key=''):
        for key, value in data.items():
            current_key = f'{parent_key}.{key}' if parent_key else key
            
            if isinstance(value, dict):
                self.process_data(namespace, language, value, current_key)
            else:
                # Создаем или получаем ключ перевода
                translation_key, _ = TranslationKey.objects.get_or_create(
                    namespace=namespace,
                    key_path=current_key
                )
                
                # Создаем или обновляем перевод
                TranslationText.objects.update_or_create(
                    key=translation_key,
                    language=language,
                    defaults={'text': str(value)}
                )