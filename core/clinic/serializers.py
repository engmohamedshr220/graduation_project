from rest_framework import serializers
from django.db import transaction
from accounts.serializers import MyUserSerializer
from .models import Patient , Doctor ,Clinic,TimeSlot,Appointment

class PatientSerializer(serializers.ModelSerializer):
    user = MyUserSerializer()
    class Meta:
        model = Patient
        fields = ['id','user']
    

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ['id','city','contact_phone']

class DoctorSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    user = MyUserSerializer(read_only = True)
    clinic = ClinicSerializer(read_only = True)
    patient_count = serializers.CharField(read_only = True)
    reviews_count = serializers.CharField(read_only = True)
    rating = serializers.CharField(read_only = True)
    is_available = serializers.BooleanField(read_only = True)
    time_slots = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Doctor
        fields = [
                'id','user','experience_years','clinic',
                'time_slots','start_hour','end_hour','reviews_count',
                'rating','patient_count','is_available','profile_img'
                ]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = {
            'name': instance.user.name,
            'email': instance.user.email,
            'phone': instance.user.phone
        }
        representation['clinic'] = {
            'city': instance.clinic.city.name,
            'contact_phone': instance.clinic.contact_phone
        }

        return representation
    def get_time_slots(self,instance):
        booked_slots = Appointment.objects.values_list('time_slot', flat=True)
        time_slots = TimeSlot.objects.exclude(id__in=booked_slots)
        return TimeSlotSerializer(time_slots, many=True).data

class TimeSlotSerializer(serializers.ModelSerializer):    
    class Meta:
        model = TimeSlot
        fields = ['id','date','start_time','end_time']
        

class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only = True)
    time_slot = TimeSlotSerializer(read_only = True)
    patient = PatientSerializer(read_only = True)
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