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

    class Meta:
        model = models.Policy
        fields = ['category', 'policy_name', 'sum_assurance', 'premium', 'tenure', 'id_number', 'cover_start', 'policy_number', 'expiry_date']
        
class ThirdpartyPolicyForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(), empty_label="Cover Category", to_field_name="id")
    id_number = forms.CharField(label='ID Number', max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID Number'}))
    cover_start = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))  # New field for cover start date
    tenure = forms.IntegerField()  # New field for tenure

    class Meta:
        model = models.ThirdpartyPolicy
        fields = ['category', 'policy_name', 'premium', 'tenure', 'id_number', 'cover_start', 'policy_number', 'expiry_date']

class QuestionForm(forms.ModelForm):
    class Meta:
        model=models.Question
        fields=['description']
        widgets = {
        'description': forms.Textarea(attrs={'rows': 6, 'cols': 30})
        }