from django.core.management.base import BaseCommand
from accounts.models import City,Location
# from django.shortcuts import 
class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        for city in City.CityChoices.choices:
            cityName = city[0]
            
            city_instance = City.objects.get_or_create(name = cityName)

            Location.objects.create(city = city_instance[0])
        
        print("Locations created successfully.")