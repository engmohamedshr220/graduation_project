from django.shortcuts import render
import uuid
from  rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponseNotAllowed
from  rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from accounts.permissions import IsAdminUser
from clinic.filters import DoctorFilter
from accounts.permissions import IsAdminOrDoctorUser
from .models import Appointment, Doctor, Reviews
from .serializers import (AppointmentCreateSerializer, AppointmentUpdateSerializer,AppointmentSerializer, DoctorSerializer,
    ReviewsSerializer,DoctorUpdateSerializer)
from drf_spectacular.utils import extend_schema,OpenApiExample
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import status 
class DoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.all()
    
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend , SearchFilter]
    filterset_class = DoctorFilter
    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
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
            self.permission_classes = [IsAdminOrDoctorUser]
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
    

class DoctorUpdateTokenApi(APIView):
    @extend_schema(
        request=DoctorUpdateSerializer,
        responses={200: DoctorUpdateSerializer},
        description="Update doctor profile using a token."
    )
    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        serializer = DoctorUpdateSerializer(token = token ,data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.save()
        return Response(serializer.data , status=status.HTTP_200_OK)



from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # Explicitly set to 'id' which will now be UUID
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminOrDoctorUser]
        return super().get_permissions()

    @extend_schema(
        description="List all appointments for the authenticated user (doctor or patient)",
        responses={200: AppointmentSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Example response',
                value=[
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",  # Example UUID
                        "doctor": {"id": "..."},
                        "patient": {"id": "..."},
                        "date": "2023-05-15",
                        "time": "14:30:00",
                        "status": "confirmed"
                    }
                ],
                response_only=True,
                status_codes=['200']
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='user-appointments', url_name='user-appointments')
    def get_appointments(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.role == 'doctor':
            appointments = Appointment.objects.filter(doctor=user.doctor)        
        elif user.role == 'patient':
            appointments = Appointment.objects.filter(patient=user.patient)
        else:
            return Response({'detail': 'Invalid user role'}, status=status.HTTP_403_FORBIDDEN)
            
        if not appointments.exists():
            return Response({'detail': 'No appointments found'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Retrieve or update a specific appointment",
        methods=['GET'],
        responses={200: AppointmentSerializer},
        parameters=[
            OpenApiParameter(
                name='appointment_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the appointment'
            )
        ]
    )
    @extend_schema(
        description="Update a specific appointment",
        methods=['PATCH'],
        request=AppointmentUpdateSerializer,
        responses={200: AppointmentSerializer},
        parameters=[
            OpenApiParameter(
                name='appointment_id',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description='UUID of the appointment'
            )
        ],
        examples=[
            OpenApiExample(
                'Example request',
                value={
                    "status": "cancelled"
                },
                request_only=True,
                status_codes=['200']
            )
        ]
    )
    @action(detail=False, methods=['get', 'patch'], url_path='user-appointments/(?P<appointment_id>[0-9a-f-]{36})', url_name='single-appointment')
    def single_appointment(self, request, appointment_id=None, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            appointment_uuid = uuid.UUID(appointment_id)
        except ValueError:
            return Response(
                {'detail': 'Invalid UUID format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if user.role == 'doctor':
                appointment = Appointment.objects.get(id=appointment_uuid, doctor=user.doctor)
            elif user.role == 'patient':
                appointment = Appointment.objects.get(id=appointment_uuid, patient=user.patient)
            else:
                return Response({'detail': 'Invalid user role'}, status=status.HTTP_403_FORBIDDEN)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            serializer = AppointmentUpdateSerializer(
                appointment, 
                data=request.data, 
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        