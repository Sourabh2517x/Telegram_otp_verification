from django import forms
from .models import User
import re

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username","phoneno"]
        
    def clean_phoneno(self):
        phone = self.cleaned_data["phoneno"]

        # Remove spaces (basic normalization)
        phone = phone.strip()

        # Validate: exactly 10 digits
        if not re.fullmatch(r"\d{10}", phone):
            raise forms.ValidationError("Enter a valid 10-digit phone number")

        return phone


class LoginForm(forms.Form):
    phoneno = forms.CharField(max_length=10)

    def clean_phoneno(self):
        phone = self.cleaned_data["phoneno"]

        # Remove spaces (basic normalization)
        phone = phone.strip()

        # Validate: exactly 10 digits
        if not re.fullmatch(r"\d{10}", phone):
            raise forms.ValidationError("Enter a valid 10-digit phone number")

        return phone
    
    
class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        required=True,
    )
    def clean_otp(self):
        otp = self.cleaned_data["otp"]

        # Remove spaces (basic normalization)
        otp = otp.strip()

        # Validate: exactly 6 digits
        if not re.fullmatch(r"\d{6}", otp):
            raise forms.ValidationError("Enter a valid 6-digit OTP")

        return otp
