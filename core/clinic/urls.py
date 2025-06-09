from django.urls import path,   include

from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, DoctorUpdateTokenApi, DoctorViewSet

router = DefaultRouter()

urlpatterns = [
    path('doctors/<uuid:token>/',DoctorUpdateTokenApi.as_view(), name='doctor-update-token') 
]
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
urlpatterns += router.urls
