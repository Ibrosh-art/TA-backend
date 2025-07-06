from django.contrib import admin
from .models import TranslationNamespace, TranslationKey, TranslationText

class TranslationTextInline(admin.TabularInline):
    model = TranslationText
    extra = 1
    max_num = len(TranslationText.LANGUAGES)

class TranslationKeyAdmin(admin.ModelAdmin):
    inlines = [TranslationTextInline]
    list_display = ('key_path', 'namespace', 'description')
    list_filter = ('namespace',)
    search_fields = ('key_path', 'description')

admin.site.register(TranslationNamespace)
admin.site.register(TranslationKey, TranslationKeyAdmin)