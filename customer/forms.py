from django import forms
from django.contrib.auth.models import User
from .models import Customer, KYCform, DirectDebitForm, HomeownersCover, ThirdPartyCarInsurance

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
        fields = ['address', 'mobile', 'id_type', 'id_number', 'postal_address', 'physical_address', 'occupation', 'alternate_phone', 'gender', 'date_of_birth', 'marital_status']

class KYCuploadForm(forms.ModelForm):
    class Meta:
        model = KYCform
        fields = ['kyc_form']

    def clean_kyc_form(self):
        kyc_form = self.cleaned_data.get('kyc_form')
        if kyc_form:
            # Validate the file extension or any other criteria if needed
            ext = kyc_form.name.split('.')[-1].lower()
            if ext != 'pdf':
                raise forms.ValidationError('Only PDF files are allowed.')
        return kyc_form



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
            if ext != 'pdf':
                raise forms.ValidationError('Only PDF files are allowed.')
        return title_deed


class ThirdPartyCarInsuranceForm(forms.ModelForm):
    
    LOCAL = 'Local'
    IMPORT = 'Import'

    CAR_TYPE_CHOICES = [
        ('', 'Select car type'),
        (LOCAL, 'Local'),
        (IMPORT, 'Import'),
    ]
    
    car_type = forms.ChoiceField(choices=CAR_TYPE_CHOICES, required=True, initial='', widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ThirdPartyCarInsurance
        fields = ['make', 'model', 'year_of_manufacture', 'registration_number', 'registered_owner', 'blue_book', 'car_type', 'relationship_to_owner']

    def clean_blue_book(self):
        blue_book = self.cleaned_data.get('blue_book')
        if blue_book:
            # Validate the file extension or any other criteria if needed
            ext = blue_book.name.split('.')[-1].lower()
            if ext != 'pdf':
                raise forms.ValidationError('Only PDF files are allowed.')
        return blue_book