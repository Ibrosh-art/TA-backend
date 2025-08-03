# translations/admin.py
from django.contrib import admin
from django import forms
from .models import Translation

class TranslationForm(forms.ModelForm):
    class Meta:
        model = Translation
        fields = '__all__'
        widgets = {
            'value_ru': forms.Textarea(attrs={'rows': 3}),
            'value_en': forms.Textarea(attrs={'rows': 3}),
            'value_kz': forms.Textarea(attrs={'rows': 3}),
            'value_ar': forms.Textarea(attrs={'rows': 3, 'dir': 'rtl'}),
        }

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    form = TranslationForm
    list_display = ('key', 'preview_ru', 'preview_en', 'preview_kz', 'preview_ar', 'updated_at')
    list_filter = ()
    search_fields = ('key', 'value_ru', 'value_en', 'value_kz', 'value_ar')
    ordering = ('key',)
    
    fieldsets = (
        (None, {
            'fields': ('key',)
        }),
        ('Переводы', {
            'fields': (
                ('value_ru',),
                ('value_en',),
                ('value_kz',),
                ('value_ar',),
            )
        }),
    )
    
    # Методы для предпросмотра в списке
    def preview_ru(self, obj):
        return obj.value_ru[:50] + '...' if obj.value_ru else ''
    preview_ru.short_description = 'Русский'
    
    def preview_en(self, obj):
        return obj.value_en[:50] + '...' if obj.value_en else ''
    preview_en.short_description = 'English'
    
    def preview_kz(self, obj):
        return obj.value_kz[:50] + '...' if obj.value_kz else ''
    preview_kz.short_description = 'Қазақша'
    
    def preview_ar(self, obj):
        return obj.value_ar[:50] + '...' if obj.value_ar else ''
    preview_ar.short_description = 'العربية'