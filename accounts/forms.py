from django import forms
from .models import ContactMessage
SUBJECT_CHOICES = [
    ('', 'Select a subject...'),
    ('general', 'General Inquiry'),
    ('donation', 'Blood Donation Drive'),
    ('support', 'Technical Support'),
]
class ContactMessageForm(forms.ModelForm):
    # If not defined in the model, override here:
    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    class Meta:
        model = ContactMessage
        fields = ["full_name", "email", "subject", "message"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter your full name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Enter your email address"}
            ),
            "message": forms.Textarea(
                attrs={"class": "form-control", "rows": 5, "placeholder": "How can we help you?"}
            ),
        }