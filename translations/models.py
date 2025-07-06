from django.db import models

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