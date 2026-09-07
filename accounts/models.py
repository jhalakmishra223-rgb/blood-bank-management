from django.db import models
from django.contrib.auth.models import User
class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ("general", "General Inquiry"),
        ("donation", "Blood Donation Query"),
        ("camp", "Organize a Blood Drive"),
        ("support", "Technical Support"),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(
        max_length=30,
        choices=SUBJECT_CHOICES
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.full_name} - {self.get_subject_display()}"