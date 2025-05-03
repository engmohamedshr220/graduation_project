from django.dispatch import receiver
from django.db.models.signals import post_save
from accounts.models import User , PasswordResetToken
from clinic.models import Doctor
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

@receiver(post_save, sender=User)
def create_doctor_instance(sender, instance, created, **kwargs):

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