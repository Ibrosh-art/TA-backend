from django.db import models

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TranslationHistory(models.Model):
    translation = models.ForeignKey('TranslationText', on_delete=models.CASCADE, related_name='history')
    old_text = models.TextField()
    new_text = models.TextField()
    changed_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.translation.key} changed at {self.changed_at}"
class TranslationNamespace(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class TranslationKey(models.Model):
    namespace = models.ForeignKey(TranslationNamespace, on_delete=models.CASCADE, related_name='keys')
    key_path = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('namespace', 'key_path')

    def __str__(self):
        return f"{self.namespace}.{self.key_path}"

class TranslationText(models.Model):
    LANGUAGES = (
        ('ru', 'Russian'),
        ('en', 'English'),
        ('ar', 'Arabic'),
        ('kz', 'Kazakh'),
    )
    
    key = models.ForeignKey(TranslationKey, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=LANGUAGES)
    text = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('key', 'language')

    def __str__(self):
        return f"{self.key} ({self.language})"