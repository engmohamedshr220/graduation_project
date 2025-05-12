import re
from rest_framework import serializers
from clinic.serializers import DoctorSerializer
from .models import City, User
from djoser.serializers import UserCreateSerializer
from djoser import utils


class MyUserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email','name','role','phone','city']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.role == 'doctor':
            representation['doctor'] = {
                "id": instance.doctor.id,
                "experience_years": instance.doctor.experience_years,
                'rating': instance.doctor.rating,
                'reviews_count': instance.doctor.reviews_count,
                'patient_count': instance.doctor.patient_count,
                'is_available': instance.doctor.is_available,
                'profile_img': instance.doctor.profile_img.url if instance.doctor.profile_img else None,
                'clinics': [
                    {
                        'id': clinic.id,
                        'city': clinic.city.name,
                        'contact_phone': clinic.contact_phone
                    } for clinic in instance.doctor.clinics.all()
                ],
                'start_hour': instance.doctor.start_hour,
                'end_hour': instance.doctor.end_hour,
                'city': instance.doctor.city.name if instance.doctor.city else None,
                
            }
        return representation


class MyUserCreateSerializer(UserCreateSerializer):
    id = serializers.UUIDField(read_only=True)
    phone = serializers.CharField()
    name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    city = serializers.CharField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name','password','phone','city','role']
        
    
    def validate_city(self, value):
        if not City.objects.filter(name=value).exists():
            raise serializers.ValidationError('This location is not available in our service areas')
        return City.objects.filter(name=value).first()

    def validate(self, attrs):
        # Check if email exists
        email = attrs.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'This email is already registered'
            })
        
        # Check if phone exists
        phone = attrs.get('phone')
        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({
                'phone': 'This phone number is already registered'
            })
        
        return super().validate(attrs)
    def validate_password(self ,value):
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        
        if not re.match(pattern, value):
            raise serializers.ValidationError('the password must contain at least one upper case and on special character')

        return value
    def to_representation(self, instance):
        represent =super().to_representation(instance)
        token = utils.login_user(self.context['request'] , instance)
        
        represent['auth_token'] = token.key
        return represent
    
    

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    code = serializers.CharField()
    email = serializers.EmailField()

class PasswordResetWithTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField()



class MessageResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    
class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()