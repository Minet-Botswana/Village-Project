from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class Customer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('S', 'Single'),
        ('M', 'Married'),
        ('D', 'Divorced'),
        ('W', 'Widowed'),
    ]
    
    ID_TYPE_CHOICES = [
        ('ID', 'ID'),
        ('Passport', 'Passport'),
    ]
    
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/Customer/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    
    # New fields
    id_type = models.CharField(max_length=10, choices=ID_TYPE_CHOICES, null=True, blank=True)
    id_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    postal_address = models.CharField(max_length=100, null=True, blank=True)
    physical_address = models.CharField(max_length=100, null=True, blank=True)
    occupation = models.CharField(max_length=50, null=True, blank=True)
    alternate_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # New fields for Gender, date of birth, and marital status
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name
    
class KYCform(models.Model):
    # Link to the authenticated customer
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='kyc_form', unique=True)
    # Attachments
    kyc_form = models.FileField(upload_to='Forms/KYC/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    submission_date = models.DateField(auto_now_add=True)

    def get_download_url(self):
        if self.kyc_form:
            return self.kyc_form.url
        return None

    def __str__(self):
        return f"KYC Form - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Error saving KYC Form instance: {e}")

class DirectDebitForm(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='direct_debit_forms')
    submission_date = models.DateField(auto_now_add=True)
    file_upload = models.FileField(upload_to='Forms/DirectDebit/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])])

    def get_download_url(self):
        if self.file_upload:
            return self.file_upload.url
        return None

    def __str__(self):
        return f"Direct Debit Form - {self.customer.get_name}"
    
    def save(self, *args, **kwargs):
        # Additional logic before saving, if needed
        super().save(*args, **kwargs)
        # Additional logic after saving, if needed

class HomeownersCover(models.Model):
    # Link to the authenticated customer
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='homeowners_cover')
    # Fields for Geo-location
    geo_location = models.CharField(max_length=255, blank=True, null=True)
    plot_number = models.CharField(max_length=50,null=True, blank=True)
    village = models.CharField(max_length=50, blank=True, null=True)
    ward = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    # Attachments
    title_deed = models.FileField(upload_to='Forms/HomeOwnersCover/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    # Financial Interest
    financial_interest = models.TextField(blank=True, null=True)
    # Submission Date
    submission_date = models.DateField(auto_now_add=True)

    def get_download_url(self):
        if self.title_deed:
            return self.title_deed.url
        return None

    def __str__(self):
        return f"Homeowners Cover - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Error saving HomeownersCover instance: {e}")

class ThirdPartyCarInsurance(models.Model):
    
    LOCAL = 'Local'
    IMPORT = 'Import'

    CAR_TYPE_CHOICES = [
        ('', 'Select car type'),
        (LOCAL, 'Local'),
        (IMPORT, 'Import'),
    ]
    
    # Link to the authenticated customer
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='thirdparty_car_cover', unique=True)
    make = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=50,null=True, blank=True)
    year_of_manufacture = models.CharField(max_length=50, blank=True, null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    registered_owner = models.CharField(max_length=50, blank=True, null=True)
    # Attachments
    blue_book = models.FileField(upload_to='Forms/ThirdPartyCarCover/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    car_type = models.CharField(max_length=10, choices=CAR_TYPE_CHOICES, default='')
    relationship_to_owner = models.TextField(blank=True, null=True)
    submission_date = models.DateField(auto_now_add=True)

    def get_download_url(self):
        if self.blue_book:
            return self.blue_book.url
        return None

    def __str__(self):
        return f"Third Party Car Cover - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Error saving Third Party Car Cover instance: {e}")