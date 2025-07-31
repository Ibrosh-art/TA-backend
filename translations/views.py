from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import TranslationNamespace, TranslationKey, TranslationText, TranslationHistory
import logging
import json

logger = logging.getLogger(__name__)
User = get_user_model()

def build_translations_dict(language):
    namespaces = TranslationNamespace.objects.prefetch_related('keys__translations').all()
    result = {}
    
    for ns in namespaces:
        ns_data = {}
        for key in ns.keys.all():
            try:
                translation = key.translations.get(language=language)
                parts = key.key_path.split('.')
                current = ns_data
                
                for part in parts[:-1]:
                    if isinstance(current.get(part), str):
                        current[part] = {}
                    if part not in current or not isinstance(current[part], dict):
                        current[part] = {}
                    current = current[part]
                
                current[parts[-1]] = translation.text
            except TranslationText.DoesNotExist:
                continue
        
        if ns_data:
            result[ns.name] = ns_data
    
    return result

@api_view(['GET'])
def get_translations(request, language):
    cache_key = f'translations_{language}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response(cached_data)
    
    try:
        translations = build_translations_dict(language)
        # Кэшируем на 1 час (можно настроить)
        cache.set(cache_key, translations, 3600)
        return Response(translations)
    except Exception as e:
        logger.error(f"Get translations error: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@transaction.atomic
def update_translation(request):
    logger.info(f"Update request started. Data: {json.dumps(request.data)}")
    
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
        
        parts = path.split('.')
        if len(parts) < 2:
            return Response(
                {'error': 'Invalid path format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        namespace_name = parts[0]
        key_path = '.'.join(parts[1:])
        
        namespace, _ = TranslationNamespace.objects.get_or_create(name=namespace_name)
        key, _ = TranslationKey.objects.get_or_create(
            namespace=namespace,
            key_path=key_path,
            defaults={'description': f"Auto-created for path {path}"}
        )

        existing_translation = TranslationText.objects.filter(
            key=key,
            language=language
        ).first()

        if existing_translation:
            TranslationHistory.objects.create(
                translation=existing_translation,
                old_text=existing_translation.text,
                new_text=value,
                changed_by=request.user if request.user.is_authenticated else None
            )

        translation, created = TranslationText.objects.update_or_create(
            key=key,
            language=language,
            defaults={'text': value}
        )

        # Инвалидируем кэш для этого языка
        cache.delete(f'translations_{language}')
        
        return Response({
            'status': 'success',
            'language': language,
            'updated_at': translation.updated_at
        })
    
    except Exception as e:
        logger.error(f"Translation update failed: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )