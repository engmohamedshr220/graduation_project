from django.db import models
from accounts.models import User
import re
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from accounts.models import City
def upload_doctor_profile_image(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{instance.user.name}-profile-image.{ext}'
    return f'doctor_profile_images/{instance.id}/{filename}'

class Patient(models.Model):
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name='patient')




class Doctor(models.Model):
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_hour = models.TimeField(default=0)
    end_hour = models.TimeField(default=0)
    experience_years = models.IntegerField(default=0)
    reviews_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0 , validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    patient_count = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    profile_img = models.ImageField(upload_to=upload_doctor_profile_image,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL ,related_name='doctors', null=True,blank=True)

class Clinic(models.Model):
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE , null=True, related_name='clinics')
    city = models.ForeignKey(City, on_delete=models.CASCADE ,default=None , related_name='clinics')
    contact_phone = models.CharField(max_length=254)
    
    def __str__(self):
        return f'{self.city} - {self.contact_phone}'
    

class Reviews(models.Model):
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.patient.user.name} - {self.doctor.user.name} - {self.created_at}'
    

class TimeSlot(models.Model):
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date','start_time','end_time'],name='unique_timeslot')
        ]
        

class Appointment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'pending'
        CONFIRMED = 'confirmed', 'confirmed'
        CANCELLED = 'cancelled', 'cancelled'
        COMPLETED = 'completed', 'completed'
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    status = models.CharField(max_length=254,choices=StatusChoices.choices,default=StatusChoices.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=254 , null=True)
    phone = models.CharField(max_length=254,null=True)
    age = models.DecimalField(max_digits=3, decimal_places=0,default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    city = models.CharField(max_length=254,choices=City.CityChoices,default=City.CityChoices.NOT_SPECIFIED)
    desc = models.TextField(blank=True, null=True)
    
    def clean(self):
        if not self.patient and (not self.name or not self.phone or not self.age or not self.city ):
            raise ValidationError('If patient is not provided, name, phone, age and city must be provided')
        if self.patient and (self.name or self.phone or self.age or self.city ):
            raise ValidationError('If patient is provided, name, phone, age and city must not be provided')
    
    def save(self, *args, **kwargs):
        if self.patient:
            self.name = self.patient.user.name
            self.phone = self.patient.user.phone
            self.age = self.patient.user.age
            self.city = self.patient.user.city
            
        self.clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return f'{self.patient.user.name} - {self.doctor.user.name} - {self.time_slot.date} - {self.status}'
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['doctor','time_slot',],name='unique_doctor_timeslot'),
            models.UniqueConstraint(fields=['patient','time_slot'],name='unique_patient_timeslot'),
            
        ]




