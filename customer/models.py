from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

from google.cloud import storage
from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings
import mimetypes
from django.utils import timezone

from django.core.files.base import ContentFile
import uuid
from django.db import transaction



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
    #profile_pic= models.TextField(null=True, blank=True)
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
    
from urllib.parse import quote  
class KYCform(models.Model):
    # Link to the authenticated customer
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='kyc_form', unique=True)
    # Attachments
    kyc_form = models.FileField(upload_to='Forms/KYC/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    submission_date = models.DateField(auto_now_add=True)

    def get_download_url(self):
        return self.kyc_form if self.kyc_form else None
    
    def __str__(self):
        return f"KYC Form for {self.customer}"  # Assuming the customer model has a field like 'name'
    class Meta:
        verbose_name_plural = "KYC Forms"
   
    def save(self, *args, **kwargs):
        if self.kyc_form:
            # Generate a unique filename for each upload
            filename = f"{uuid.uuid4()}/{self.kyc_form.name}"
            
            # Upload the file to Google Cloud Storage
            uploaded_url = self.upload_form(self.kyc_form, filename)
            
            # Save the URL path in the model
            if uploaded_url:
                self.kyc_form.name = uploaded_url
            else:
                print("Failed to upload KYC form to Google Cloud Storage.")
        
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Error saving KYC Form instance: {e}")
            
    @staticmethod
    def upload_form(file, filename):
        try:
            client = storage.Client()
            bucket = client.get_bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob('Forms/KYC/' + filename)
            #blob.upload_from_file(file)
            # Set the content type based on the file extension
            content_type, encoding = mimetypes.guess_type(filename)
            blob.upload_from_file(file, content_type=content_type)
            return blob.public_url
        except Exception as e:
            print("Failed to upload!")
            return None
        
class CopyOfOmang(models.Model):
    # Link to the authenticated customer
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='copy_of_omang', unique=True)
    # Attachments
    copy_of_omang = models.FileField(upload_to='Forms/CopyOfOmang/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    submission_date = models.DateField(auto_now_add=True)

    def get_download_url(self):
        return self.copy_of_omang if self.copy_of_omang else None
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.copy_of_omang:
            # Generate a unique filename for each upload
            filename = f"{uuid.uuid4()}/{self.copy_of_omang.name}"
            
            # Upload the file to Google Cloud Storage
            uploaded_url = self.upload_form(self.copy_of_omang, filename)
            
            # Save the URL path in the model
            if uploaded_url:
                self.copy_of_omang.name = uploaded_url
            else:
                print("Failed to upload Copy Of Omang  form to Google Cloud Storage.")
        
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Error saving Copy of Omang Form instance: {e}")
            
    @staticmethod
    def upload_form(file, filename):
        try:
            client = storage.Client()
            bucket = client.get_bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob('Forms/CopyOfOmang/' + filename)
            #blob.upload_from_file(file)
            # Set the content type based on the file extension
            content_type, encoding = mimetypes.guess_type(filename)
            blob.upload_from_file(file, content_type=content_type)
            return blob.public_url
        except Exception as e:
            print("Failed to upload!")
            return None
            
    def __str__(self):
        return f"{self.customer.user.get_full_name()} - Copy of Omang {self.id}"

# Proof Of Residence 
class ResidenceProof(models.Model):
    # Link to the authenticated customer
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='residence_proof', unique=True)
    # Attachments
    residence_proof = models.FileField(upload_to='Forms/ResidenceProof/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    submission_date = models.DateField(auto_now_add=True)

    def get_download_url(self):
        return self.residence_proof if self.residence_proof else None
   
    def save(self, *args, **kwargs):
        if self.residence_proof:
            # Generate a unique filename for each upload
            filename = f"{uuid.uuid4()}/{self.residence_proof.name}"
            
            # Upload the file to Google Cloud Storage
            uploaded_url = self.upload_form(self.residence_proof, filename)
            
            # Save the URL path in the model
            if uploaded_url:
                self.residence_proof.name = uploaded_url
            else:
                print("Failed to upload proof of residence form to Google Cloud Storage.")
        
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Error savingproof of residence Form instance: {e}")
            
    def __str__(self):
        return f"{self.customer.user.get_full_name()} - Residence Proof {self.id}"
            
    @staticmethod
    def upload_form(file, filename):
        try:
            client = storage.Client()
            bucket = client.get_bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob('Forms/ResidenceProof/' + filename)
            #blob.upload_from_file(file)
            # Set the content type based on the file extension
            content_type, encoding = mimetypes.guess_type(filename)
            blob.upload_from_file(file, content_type=content_type)
            return blob.public_url
        except Exception as e:
            print("Failed to upload!")
            return None
        
    def __str__(self):
        return f"{self.customer.user.get_full_name()} - Residence Proof {self.id}"     

#Proof of Income Model
class IncomeProof(models.Model):
    # Link to the authenticated customer
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='income_proof', unique=True)
    # Attachments
    income_proof = models.FileField(upload_to='Forms/IncomeProof/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    submission_date = models.DateField(auto_now_add=True)

    def get_download_url(self):
        return self.income_proof if self.income_proof else None
   
    def save(self, *args, **kwargs):
        if self.income_proof:
            # Generate a unique filename for each upload
            filename = f"{uuid.uuid4()}/{self.income_proof.name}"
            
            # Upload the file to Google Cloud Storage
            uploaded_url = self.upload_form(self.income_proof, filename)
            
            # Save the URL path in the model
            if uploaded_url:
                self.income_proof.name = uploaded_url
            else:
                print("Failed to upload proof of income form to Google Cloud Storage.")
        
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Error saving proof of income Form instance: {e}")
            
    @staticmethod
    def upload_form(file, filename):
        try:
            client = storage.Client()
            bucket = client.get_bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob('Forms/IncomeProof/' + filename)
            #blob.upload_from_file(file)
            # Set the content type based on the file extension
            content_type, encoding = mimetypes.guess_type(filename)
            blob.upload_from_file(file, content_type=content_type)
            return blob.public_url
        except Exception as e:
            print("Failed to upload!")
            return None  
        
    def __str__(self):
        return f"{self.customer.user.get_full_name()} - Income Proof {self.id}"

class DirectDebitForm(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='direct_debit_forms')
    submission_date = models.DateField(auto_now_add=True)
    file_upload = models.FileField(upload_to='Forms/DirectDebit/', null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])])

    def get_download_url(self):
        if self.file_upload:
            return self.file_upload.url
        return None
    
    def save(self, *args, **kwargs):
        # Additional logic before saving, if needed
        super().save(*args, **kwargs)
        # Additional logic after saving, if needed

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

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
    title_deed = models.FileField(max_length=255, null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    # Financial Interest
    financial_interest = models.TextField(blank=True, null=True)
    # Submission Date
    submission_date = models.DateField(auto_now_add=True)

    def get_download_url(self):
        return self.title_deed if self.title_deed else None

    def save(self, *args, **kwargs):
        try:
            # Ensure id is not set explicitly to None
            if self.id is None:
                self.id = None

            super().save(*args, **kwargs)

            # Upload title_deed to Google Cloud Storage
            if self.title_deed:
                file_name = self.title_deed.name
                file = self.title_deed.file
                public_url = self.upload_form(file, file_name)

                # Set the title_deed field to the Google Cloud Storage URL
                self.title_deed.name = public_url
                super().save(*args, **kwargs)
        except ValidationError as e:
            print(f"Validation error saving HomeownersCover instance: {e}")
        except Exception as e:
            print(f"Error saving HomeownersCover instance: {e}")

    @staticmethod
    def upload_form(file, filename):
        try:
            client = storage.Client()
            bucket = client.get_bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob('Forms/HomeOwnersCover/' + filename)

            # Set the content type based on the file extension
            content_type, encoding = mimetypes.guess_type(filename)
            blob.upload_from_file(file, content_type=content_type)

            return blob.public_url
        except Exception as e:
            print("Failed to upload!")
            return None

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
    blue_book = models.FileField(max_length=255, null=True, blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    car_type = models.CharField(max_length=10, choices=CAR_TYPE_CHOICES, default='')
    relationship_to_owner = models.TextField(blank=True, null=True)
    submission_date = models.DateField(auto_now_add=True)
            
    def get_download_url(self):
        return self.blue_book if self.blue_book else None

    def save(self, *args, **kwargs):
        try:
            # Ensure id is not set explicitly to None
            if self.id is None:
                self.id = None

            super().save(*args, **kwargs)

            # Upload blue_book to Google Cloud Storage
            if self.blue_book:
                file_name = self.blue_book.name
                file = self.blue_book.file
                public_url = self.upload_form(file, file_name)

                # Set the blue_book field to the Google Cloud Storage URL
                self.blue_book.name = public_url
                super().save(*args, **kwargs)
        except ValidationError as e:
            print(f"Validation error saving Third Party Cover instance: {e}")
        except Exception as e:
            print(f"Error saving Third Party Cover instance: {e}")

    @staticmethod
    def upload_form(file, filename):
        try:
            client = storage.Client()
            bucket = client.get_bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob('Forms/ThirdPartyCarCover/' + filename)

            # Set the content type based on the file extension
            content_type, encoding = mimetypes.guess_type(filename)
            blob.upload_from_file(file, content_type=content_type)

            return blob.public_url
        except Exception as e:
            print("Failed to upload!")
            return None