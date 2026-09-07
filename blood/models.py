from django.db import models
from django.contrib.auth.models import User
from donor.models import Donor
class BloodInventory(models.Model):
    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES,
        unique=True
    )
    units_available = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.blood_group} ({self.units_available} Units)"
class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Fulfilled", "Fulfilled"),
    ]
    BLOOD_GROUP_CHOICES = BloodInventory.BLOOD_GROUP_CHOICES
    URGENCY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Critical", "Critical"),
    ]
    REQUEST_FOR_CHOICES = [
    ("self", "Myself"),
    ("other", "Someone Else"),
]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)
    request_for = models.CharField(
    max_length=10,
    choices=REQUEST_FOR_CHOICES,
    default="self"
)
    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES
    )
    units_required = models.PositiveIntegerField()
    hospital_name = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    reason = models.TextField()
    urgency = models.CharField(
        max_length=10,
        choices=URGENCY_CHOICES,
        default="Medium"
    )
    required_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    requested_on = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return f"{self.patient_name} - {self.blood_group}"
class Donation(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Completed", "Completed"),
    ]

    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,
        related_name="donations"
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BloodInventory.BLOOD_GROUP_CHOICES
    )

    units_donated = models.PositiveIntegerField(
        default=1
    )

    donation_date = models.DateField()

    hospital_name = models.CharField(
        max_length=150
    )

    city = models.CharField(
        max_length=100
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    notes = models.TextField(
        blank=True
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.donor.user.username} - {self.blood_group} - {self.units_donated} Unit(s)"