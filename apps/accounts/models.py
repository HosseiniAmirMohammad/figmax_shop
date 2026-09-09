# apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator


class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        unique=True,  # ← شماره تلفن یکتا
        validators=[
            RegexValidator(
                regex=r'^09\d{9}$',
                message='شماره تلفن باید با 09 شروع شود و 11 رقم باشد',
                code='invalid_phone'
            )
        ]
    )
    avatar = models.CharField(
        max_length=100, 
        default='figmax-pfp1.png'
    )  # برای ذخیره نام فایل
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


# سیگنال برای ایجاد خودکار پروفایل
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()