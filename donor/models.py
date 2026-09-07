from django.db import models
from django.contrib.auth.models import User
class Donor(models.Model):
    BLOOD_GROUPS = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]
    user = models.OneToOneField(
    User,
        on_delete=models.CASCADE
    )
    age = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUPS,
        blank=True
    )
    phone = models.CharField(
        max_length=15,
        blank=True
    )
    address = models.TextField(blank=True)
    city = models.CharField(
        max_length=100,
        blank=True
    )
    state = models.CharField(
        max_length=100,
        blank=True
    )
    profile_picture = models.ImageField(
    upload_to="profile_photos/",
    blank=True,
    null=True
)
    def __str__(self):
        return self.user.username