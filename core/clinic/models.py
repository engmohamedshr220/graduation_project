from django.db import models
from accounts.models import User
import re
import uuid
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from accounts.models import City

def upload_doctor_certification(instance, filename):
    file_ext = filename.split('.')[-1]
    filename = f'{instance.user.name}-certification.{file_ext}'
    return f'doctor_certification/{instance.id}/{filename}'

class Patient(models.Model):
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name='patient')

class Doctor(models.Model):
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='doctor')
    start_hour = models.TimeField( null=True ,blank=True)
    end_hour = models.TimeField( null=True ,blank=True) 
    experience_years = models.IntegerField(default=0)
    reviews_count = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0 , validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    patient_count = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    certification = models.ImageField( upload_to= upload_doctor_certification,max_length=254 , null=True , blank=True)
    is_active = models.BooleanField(default=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL ,related_name='doctors', null=True ,blank=True)



class Clinic(models.Model):
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE , null=True ,blank=True, related_name='clinics')
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
    id = models.UUIDField(primary_key=True, unique=True, verbose_name="id", default=uuid.uuid4)
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    status = models.CharField(max_length=254, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    time_slot = models.ForeignKey('TimeSlot', on_delete=models.CASCADE)
    
    name = models.CharField(max_length=254, null=True, blank=True)
    phone = models.CharField(max_length=254, null=True, blank=True)
    age = models.DecimalField(max_digits=3, decimal_places=0, default=0, 
                            validators=[MinValueValidator(0), MaxValueValidator(100)],
                            null=True, blank=True)
    city = models.CharField(max_length=254, null=True, blank=True)  
    def save(self, *args, **kwargs):
        # If this is a patient appointment and fields are not set, copy from patient
        if self.patient:
            if not self.name:
                self.name = self.patient.user.name
            if not self.phone:
                self.phone = self.patient.user.phone
            if not self.age and hasattr(self.patient, 'age'):
                self.age = self.patient.user.age
            if not self.city and hasattr(self.patient.user, 'city'):
                # Ensure city is stored as a string
                self.city = str(self.patient.user.city) if self.patient.user.city else None

        # Clean before save to ensure validation
        self.clean()
        super().save(*args, **kwargs)
    desc = models.TextField(blank=True, null=True)
    
    def clean(self):
        # For guest appointments (no patient), all guest fields must be provided
        if not self.patient:
            if not all([self.name, self.phone, self.age, self.city]):
                raise ValidationError('For guest appointments, name, phone, age and city must be provided')
        

    
    def save(self, *args, **kwargs):
        # If this is a patient appointment and fields are not set, copy from patient
        if self.patient:
            if not self.name:
                self.name = self.patient.user.name
            if not self.phone:
                self.phone = self.patient.user.phone
            if not self.age and hasattr(self.patient, 'age'):
                self.age = self.patient.user.age
            if not self.city and hasattr(self.patient.user, 'city'):
                self.city = self.patient.user.city.name if self.patient.user.city else None
        
        # Clean before save to ensure validation
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        patient_name = self.patient.user.name if self.patient else self.name
        return f'{patient_name} - {self.doctor.user.name} - {self.time_slot.date} - {self.status}'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'time_slot'], name='unique_doctor_timeslot'),
            models.UniqueConstraint(fields=['patient', 'time_slot'], name='unique_patient_timeslot',
                                   condition=models.Q(patient__isnull=False)),
        ]
    




class DoctorUpdateToken(models.Model):
    
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return self.created_at < timezone.now() - timezone.timedelta(minutes=15)
    
    def __str__(self):
        return f'{self.doctor.user.name} - {self.token}'