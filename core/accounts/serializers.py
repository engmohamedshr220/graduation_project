import re
from rest_framework import serializers
from .models import City, User
from djoser.serializers import UserCreateSerializer
from djoser import utils


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email','name','role']
        
        

class MyUserCreateSerializer(UserCreateSerializer):
    location = serializers.CharField()
    class Meta:
        model = User
        fields = ['id', 'email', 'name','password','location','role']
        extra_kwargs = {
            'password':{'write_only':True},
            'name':{'required':True},
            'phone':{'required':True},
        }
    
    def validate_location(self, value):
        if not City.objects.filter(name=value).exists():
            raise serializers.ValidationError('location is not a valid choice')
        return City.objects.filter(name=value).first()
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