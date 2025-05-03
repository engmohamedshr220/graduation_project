from django_filters import FilterSet
from .models import  Doctor
class DoctorFilter(FilterSet):
    class Meta:
        model = Doctor
        fields = {
            "rating":['lt','gt','range'],
            "user__name":['iexact','contains'],
            "user__gender":['exact'],
            "user__phone":['exact'],
            'city__name': ['exact'],
            
        }