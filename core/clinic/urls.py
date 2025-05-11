from django.urls import path,   include

from rest_framework.routers import DefaultRouter

from .views import DoctorViewSet , DoctorUpdateTokenApi

router = DefaultRouter()

urlpatterns = [
    path('doctors/<uuid:token>/',DoctorUpdateTokenApi.as_view(), name='doctor-update-token') 
]
router.register(r'doctors', DoctorViewSet, basename='doctor')

urlpatterns += router.urls
