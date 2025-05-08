from django.db import models
import uuid
# Create your models here.

class City(models.Model):
    class CityChoices(models.TextChoices):
        # Menofia
        SHEBIN_EL_KOM = 'Shebin El-Kom', 'Shebin El-Kom'
        MENOUF = 'Menouf', 'Menouf'
        TOOKH_TANBESHA = 'Tookh Tanbesha', 'Tookh Tanbesha'
        QUESNA = 'Quesna', 'Quesna'
        BERKET_EL_SABAA = 'Berket El-Sabaa', 'Berket El-Sabaa'
        ASHAN = 'Ashan', 'Ashan'
        SHIBRA_BALLOULA = 'Shibra Balloula', 'Shibra Balloula'
        SADAT_CITY = 'Sadat City', 'Sadat City'

        # Cairo
        NASR_CITY = 'Nasr City', 'Nasr City'
        HELIOPOLIS = 'Heliopolis', 'Heliopolis'
        MAADI = 'Maadi', 'Maadi'
        ZAMALEK = 'Zamalek', 'Zamalek'
        DOWNTOWN = 'Downtown', 'Downtown'
        NEW_CAIRO = 'New Cairo', 'New Cairo'
        MOKATTAM = 'Mokattam', 'Mokattam'
        SHERATON = 'Sheraton', 'Sheraton'
        GARDEN_CITY = 'Garden City', 'Garden City'
        ABBASIA = 'Abbasia', 'Abbasia'

        # Alexandria
        SMOUHA = 'Smouha', 'Smouha'
        MIAMI = 'Miami', 'Miami'
        RUSHEDY = 'Roushdy', 'Roushdy'
        GLEEM = 'Gleem', 'Gleem'
        STANLEY = 'Stanley', 'Stanley'
        LOURAN = 'Louran', 'Louran'
        AL_MANSHEYA = 'Al Mansheya', 'Al Mansheya'
        BOLKLY = 'Bolkly', 'Bolkly'

        # Giza
        DOKKI = 'Dokki', 'Dokki'
        MOHANDSEEN = 'Mohandeseen', 'Mohandeseen'
        AGOUZA = 'Agouza', 'Agouza'
        HARAM = 'Haram', 'Haram'
        FAYSAL = 'Faysal', 'Faysal'
        OCTOBER = 'October', 'October'
        SHEIKH_ZAYED = 'Sheikh Zayed', 'Sheikh Zayed'
        IMBABA = 'Imbaba', 'Imbaba'
        
        NOT_SPECIFIED = 'Not Specified', 'Not Specified'
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    name = models.CharField(max_length=50, choices=CityChoices.choices)

    def __str__(self):
        return self.name
    
