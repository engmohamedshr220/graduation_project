from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from clinic.models import Doctor, Clinic, Appointment, Patient, TimeSlot, Reviews
from city.models import City
from datetime import datetime, timedelta, time
import random
from faker import Faker
import uuid

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Generate comprehensive dummy data for the clinic application'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating comprehensive dummy data...')

        # Clear existing data (optional - be careful with this in production)
        self.stdout.write('Deleting old data...')
        Appointment.objects.all().delete()
        Reviews.objects.all().delete()
        TimeSlot.objects.all().delete()
        Clinic.objects.all().delete()
        Patient.objects.all().delete()
        Doctor.objects.all().delete()
        User.objects.filter(role__in=['doctor', 'patient']).delete()

        # Create cities
        city_choices = [
            'Cairo', 'Alexandria', 'Giza', 'Sharm El Sheikh', 'Hurghada',
            'Luxor', 'Aswan', 'Port Said', 'Suez', 'Ismailia'
        ]
        
        city_objects = []
        for name in city_choices:
            city, created = City.objects.get_or_create(name=name)
            city_objects.append(city)
            if created:
                self.stdout.write(f'Created city: {name}')

        # Create doctors and their users
        doctor_objs = []
        for i in range(20):  # Create 20 doctors
            first_name = fake.first_name_male() if i % 2 else fake.first_name_female()
            last_name = fake.last_name()
            email = f'dr.{first_name.lower()}.{last_name.lower()}{i}@example.com'
            
            user = User.objects.create_user(
                email=email,
                password='doctorpass123',
                name=f'Dr. {first_name} {last_name}',
                phone=f'01{random.randint(2,5)}{random.randint(10000000, 99999999)}',
                role='doctor',
                username=f'dr_{first_name.lower()}_{last_name.lower()}_{i}',
                city=random.choice(city_objects),
                gender='male' if i % 2 else 'female'
            )
            
            # Get the doctor instance created by the signal
            doctor = Doctor.objects.get(user=user)
            
            # Update the doctor fields
            doctor.start_hour = time(random.randint(8, 10))  # Between 8-10 AM
            doctor.end_hour = time(random.randint(15, 19))   # Between 3-7 PM
            doctor.experience_years = random.randint(1, 30)
            doctor.reviews_count = 0
            doctor.rating = 0
            doctor.patient_count = random.randint(50, 500)
            doctor.is_available = random.choice([True, False])
            doctor.is_active = True
            doctor.save()
            
            doctor_objs.append(doctor)
            
            # Create 1-3 clinics for each doctor
            for _ in range(random.randint(1, 3)):
                Clinic.objects.create(
                    doctor=doctor,
                    city=random.choice(city_objects),
                    contact_phone=f'01{random.randint(2,5)}{random.randint(10000000, 99999999)}'
                )

        # Create patient users - the signal will create Patient instances
        patient_users = []
        for i in range(50):  # Create 50 patients
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f'patient.{first_name.lower()}.{last_name.lower()}{i}@example.com'
            
            user = User.objects.create_user(
                email=email,
                password='patientpass123',
                name=f'{first_name} {last_name}',
                phone=f'01{random.randint(0,2)}{random.randint(10000000, 99999999)}',
                role='patient',
                username=f'patient_{first_name.lower()}_{last_name.lower()}_{i}',
                city=random.choice(city_objects),
                gender=random.choice(['male', 'female'])
            )
            patient_users.append(user)

        # Get all patient instances created by the signal
        patient_objs = list(Patient.objects.filter(user__in=patient_users))
        
        # Update patient ages
        for patient in patient_objs:
            patient.age = random.randint(18, 80)
            patient.save()

        # Create time slots for the next 30 days
        # DEBUGGING: Print list of timeslots created
        self.stdout.write("Creating time slots...")
        timeslots = []
        today = datetime.now().date()
        
        # Create slots with more variation to avoid conflicts
        for day in range(30):  # For the next 30 days
            slot_date = today + timedelta(days=day)
            # Create multiple slots per day
            for hour in range(8, 17, 2):  # 8am, 10am, 12pm, 2pm, 4pm
                start_time = time(hour, 0)
                end_time = time(hour + 1, 0)
                
                # Create the time slot
                slot = TimeSlot.objects.create(
                    date=slot_date,
                    start_time=start_time,
                    end_time=end_time
                )
                timeslots.append(slot)
                self.stdout.write(f"  Created slot: {slot_date} {start_time}-{end_time}")
        
        self.stdout.write(f"Created {len(timeslots)} time slots")

        # Create reviews for doctors
        for doctor in doctor_objs:
            num_reviews = random.randint(5, 15)
            
            for _ in range(num_reviews):
                patient = random.choice(patient_objs)
                
                Reviews.objects.create(
                    doctor=doctor,
                    patient=patient,
                    review=fake.paragraph(nb_sentences=3),
                    created_at=fake.date_time_between(start_date='-1y', end_date='now')
                )
            
            # Update doctor's review count and calculate average rating
            reviews = Reviews.objects.filter(doctor=doctor)
            doctor.reviews_count = reviews.count()
            doctor.rating = round(random.uniform(3.0, 5.0), 1)  # Random rating between 3.0-5.0
            doctor.save()

        # DEBUGGING: Create appointments with more detailed error reporting
        self.stdout.write("Creating appointments...")
        status_choices = ['pending', 'confirmed', 'completed', 'cancelled']
        appointment_count = 0
        
        # Track used doctor-timeslot and patient-timeslot combinations
        used_doctor_slots = set()
        used_patient_slots = set()
        
        # Guest appointments - simpler validation
        for _ in range(30):  # Try to create 30 guest appointments
            doctor = random.choice(doctor_objs)
            slot = random.choice(timeslots)
            
            # Check if this doctor already has this slot booked
            doctor_slot_key = f"{doctor.id}_{slot.id}"
            if doctor_slot_key in used_doctor_slots:
                continue
            
            try:
                # For guest appointments, we need ALL guest fields
                appt = Appointment(
                    doctor=doctor,
                    time_slot=slot,
                    status=random.choice(status_choices),
                    name=fake.name(),
                    phone=f'01{random.randint(0,2)}{random.randint(10000000, 99999999)}',
                    age=random.randint(18, 80),
                    city=random.choice([c.name for c in city_objects]),
                    desc=fake.sentence()
                )
                # Call full_clean to trigger validation before saving
                appt.full_clean()
                appt.save()
                
                used_doctor_slots.add(doctor_slot_key)
                appointment_count += 1
                self.stdout.write(f"  Created guest appointment: #{appointment_count}")
            except Exception as e:
                self.stdout.write(f"  Error creating guest appointment: {e}")
        
        # Regular patient appointments
        for _ in range(70):  # Try to create 70 patient appointments
            doctor = random.choice(doctor_objs)
            patient = random.choice(patient_objs)
            slot = random.choice(timeslots)
            
            # Check constraints
            doctor_slot_key = f"{doctor.id}_{slot.id}"
            patient_slot_key = f"{patient.id}_{slot.id}"
            
            if doctor_slot_key in used_doctor_slots or patient_slot_key in used_patient_slots:
                continue
            
            try:
                # For patient appointments, we should NOT provide guest fields
                appt = Appointment(
                    doctor=doctor,
                    patient=patient,
                    time_slot=slot,
                    status=random.choice(status_choices),
                    desc=fake.sentence()
                )
                # Call full_clean to trigger validation before saving
                appt.full_clean()
                appt.save()
                
                used_doctor_slots.add(doctor_slot_key)
                used_patient_slots.add(patient_slot_key)
                appointment_count += 1
                self.stdout.write(f"  Created patient appointment: #{appointment_count}")
            except Exception as e:
                self.stdout.write(f"  Error creating patient appointment: {e}")

        # Create admin user
        if not User.objects.filter(email='admin@clinic.com').exists():
            User.objects.create_superuser(
                email='admin@clinic.com',
                password='adminpass123',
                name='Admin User',
                phone='01000000000',
                username='admin',
                city=random.choice(city_objects),
                role='admin'
            )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created dummy data:\n'
            f'- {len(city_objects)} cities\n'
            f'- {len(doctor_objs)} doctors with {Clinic.objects.count()} clinics\n'
            f'- {len(patient_objs)} patients\n'
            f'- {TimeSlot.objects.count()} time slots\n'
            f'- {Reviews.objects.count()} reviews\n'
            f'- {appointment_count} appointments\n'
            f'- 1 admin user'
        ))