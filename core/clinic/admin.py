from django.contrib import admin
from clinic.models import Appointment, Doctor, Patient
from clinic.models import Clinic

# Register your models here.

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','experience_years', 'is_available', 'rating')
    search_fields = ['user__name']
    list_filter = ['experience_years']
    ordering = ['user__name']
    
    
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('id','contact_phone')
    search_fields = ['location__name']
    
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'time_slot')
    search_fields = ['doctor__user__name', 'patient__user__name']
    list_filter = ['doctor', 'patient']
    ordering = ['doctor__user__name']