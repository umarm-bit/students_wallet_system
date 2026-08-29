from django import forms
from .models import Student


class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Create password"
        })
    )

    class Meta:
        model = Student
        fields = [
            "reg_no",
            "full_name",
            "email",
            "phone",
            "department",
            "programme",
            "level",
            "password",
        ]

        widgets = {
            "reg_no": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Registration Number"
            }),
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Full Name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Email"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Phone Number"
            }),
            "department": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Department"
            }),
            "programme": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Programme"
            }),
            "level": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. ND I"
            }),
        }