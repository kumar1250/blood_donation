from django import forms
from .models import BloodCamp

class BloodCampForm(forms.ModelForm):
    class Meta:
        model = BloodCamp
        fields = [
            "name", "organized_by", "date", "time", "venue", "city",
            "latitude", "longitude",
            "contact_person", "contact_phone",
            "min_age", "max_age", "min_weight", "notes", "permanent"
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TextInput(attrs={"placeholder": "10:00 AM - 4:00 PM", "class": "form-control"}),
            "venue": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter city"}),
            "latitude": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Latitude"}),
            "longitude": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Longitude"}),
            "permanent": forms.CheckboxInput(attrs={"class": "form-check-input"}),  # ✅ Nice checkbox
        }

