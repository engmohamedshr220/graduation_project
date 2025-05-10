from django.core.management.base import BaseCommand
from city.models import City
# from django.shortcuts import 
class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        for city in City.CityChoices.choices:
            cityName = city[0]
            
            City.objects.get_or_create(name = cityName)

            
        
        print("Locations created successfully.")