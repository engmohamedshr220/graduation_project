from django.shortcuts import render
import re
from  rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from accounts.permissions import IsAdminUser
from clinic.filters import DoctorFilter
from .models import Appointment, Doctor, Reviews
from .serializers import (AppointmentCreateSerializer, AppointmentSerializer, DoctorSerializer,
    ReviewsSerializer)
from drf_spectacular.utils import extend_schema,OpenApiExample
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

class DoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.all()
    
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend , SearchFilter]
    filterset_class = DoctorFilter
    
    
    def get_serializer_class(self):
        if self.action in ['book_slot']:
            return  AppointmentCreateSerializer
        elif self.action == 'add_review':
            return ReviewsSerializer
        elif self.action == 'get_appointments':
            return AppointmentSerializer
        elif self.action == 'get_reviews':
            return ReviewsSerializer
        else:
            return DoctorSerializer
        
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif self.action == 'add_review':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    

    @extend_schema(
        request=AppointmentCreateSerializer,
        responses={
            201:AppointmentCreateSerializer,},
        
        examples=[
            OpenApiExample(
                'User Must be logged in',
                value={
                    'time_slot':'time_slot_id',
                    
                },
                request_only=True,
            ),
            OpenApiExample(
                'Annonymous User',
                value={
                    'time_slot':'time_slot_id',
                    'name':'John Doe',
                    'age': 30,
                    'phone': '+1234567890',
                    'city': 'New York',
                },
                request_only=True,
                response_only=False,
            )
        ]
    )
    @action(detail=True, methods=['post'],url_path = 'book_slot',url_name = 'book_slot')
    def book_slot(self,request , pk=None):
        doctor =  self.get_object()
        serializer= self.get_serializer(data=request.data, context = {'request': request, 'doctor': doctor})
        serializer.is_valid(raise_exception=True)
        Appointment.objects.create(
            doctor = doctor,
            patient = request.user.patient,
            time_slot = request.data.get('time_slot'),
            status = 'booked'
        )
        return Response({'detail': 'Slot booked successfully'}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'],url_path = 'appointments',url_name = 'appointments')
    def get_appointments(self, request, pk=None):
        doctor = self.get_object()
        appointments = Appointment.objects.filter(doctor=doctor)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'],url_path = 'reviews',url_name = 'reviews')
    def get_reviews(self, request, pk=None):
        doctor = self.get_object()
        reviews = doctor.reviews.all()
        serializer = ReviewsSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'],url_path = 'add-review',url_name = 'make_review')
    def add_review(self, request, pk=None):
        doctor = self.get_object()
        review = request.data.get('review')
        patient = request.user.patient
        if not review:
            return Response({'detail': 'Review is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        Reviews.objects.create(
            doctor=doctor,
            patient=patient,
            review=review
        )
        doctor.reviews_count += 1
        return Response({'detail': 'Review added successfully'}, status=status.HTTP_201_CREATED)