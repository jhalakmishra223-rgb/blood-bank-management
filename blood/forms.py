from django import forms
from .models import BloodRequest
from .models import Donation

class BloodRequestForm(forms.ModelForm):

    class Meta:
        model = BloodRequest

        exclude = [
            'user',
            'status',
            'request_for',
            'requested_on',
        ]

        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Patient Name'
            }),

            'blood_group': forms.Select(attrs={
                'class': 'form-select'
            }),

            'units_required': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),

            'hospital_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hospital Name'
            }),

            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),

            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),

            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Reason for blood request'
            }),

            'urgency': forms.Select(attrs={
                'class': 'form-select'
            }),

            'required_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
class DonationForm(forms.ModelForm):

    class Meta:
        model = Donation

        fields = [
            "blood_group",
            "units_donated",
            "donation_date",
            "hospital_name",
            "city",
            "notes",
        ]

        widgets = {
            "blood_group": forms.Select(
                attrs={
                    "class": "form-select border-start-0"
                }
            ),

            "units_donated": forms.NumberInput(
                attrs={
                    "class": "form-control border-start-0",
                    "min": 1,
                    "placeholder": "Enter units"
                }
            ),

            "donation_date": forms.DateInput(
                attrs={
                    "class": "form-control border-start-0",
                    "type": "date"
                }
            ),

            "hospital_name": forms.TextInput(
                attrs={
                    "class": "form-control border-start-0",
                    "placeholder": "Enter hospital or donation center"
                }
            ),

            "city": forms.TextInput(
                attrs={
                    "class": "form-control border-start-0",
                    "placeholder": "Enter city"
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Add any additional information if required..."
                }
            ),
        }