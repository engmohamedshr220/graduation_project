from django.conf import settings
from django.shortcuts import render
import re
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import PasswordResetCode, PasswordResetToken, User
from rest_framework.views import APIView
import random
from rest_framework.permissions import AllowAny
from .serializers import (ErrorResponseSerializer, MessageResponseSerializer,
    PasswordResetConfirmSerializer, PasswordResetWithTokenSerializer, ResetPasswordEmailSerializer)
from drf_spectacular.utils import extend_schema ,OpenApiResponse , OpenApiExample


class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=ResetPasswordEmailSerializer,
        responses={
            200: OpenApiResponse(
                response=MessageResponseSerializer,
                description="Success",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"detail": "Password reset code sent"},
                        status_codes=["200"]
                    ),
                ]
                ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description= "error",
                examples=[
                    OpenApiExample(
                        "User not found",
                        value={"error": "User with this email does not exist"},
                        status_codes=["400"]
                    ),
                    OpenApiExample(
                        "Invalid email",
                        value={"error": "Invalid email format"},
                        status_codes=["400"]
                    ),
                    OpenApiExample(
                        "Email sending error",
                        value={"error": "Can't send email, Try again Later"},
                        status_codes=["400"]
                    )
                ]
            )
            
            
        }
    )
    
    
    def post(self, request):
        serializer = ResetPasswordEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            code = random.randint(1000, 9999)

            # Delete any existing codes
            user.password_reset_codes.all().delete()

            PasswordResetCode.objects.create(user=user, code=str(code))

            # Render HTML email content
            try:
                html_content = render_to_string('emails/password_reset.html', {
                    'user': user,
                    'code': code,
                'name': user.name})

                # Fallback plain text version
                text_content = f"Hello,\n\nYour password reset code is: {code}\n\nThanks,\nThe Vital Breast Team"

                subject = "Password Reset Code"
                from_email = settings.EMAIL_HOST_USER
                to_email = [user.email]

                email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                email_message.attach_alternative(html_content, "text/html")
                email_message.send()
            except Exception as e:
                return Response({'error': f"Can't send email {e }"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': "Can't generate code for this user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'Password reset code sent'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    
    @extend_schema(
        request= PasswordResetConfirmSerializer,
        responses={
            200: OpenApiResponse(
                response=MessageResponseSerializer,
                description="Success",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"detail": "Code is valid"},
                        status_codes=["200"]
                    )
                ]
            ),
            400:OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "Invalid code",
                        value={"error": "Invalid code"},
                        status_codes=["400"]
                    ),
                    OpenApiExample(
                        "Code is expired",
                        value={"error": "Code is expired"},
                        status_codes=["400"]
                    ),
                   
                ]
            )
        }
    )
    
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reset_code = user.password_reset_codes.get(code=code)
        except PasswordResetCode.DoesNotExist:
            return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

        if reset_code.is_expired():
            reset_code.delete()
            return Response({'error': 'Code is expired'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete any old tokens
        user.password_reset_tokens.all().delete()

        # Create a new token
        token_obj = PasswordResetToken.objects.create(user=user)

        return Response({
            'detail': 'Code is valid',
            'reset_password_token': token_obj.token
        }, status=status.HTTP_200_OK)
    


class PasswordResetWithTokenView(APIView):
    
    @extend_schema(
        request= PasswordResetWithTokenSerializer,
        responses={
            200: OpenApiResponse(
                response=MessageResponseSerializer,
                description="Success",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={"detail": "Password was set successfuly"},
                        status_codes=["200"]
                    )
                ]
            ),
            400:OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "Invalid Token",
                        value={"error": "Invalid Token"},
                        status_codes=["400"]
                    ),
                    OpenApiExample(
                        "Code is expired",
                        value={"error": "Token is expired"},
                        status_codes=["400"]
                    ),
                   
                ]
            )
        }
    )
    
    
    def post(self, request):
        serializer = PasswordResetWithTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['password']

        try:
            user_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        if user_token.is_expired():
            user_token.delete()
            PasswordResetCode.objects.filter(user=user_token.user).delete()
            return Response({'error': 'Token is expired'}, status=status.HTTP_400_BAD_REQUEST)

        user = user_token.user
        user.set_password(new_password)
        user.save()

        # Cleanup token after use
        user_token.delete()
        PasswordResetCode.objects.filter(user=user).delete()

        return Response({'detail': 'Password reset successful'}, status=status.HTTP_200_OK)
    


