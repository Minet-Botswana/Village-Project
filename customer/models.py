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
    
class KYCForm(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='kyc_forms')
    submission_date = models.DateField(auto_now_add=True)
    file_upload = models.FileField(upload_to='Forms/KYC/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])])

    def get_download_url(self):
        if self.file_upload:
            return self.file_upload.url
        return None

    def __str__(self):
        return f"KYC Form - {self.customer.get_name}"

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

class HomeownersCover(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='homeowners_covers')
    submission_date = models.DateField(auto_now_add=True)
    file_upload = models.FileField(upload_to='Forms/HomeOwnersCover/', null=True, blank=True, )
    file_upload = models.FileField(upload_to='Forms/HomeOwnersCover/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])])

    def get_download_url(self):
        if self.file_upload:
            return self.file_upload.url
        return None

    def __str__(self):
        return f"Homeowners Cover - {self.customer.get_name}"

class ThirdPartyCarInsurance(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='car_insurance_covers')
    submission_date = models.DateField(auto_now_add=True)
    file_upload = models.FileField(upload_to='Forms/ThirdPartyCarInsurance/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf']) ])

    def get_download_url(self):
        if self.file_upload:
            return self.file_upload.url
        return None

    def __str__(self):
        return f"Third Party Car Insurance Cover - {self.customer.get_name}"

