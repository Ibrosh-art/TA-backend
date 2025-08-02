# translations/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Translation
from .serializers import TranslationSerializer, TranslationsByLanguageSerializer

class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    
    @action(detail=False, methods=['get'])
    def all(self, request):
        translations = self.get_queryset()
        serializer = TranslationsByLanguageSerializer(translations)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_language(self, request, language=None):
        translations = self.get_queryset()
        lang_field = f'value_{language}'
        
        # Фильтруем только записи с переводом на запрошенный язык
        valid_translations = [
            t for t in translations 
            if getattr(t, lang_field, None) not in [None, '']
        ]
        
        result = {t.key: getattr(t, lang_field) for t in valid_translations}
        return Response(result)
