from django.contrib import admin
from clinic.models import Doctor
from clinic.models import Clinic

# Register your models here.

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user','experience_years','clinic',)
    search_fields = ['user__name']
    list_filter = ['experience_years']
    ordering = ['user__name']
    
    
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('id','contact_phone')
    search_fields = ['location__name']