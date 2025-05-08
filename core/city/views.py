from django.shortcuts import render
from .models import City
from .serializers import CitySerializer
from rest_framework.generics import ListAPIView , RetrieveAPIView




class CityListView(ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class CityDetailView(RetrieveAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer


