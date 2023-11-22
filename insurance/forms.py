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
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(), empty_label="long term cover, short term cover etc.", to_field_name="id")
    id_number = forms.CharField(label='ID Number', max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID Number'}))

    class Meta:
        model = models.Policy
        fields = ['category', 'policy_name', 'sum_assurance', 'premium', 'tenure', 'id_number']

class QuestionForm(forms.ModelForm):
    class Meta:
        model=models.Question
        fields=['description']
        widgets = {
        'description': forms.Textarea(attrs={'rows': 6, 'cols': 30})
        }