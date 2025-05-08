from django.urls import path
from .views import CityListView , CityDetailView

urlpatterns = [
    path('' , CityListView.as_view(), name='get cities' ),
    path('<int:pk>/' , CityDetailView.as_view(), name='get city' ),
]