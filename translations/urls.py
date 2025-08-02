# translations/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TranslationViewSet

router = DefaultRouter()
router.register(r'translations', TranslationViewSet)

urlpatterns = router.urls + [
    path('translations/all/', 
         TranslationViewSet.as_view({'get': 'all'}), 
         name='translations-all'),
    path('translations/by_language/<str:language>/', 
         TranslationViewSet.as_view({'get': 'by_language'}), 
         name='translations-by-language'),
]