from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.core.files.base import ContentFile
import uuid
from django.db import transaction
from datetime import timedelta
from dateutil.relativedelta import relativedelta



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
    
    KYC_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Compliant', 'Compliant'),
        ('Non-Compliant', 'Non-Compliant'),
        ('Renewal Required', 'Renewal Required'),
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
    
    # KYC Compliance fields
    kyc_status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='Pending', help_text="Current KYC compliance status")
    kyc_approval_date = models.DateTimeField(null=True, blank=True, help_text="Date when KYC was approved")
    kyc_expiry_date = models.DateField(null=True, blank=True, help_text="Date when KYC expires (typically 1-2 years from approval)")
    kyc_reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='kyc_reviews', help_text="Admin who reviewed the KYC")
    kyc_notes = models.TextField(null=True, blank=True, help_text="Notes about KYC status, reasons for rejection, etc.")
    kyc_last_updated = models.DateTimeField(auto_now=True, help_text="Last time KYC status was updated")
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    
    @property
    def is_kyc_compliant(self):
        """Check if customer is KYC compliant"""
        return self.kyc_status == 'Compliant'
    
    @property
    def kyc_expires_soon(self):
        """Check if KYC expires within 30 days"""
        if self.kyc_expiry_date and self.kyc_status == 'Compliant':
            days_until_expiry = (self.kyc_expiry_date - timezone.now().date()).days
            return 0 <= days_until_expiry <= 30
        return False
    
    @property
    def kyc_is_expired(self):
        """Check if KYC has expired"""
        if self.kyc_expiry_date:
            return timezone.now().date() > self.kyc_expiry_date
        return False
    
    @property
    def days_until_kyc_expiry(self):
        """Calculate days until KYC expiry"""
        if self.kyc_expiry_date:
            delta = self.kyc_expiry_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def days_since_kyc_expired(self):
        """Calculate days since KYC expired (positive number)"""
        if self.kyc_expiry_date:
            delta = self.kyc_expiry_date - timezone.now().date()
            if delta.days < 0:
                return abs(delta.days)
        return None
    
    def mark_kyc_for_renewal(self):
        """Mark KYC as requiring renewal"""
        self.kyc_status = 'Renewal Required'
        self.save(update_fields=['kyc_status', 'kyc_last_updated'])
    
    def approve_kyc(self, reviewed_by, expiry_months=12, notes=""):
        """Approve KYC with expiry date"""
        self.kyc_status = 'Compliant'
        self.kyc_approval_date = timezone.now()
        self.kyc_expiry_date = timezone.now().date() + relativedelta(months=expiry_months)
        self.kyc_reviewed_by = reviewed_by
        if notes:
            self.kyc_notes = notes
        self.save(update_fields=['kyc_status', 'kyc_approval_date', 'kyc_expiry_date', 'kyc_reviewed_by', 'kyc_notes', 'kyc_last_updated'])
    
    def reject_kyc(self, reviewed_by, reason=""):
        """Reject KYC application"""
        self.kyc_status = 'Non-Compliant'
        self.kyc_reviewed_by = reviewed_by
        self.kyc_notes = reason
        self.kyc_approval_date = None
        self.kyc_expiry_date = None
        self.save(update_fields=['kyc_status', 'kyc_reviewed_by', 'kyc_notes', 'kyc_approval_date', 'kyc_expiry_date', 'kyc_last_updated'])
    
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
        # Simply save the model - Django will handle file storage to MEDIA_ROOT automatically
        super().save(*args, **kwargs)
            
    def get_download_url(self):
        """Return the URL to access the uploaded file"""
        if self.kyc_form:
            return self.kyc_form.url
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
        """Return the URL to access the uploaded file"""
        if self.copy_of_omang:
            return self.copy_of_omang.url
        return None
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        # Simply save the model - Django will handle file storage to MEDIA_ROOT automatically
        super().save(*args, **kwargs)
            
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
        """Return the URL to access the uploaded file"""
        if self.residence_proof:
            return self.residence_proof.url
        return None
   
    def save(self, *args, **kwargs):
        # Simply save the model - Django will handle file storage to MEDIA_ROOT automatically
        super().save(*args, **kwargs)
            
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
        """Return the URL for downloading the uploaded document"""
        return self.income_proof.url if self.income_proof else None
   
    def save(self, *args, **kwargs):
        # Simply save the model - Django will handle file storage to MEDIA_ROOT automatically
        super().save(*args, **kwargs)  
        
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