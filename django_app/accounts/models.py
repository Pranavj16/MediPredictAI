from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('chw', 'Community Health Worker'),
        ('clinician', 'Clinician / Reviewer'),
        ('admin', 'Administrator'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'हिंदी (Hindi)'),
        ('mr', 'मराठी (Marathi)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        blank=True,
        null=True
    )
    assigned_center = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Assigned Primary Health Centre, Sub-Centre, or Hospital"
    )
    preferred_language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='en'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
