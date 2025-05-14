import re
from rest_framework import serializers
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist


import rest_framework.generics
import uuid

from city.models import City
from city.serializers import CitySerializer
from .models import Appointment, Clinic, Doctor, DoctorUpdateToken, Patient, Reviews, TimeSlot

class PatientSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    class Meta:
        model = Patient
        fields = ['id','user']
    
    def get_user(self,obj):
        return {
            "name": obj.user.name,
            "email": obj.user.email,
            "phone": obj.user.phone,
            'city': obj.user.city.name,
            'role': obj.user.role,
            
        }

class ClinicSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Clinic
        fields = ['id','doctor','city','contact_phone']
        read_only_fields = ['id','doctor']

class DoctorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = serializers.UUIDField(read_only=True)
    
    patient_count = serializers.CharField(read_only = True)
    clinics = ClinicSerializer( many = True)
    reviews_count = serializers.CharField(read_only = True)
    rating = serializers.CharField(read_only = True)
    is_available = serializers.BooleanField(read_only = True)
    time_slots = serializers.SerializerMethodField(read_only = True)
    city = serializers.CharField()
    class Meta:
        model = Doctor
        fields = [
                'id','user','experience_years',
                'time_slots','reviews_count','clinics',
                'rating','patient_count','is_available' , 'city'
                ]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = {
            'name': instance.user.name,
            'email': instance.user.email,
            'phone': instance.user.phone
        }
        

        return representation
    def get_time_slots(self,instance):
        booked_slots = Appointment.objects.values_list('time_slot', flat=True)
        time_slots = TimeSlot.objects.exclude(
            id__in=booked_slots).filter(
                start_time__gte=instance.start_hour,
                end_time__lte=instance.end_hour,)
        return TimeSlotSerializer(time_slots, many=True).data

class ReviewsSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only = True)
    class Meta:
        model = Reviews
        fields = ['id','doctor','patient','review','created_at'
                  ]
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'doctor': {'read_only': True},
            'patient': {'read_only': True},
        }

class TimeSlotSerializer(serializers.ModelSerializer):    
    class Meta:
        model = TimeSlot
        fields = ['id','date','start_time','end_time']
        

class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only = True)
    time_slot = TimeSlotSerializer(read_only = True)
    patient = PatientSerializer(read_only = True)
    city = serializers.CharField( read_only=True)
    class Meta:
        model = Appointment
        fields = ['id','doctor','patient','time_slot',
                'status','name','age','phone','city',
                'desc','created_at','updated_at'
                ]
        extra_kwargs = {
            'status': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'doctor': {'read_only': True},
        }

    def to_representation(self, instance):
        representation=  super().to_representation(instance)
        representation['doctor'] = {
            'name': instance.doctor.user.name,
            'email': instance.doctor.user.email,
            'phone': instance.doctor.user.phone,
            'city': instance.doctor.city.name if hasattr(instance.doctor.city,'name') else None,
        }
    
    
        return representation


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['status', 'desc']  # Only allow these fields to be updated
        extra_kwargs = {
            'status': {
                'choices': [Appointment.StatusChoices.CANCELLED, Appointment.StatusChoices.COMPLETED],
                'error_messages': {
                    'invalid_choice': 'Status can only be changed to "cancelled" or "completed"'
                }
            },
            'desc': {'required': False, 'allow_blank': True}
        }

    def validate_status(self, value):
        # Ensure only allowed status changes are permitted
        if value not in [Appointment.StatusChoices.CANCELLED, Appointment.StatusChoices.COMPLETED]:
            raise serializers.ValidationError(
                'Status can only be changed to "cancelled" or "completed"'
            )
        return value
    
    def validate(self, attrs):
        if self.instance.status == Appointment.StatusChoices.CANCELLED and \
        attrs.get('status') == Appointment.StatusChoices.COMPLETED:
            raise serializers.ValidationError(
                'Cannot mark a cancelled appointment as completed'
            )
        return attrs
class AppointmentCreateSerializer(serializers.ModelSerializer):

    time_slot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())
   
    class Meta:
        model = Appointment
        fields = [ 'time_slot', 'patient','name', 'age', 'phone', 'city', 'desc']
    
    def create(self, validated_data):
        request = self.context.get('request')
        patient = request.user.patient if request else None
        doctor = self.context.get('doctor')
        time_slot = validated_data['time_slot']
        
        with transaction.atomic():
            # Check if the time slot is already booked
         
            if Appointment.objects.filter(time_slot=time_slot).exists():
                raise serializers.ValidationError("This time slot is already booked.")

            return Appointment.objects.create(
                patient=patient, 
                doctor=doctor,
                **validated_data
            )
            

    
class DoctorUpdateSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    clinics = ClinicSerializer(many=True) 
    experience_years = serializers.IntegerField()
    profile_img = serializers.ImageField(required=False)
    

    def save(self, **kwargs):
        token = self.validated_data.get('token')
        clinics = self.validated_data.get('clinics')
        experience_years = self.validated_data.get('experience_years')
        profile_img = self.validated_data.get('profile_img')

        try:
            doctor = DoctorUpdateToken.objects.get(token=token).doctor
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        with transaction.atomic():
            # Update doctor's fields
            if experience_years:
                doctor.experience_years = experience_years
            if profile_img:
                doctor.profile_img = profile_img

            # Create clinics if provided
            if clinics:
                for clinic in clinics:
                    # Avoid duplicate clinics
                    if not Clinic.objects.filter(
                        doctor=doctor,
                        city=clinic['city'],
                        contact_phone=clinic['contact_phone']
                    ).exists():
                        Clinic.objects.create(
                            doctor=doctor,
                            city=clinic['city'],
                            contact_phone=clinic['contact_phone']
                        )

            doctor.save()

        return doctor