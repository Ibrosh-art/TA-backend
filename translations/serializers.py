# translations/serializers.py
from rest_framework import serializers
from .models import Translation

class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = '__all__'

class TranslationsByLanguageSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'ru': {t.key: t.value_ru for t in instance if t.value_ru},
            'en': {t.key: t.value_en for t in instance if t.value_en},
            'kz': {t.key: t.value_kz for t in instance if t.value_kz},
            'ar': {t.key: t.value_ar for t in instance if t.value_ar},
        }