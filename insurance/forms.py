from django import forms
from django.contrib.auth.models import User
from . import models

class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))


class CategoryForm(forms.ModelForm):
    class Meta:
        model=models.Category
        fields=['category_name']

class PolicyForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(), empty_label="Cover Category", to_field_name="id")
    id_number = forms.CharField(label='ID Number', max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID Number'}))
    cover_start = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))  # New field for cover start date
    tenure = forms.IntegerField()  # New field for tenure

    # Homeowners Policy Fields
    plot_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Plot 12345'}),
        label='Plot Number',
        help_text='The official plot number of the property'
    )
    
    ward_kgotla = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Ward 10 or Kgotla Name'}),
        label='Ward/Kgotla',
        help_text='The ward number or traditional authority (Kgotla) area'
    )
    
    village = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Gaborone Village'}),
        label='Village',
        help_text='The village or township name'
    )
    
    district = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., South East District'}),
        label='District',
        help_text='The administrative district'
    )
    
    title_deed = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        label='Title Deed (Optional)',
        help_text='Upload the property title deed (PDF format only)'
    )
    
    financial_interest = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g., Mortgaged to ABC Bank, Jointly owned with spouse, etc.'}),
        label='Financial Interest (Optional)',
        help_text='Describe any financial interests, mortgages, or co-ownership details'
    )

    class Meta:
        model = models.Policy
        fields = ['category', 'policy_name', 'sum_assurance', 'premium', 'tenure', 'id_number', 'cover_start', 
                 'plot_number', 'ward_kgotla', 'village', 'district', 'title_deed', 'financial_interest']
        
class ThirdpartyPolicyForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(), empty_label="Cover Category", to_field_name="id")
    id_number = forms.CharField(label='ID Number', max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID Number'}))
    cover_start = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))  # New field for cover start date
    tenure = forms.IntegerField()  # New field for tenure
    
    # Vehicle Details Fields
    vehicle_type = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Sedan, Hatchback, SUV, Truck'}),
        help_text="Type of vehicle"
    )
    vehicle_make = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toyota, BMW, Ford'}),
        help_text="Vehicle manufacturer"
    )
    vehicle_model = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Camry, X5, Focus'}),
        help_text="Vehicle model"
    )
    vehicle_year = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2020', 'min': '1900', 'max': '2030'}),
        help_text="Year of manufacture"
    )
    chassis_number = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vehicle Identification Number (VIN)'}),
        help_text="Vehicle chassis/VIN number"
    )
    registration_number = forms.CharField(
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ABC123GP'}),
        help_text="Vehicle registration number"
    )
    engine_number = forms.CharField(
        max_length=50, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Engine serial number'}),
        help_text="Engine serial number"
    )
    territorial_limits = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g., Republic of Botswana and neighboring SADC countries'}),
        help_text="Geographic coverage limits where the policy is valid"
    )

    class Meta:
        model = models.ThirdpartyPolicy
        fields = [
            'category', 'policy_name', 'premium', 'tenure', 'id_number', 'cover_start', 
            'vehicle_type', 'vehicle_make', 'vehicle_model', 'vehicle_year', 
            'chassis_number', 'registration_number', 'engine_number', 'territorial_limits'
        ]

class QuestionForm(forms.ModelForm):
    class Meta:
        model=models.Question
        fields=['description']
        widgets = {
        'description': forms.Textarea(attrs={'rows': 6, 'cols': 30})
        }