# translations/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class Translation(models.Model):
    key = models.CharField(
        _('Ключ перевода'), 
        max_length=255,
        unique=True,
        help_text=_('Уникальный идентификатор перевода (например: "header.title")')
    )
    
    # Поля для каждого языка
    value_ru = models.TextField(_('Русский перевод'), blank=True)
    value_en = models.TextField(_('Английский перевод'), blank=True)
    value_kz = models.TextField(_('Казахский перевод'), blank=True)
    value_ar = models.TextField(_('Арабский перевод'), blank=True)
    
    created_at = models.DateTimeField(_('Создано'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Обновлено'), auto_now=True)
    
    class Meta:
        verbose_name = _('Перевод')
        verbose_name_plural = _('Переводы')
        ordering = ['key']
    
    def __str__(self):
        return self.key
    
    def get_all_translations(self):
        return {
            'ru': self.value_ru,
            'en': self.value_en,
            'kz': self.value_kz,
            'ar': self.value_ar,
        }
