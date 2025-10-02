from django import forms
from .models import BloodRequest, DonorLocation

<<<<<<< HEAD
# Blood Request Form
class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ["name", "email", "phone", "address", "blood_group", "emergency", "reason", "requester_lat", "requester_lng"]
=======
# ------------------------
# Blood Request Form
# ------------------------
class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            "name", "email", "phone", "address",
            "blood_group", "emergency", "reason",
            "requester_lat", "requester_lng"
        ]
>>>>>>> 6942391 (Initial commit: Updated project with new files and blood camp changes blood camp)
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "blood_group": forms.Select(attrs={"class": "form-select"}),
            "emergency": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
<<<<<<< HEAD
            "requester_lat": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "requester_lng": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
        }

# OTP Form
class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter OTP"})
    )

# Share Donor Location Form
=======
            # ✅ keep lat/lng but hide them (they will be updated by JS)
            "requester_lat": forms.HiddenInput(),
            "requester_lng": forms.HiddenInput(),
        }

# ------------------------
# OTP Form
# ------------------------
class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter OTP"
        })
    )

# ------------------------
# Share Donor Location Form
# ------------------------
>>>>>>> 6942391 (Initial commit: Updated project with new files and blood camp changes blood camp)
class ShareLocationForm(forms.ModelForm):
    class Meta:
        model = DonorLocation
        fields = ["lat", "lng"]
        widgets = {
<<<<<<< HEAD
            "lat": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "lng": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
=======
            "lat": forms.HiddenInput(),   # ✅ hide so JS can update
            "lng": forms.HiddenInput(),
>>>>>>> 6942391 (Initial commit: Updated project with new files and blood camp changes blood camp)
        }
