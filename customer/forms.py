from django import forms
from django.contrib.auth.models import User
from .models import Customer

class CustomerUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

class CustomerForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('', 'Select Gender'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('', 'Select Marital Status'),
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
    ]
    
    ID_TYPE_CHOICES = [
        ('', 'Select ID Type'),
        ('ID', 'ID'),
        ('Passport', 'Passport'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True, initial='', widget=forms.Select(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=True)
    marital_status = forms.ChoiceField(choices=MARITAL_STATUS_CHOICES, required=True, initial='', widget=forms.Select(attrs={'class': 'form-control'}))
    id_type = forms.ChoiceField(choices=ID_TYPE_CHOICES, required=True, initial='', widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Customer
        fields = ['address', 'mobile', 'profile_pic', 'id_type', 'id_number', 'postal_address', 'physical_address', 'occupation', 'alternate_phone', 'gender', 'date_of_birth', 'marital_status']
