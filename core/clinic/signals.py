from django.dispatch import receiver
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse

from .models import DoctorUpdateToken , Doctor

@receiver(post_save, sender=Doctor)
def create_doctor_update_token(sender, instance, created, **kwargs):
    if created:
        # Generate a unique token for the doctor
        token= DoctorUpdateToken.objects.create(doctor=instance)
        
        try:
            # Generate the URL for updating the doctor token
            update_token_url = reverse('doctor-update-token', kwargs={'token': token.token})
            full_url = f"{settings.FRONTEND_BASE_URL}{update_token_url}"
            html_content = render_to_string('emails/welcome_doctor.html', {
                'name': instance.user.name,
                'update_url': full_url,
            })
            # Fallback plain text version
            text_content = f"Hello Dr/{instance.user.name},\nUpdate your profile here: {full_url}"
            subject = "Welcome to Vital Breast Team"
            from_email = settings.EMAIL_HOST_USER
            to_email = [instance.user.email]
            email_message = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()
        except Exception as e:
            print(f"Error sending email: {e}")
                    
        