from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TranslationNamespace, TranslationKey, TranslationText
import json

@api_view(['GET'])
def get_translations(request, language):
    try:
        namespaces = TranslationNamespace.objects.prefetch_related(
            'keys__translations'
        ).all()
        
        result = {}
        for ns in namespaces:
            ns_data = {}
            for key in ns.keys.all():
                try:
                    translation = key.translations.get(language=language)
                    # Строим вложенную структуру по точкам в key_path
                    parts = key.key_path.split('.')
                    current = ns_data
                    for part in parts[:-1]:
                        if part not in current or not isinstance(current.get(part), dict):
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = translation.text
                except TranslationText.DoesNotExist:
                    continue
            
            if ns_data:
                result[ns.name] = ns_data
        
        return Response(result)
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def update_translation(request):
    try:
        data = request.data
        path = data.get('path')
        value = data.get('value')
        language = data.get('language')
        
        if not all([path, value, language]):
            return Response(
                {'error': 'Missing required fields'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Разбираем путь: namespace.key.path
        parts = path.split('.')
        if len(parts) < 2:
            return Response(
                {'error': 'Invalid path format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        namespace_name = parts[0]
        key_path = '.'.join(parts[1:])
        
        # Получаем или создаем namespace и key
        namespace, _ = TranslationNamespace.objects.get_or_create(name=namespace_name)
        key, _ = TranslationKey.objects.get_or_create(
            namespace=namespace,
            key_path=key_path
        )
        
        # Обновляем или создаем перевод
        translation, created = TranslationText.objects.update_or_create(
            key=key,
            language=language,
            defaults={'text': value}
        )
        
        return Response({'status': 'success', 'created': created})
    
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )