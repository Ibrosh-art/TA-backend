from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import (
    TranslationNamespace, 
    TranslationKey, 
    TranslationText,
    TranslationHistory
)
import logging
import json

logger = logging.getLogger(__name__)
User = get_user_model()

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
                    parts = key.key_path.split('.')
                    current = ns_data
                    for part in parts[:-1]:
                        current = current.setdefault(part, {})
                    current[parts[-1]] = translation.text
                except TranslationText.DoesNotExist:
                    continue
            
            if ns_data:
                result[ns.name] = ns_data
        
        response = Response(result)
        response['Cache-Control'] = 'no-store, max-age=0'
        return response
    
    except Exception as e:
        logger.error(f"Get translations error: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Internal server error'}, 
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
            logger.warning("Missing required fields in request")
            return Response(
                {'error': 'Missing required fields: path, value, language'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        parts = path.split('.')
        if len(parts) < 2:
            logger.warning(f"Invalid path format: {path}")
            return Response(
                {'error': 'Path must contain at least namespace and key'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        namespace_name = parts[0]
        key_path = '.'.join(parts[1:])
        
        try:
            namespace = TranslationNamespace.objects.get(name=namespace_name)
        except TranslationNamespace.DoesNotExist:
            namespace = TranslationNamespace.objects.create(name=namespace_name)
            logger.info(f"Created new namespace: {namespace_name}")

        key, created = TranslationKey.objects.get_or_create(
            namespace=namespace,
            key_path=key_path,
            defaults={'description': f"Auto-created for path {path}"}
        )
        
        if created:
            logger.info(f"Created new key: {namespace_name}.{key_path}")

        # Получаем текущий перевод (если есть)
        existing_translation = TranslationText.objects.filter(
            key=key,
            language=language
        ).first()

        # Создаем запись в истории перед изменением
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
            defaults={
                'text': value,
                # updated_at обновится автоматически благодаря auto_now
            }
        )

        action = "created" if created else "updated"
        logger.info(
            f"Successfully {action} translation. "
            f"Key: {path}, Lang: {language}, "
            f"User: {request.user.username if request.user else 'anonymous'}"
        )

        return Response({
            'status': 'success',
            'action': action,
            'translation_id': translation.id,
            'updated_at': translation.updated_at
        })
    
    except Exception as e:
        logger.error(
            f"Translation update failed. Error: {str(e)}", 
            exc_info=True,
            extra={'request_data': request.data}
        )
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )