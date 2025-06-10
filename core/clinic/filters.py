from django_filters import FilterSet, filters
from .models import Doctor

class DoctorFilter(FilterSet):
    user__name = filters.CharFilter(method='filter_user_name')
    user__phone = filters.CharFilter(method='filter_user_phone')
    city__name = filters.CharFilter(method='filter_city_name')

    class Meta:
        model = Doctor
        fields = {
            "rating": ['lt', 'gt', 'range'],
            "user__name": ['iexact', 'contains'],
            "user__gender": ['exact'],
            "user__phone": ['exact'],
            'city__name': ['exact'],
        }

    def filter_user_name(self, queryset, name, value):
        if value:
            return queryset.filter(user__name__icontains=value)
        return queryset

    def filter_user_phone(self, queryset, name, value):
        if value:
            return queryset.filter(user__phone=value)
        return queryset

    def filter_city_name(self, queryset, name, value):
        if value:
            return queryset.filter(city__name=value)
        return queryset.filter(city__isnull=False) | queryset.filter(city__isnull=True)