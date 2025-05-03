from django.urls import path,   include

from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet

router = DefaultRouter()

urlpatterns = [
    
]
router.register(r'doctors', DoctorViewSet, basename='doctor')

urlpatterns += router.urls
