from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import transaction
from accounts.models import User
from clinic.models import Doctor, Patient

@receiver(post_save, sender=User)
@transaction.atomic
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Role.DOCTOR:
            # Create a Doctor profile
            Doctor.objects.create(user=instance)
        elif instance.role == User.Role.PATIENT:
            # Create a Patient profile
            Patient.objects.create(user=instance)
            


