import email
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import transaction
from django.db.models import ProtectedError
from accounts.models import User , PasswordResetToken
from clinic.models import Doctor, Patient
from city.models import City
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

@receiver(post_save, sender=User)
@transaction.atomic
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Role.DOCTOR:
            try:
                # Ensure we have a city
                try:
                    if not instance.city_id:
                        city, _ = City.objects.get_or_create(name=City.CityChoices.NOT_SPECIFIED)
                        instance.city = city
                        instance.save(update_fields=['city'])
                    
                    # Validate city instance
                    if not isinstance(instance.city, City):
                        error_msg = 'Failed to create doctor profile: Invalid city instance'
                        print(error_msg)
                        raise ValueError(error_msg)
                    
                    # Ensure city exists in database
                    city = City.objects.get(id=instance.city.id)
                except City.DoesNotExist:
                    error_msg = 'Failed to create doctor profile: City does not exist in database'
                    print(error_msg)
                    raise
                except Exception as e:
                    error_msg = f'Failed to create doctor profile: Error validating city - {str(e)}'
                    print(error_msg)
                    raise
                
                # Create doctor with the validated city instance and proper time values
                from datetime import time
                doctor = Doctor.objects.create(
                    user=instance,
                    city=city,  # Use the validated city instance
                    start_hour=time(0, 0),  # Midnight
                    end_hour=time(0, 0)  # Midnight
                )
            except City.DoesNotExist:
                error_msg = 'Failed to create doctor profile: City does not exist'
                print(error_msg)
                raise Exception(error_msg)
            except ProtectedError as e:
                error_msg = f'Failed to create doctor profile: Protected error - {str(e)}'
                print(error_msg)
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f'Failed to create doctor profile: {str(e)}'
                print(error_msg)
                raise Exception(error_msg)
        elif instance.role == User.Role.PATIENT:
            try:
                patient = Patient.objects.create(user=instance)
            except ProtectedError as e:
                error_msg = f'Failed to create patient profile: Protected error - {str(e)}'
                print(error_msg)
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f'Failed to create patient profile: {str(e)}'
                print(error_msg)
                raise Exception(error_msg)
        if created:
            if instance.role == 'doctor':
                try:
                    html_content = render_to_string('emails/welcome_doctor.html', {
                        'name': instance.name,
                    })
                    # Fallback plain text version
                    text_content = f"Hello Dr/{instance.name}"
                    subject = "Welcome to Vital Breast Team"
                    from_email = settings.EMAIL_HOST_USER
                    to_email = [instance.email]
                    email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                    email_message.attach_alternative(html_content, "text/html")
                    email_message.send()
                except Exception as e:
                    print(f"Error sending email: {e}")
                    return
            