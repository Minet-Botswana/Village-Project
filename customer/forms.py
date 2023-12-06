from django import forms
from django.contrib.auth.models import User
from .models import Customer, KYCForm, DirectDebitForm, HomeownersCover, ThirdPartyCarInsurance

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

class KYCFormModelForm(forms.ModelForm):
    class Meta:
        model = KYCForm
        fields = ['file_upload']
        # Set 'file_upload' as required
        widgets = {
            'file_upload': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'file_upload': {
                'required': 'This field is required.',
            }
        }

class DirectDebitFormModelForm(forms.ModelForm):
    class Meta:
        model = DirectDebitForm
        fields = ['file_upload']
        # Set 'file_upload' as required
        widgets = {
            'file_upload': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'file_upload': {
                'required': 'This field is required.',
            }
        }

class HomeownersCoverForm(forms.ModelForm):
    class Meta:
        model = HomeownersCover
        fields = ['geo_location', 'plot_number', 'ward', 'village', 'district', 'title_deed', 'financial_interest']

    def clean_title_deed(self):
        title_deed = self.cleaned_data.get('title_deed')
        if title_deed:
            # Validate the file extension or any other criteria if needed
            ext = title_deed.name.split('.')[-1].lower()
            if ext not in ['pdf']:
                raise forms.ValidationError('Only PDF files are allowed.')
        return title_deed

class ThirdPartyCarInsuranceModelForm(forms.ModelForm):
    class Meta:
        model = ThirdPartyCarInsurance
        fields = ['file_upload']
        # Set 'file_upload' as required
        widgets = {
            'file_upload': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'file_upload': {
                'required': 'This field is required.',
            }
        }