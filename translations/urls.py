from django.urls import path
from .views import get_translations, update_translation

urlpatterns = [
    path('translations/<str:language>/', get_translations, name='get_translations'),
    path('translations/update/', update_translation, name='update_translation'),
]