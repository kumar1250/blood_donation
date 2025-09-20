
# blood_requests/forms.py
from django import forms
from .models import BloodRequest



class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            "name",
            "email",
            "phone",
            "address",
            "blood_group",
            "emergency",
            "reason",
        ]

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, label="Enter OTP")
