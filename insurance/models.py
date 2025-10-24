from django.db import models
from django.contrib.auth.models import User
from customer.models import Customer
import random
import string

class CustomModelName(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # instead of user_id = IntegerField()

class Category(models.Model):
    category_name =models.CharField(max_length=20)
    creation_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.category_name
    class Meta:
        verbose_name_plural = "Categories"

class Policy(models.Model):
    category= models.ForeignKey('Category', on_delete=models.CASCADE)
    insured = models.ForeignKey(Customer, on_delete=models.CASCADE, to_field='id_number', null=True, related_name='policies')
    policy_name=models.CharField(max_length=205)
    sum_assurance = models.DecimalField(max_digits=10, decimal_places=2)
    premium = models.DecimalField(max_digits=10, decimal_places=2)
    tenure=models.PositiveIntegerField()
    creation_date =models.DateField(auto_now=True)
    cover_start = models.DateField(null=True)  # New field for cover start date
    cover_end = models.DateField(null=True) 
    policy_number = models.CharField(max_length=21, unique=True, blank=True, null=True)
    expiry_date = models.DateField(null=True) 
    
    # Homeowners Policy Fields
    plot_number = models.CharField(max_length=50, null=True, blank=True, help_text="The official plot number of the property")
    ward_kgotla = models.CharField(max_length=50, null=True, blank=True, help_text="The ward number or traditional authority (Kgotla) area")
    village = models.CharField(max_length=50, null=True, blank=True, help_text="The village or township name")
    district = models.CharField(max_length=50, null=True, blank=True, help_text="The administrative district")
    title_deed = models.FileField(upload_to='homeowners/title_deeds/', null=True, blank=True, help_text="Upload property title deed (optional)")
    financial_interest = models.TextField(null=True, blank=True, help_text="Describe any financial interests, mortgages, or co-ownership details") 
    
    def __str__(self):
        return self.policy_name
    class Meta:
        verbose_name_plural = "Policies"
    
    def save(self, *args, **kwargs):
        if not self.policy_number:
            while True:
                # Generate a random alphanumeric string for the policy number
                random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                # Assign the policy number using the desired format
                potential_policy_number = f"INS-{self.cover_start.year}-{random_string}"

                # Check if the generated policy number is unique
                if not Policy.objects.filter(policy_number=potential_policy_number).exists():
                    self.policy_number = potential_policy_number
                    break

        super().save(*args, **kwargs)

class ThirdpartyPolicy(models.Model):
    category= models.ForeignKey('Category', on_delete=models.CASCADE)
    insured = models.ForeignKey(Customer, on_delete=models.CASCADE, to_field='id_number', null=True, related_name='thirdparty_policies')
    policy_name=models.CharField(max_length=205)
    #sum_assurance = models.DecimalField(max_digits=10, decimal_places=2)
    premium = models.DecimalField(max_digits=11, decimal_places=2)
    tenure=models.PositiveIntegerField()
    creation_date =models.DateField(auto_now=True)
    cover_start = models.DateField(null=True)  # New field for cover start date
    cover_end = models.DateField(null=True) 
    policy_number = models.CharField(max_length=21, unique=True, blank=True, null=True)
    expiry_date = models.DateField(null=True) 
    
    # Vehicle Details
    vehicle_type = models.CharField(max_length=100, null=True, blank=True, help_text="Type of vehicle (e.g., Sedan, SUV, Hatchback)")
    vehicle_make = models.CharField(max_length=100, null=True, blank=True, help_text="Vehicle manufacturer (e.g., Toyota, BMW)")
    vehicle_model = models.CharField(max_length=100, null=True, blank=True, help_text="Vehicle model (e.g., Camry, X5)")
    vehicle_year = models.PositiveIntegerField(null=True, blank=True, help_text="Year of manufacture")
    chassis_number = models.CharField(max_length=50, null=True, blank=True, help_text="Vehicle chassis/VIN number")
    registration_number = models.CharField(max_length=20, null=True, blank=True, help_text="Vehicle registration number")
    engine_number = models.CharField(max_length=50, null=True, blank=True, help_text="Engine serial number")
    territorial_limits = models.TextField(null=True, blank=True, help_text="Geographic coverage limits")
    
    def __str__(self):
        if self.vehicle_make and self.vehicle_model:
            return f"{self.policy_name} - {self.vehicle_make} {self.vehicle_model}"
        return self.policy_name
    class Meta:
        verbose_name_plural = "Thirdparty Policies"
    
    def save(self, *args, **kwargs):
        if not self.policy_number:
            while True:
                # Generate a random alphanumeric string for the policy number
                random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                # Assign the policy number using the desired format
                potential_policy_number = f"INS-{self.cover_start.year}-{random_string}"

                # Check if the generated policy number is unique
                if not Policy.objects.filter(policy_number=potential_policy_number).exists():
                    self.policy_number = potential_policy_number
                    break

        super().save(*args, **kwargs)

class PolicyRecord(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
    ]
    
    customer= models.ForeignKey(Customer, on_delete=models.CASCADE)
    Policy= models.ForeignKey(Policy, on_delete=models.CASCADE)
    status = models.CharField(max_length=101, choices=STATUS_CHOICES, default='Pending')
    creation_date =models.DateField(auto_now=True)
    
    @property
    def cover_start(self):
        return self.Policy.cover_start 
    
    @property
    def cover_end(self):
        return self.Policy.cover_end  
    
    @property
    def tenure(self):
        return self.Policy.tenure
    
    def __str__(self):
        return f"{self.customer} - {self.Policy} - {self.status}"

class ThirdpartyPolicyRecord(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
    ]
    
    thirdpartycustomer= models.ForeignKey(Customer, on_delete=models.CASCADE)
    thirdpartypolicy= models.ForeignKey(ThirdpartyPolicy, null=True, on_delete=models.CASCADE)
    thirdpartystatus = models.CharField(max_length=101, choices=STATUS_CHOICES, default='Pending')
    thirdpartycreation_date =models.DateField(auto_now=True)
    
    @property
    def cover_start(self):
        return self.thirdpartypolicy.cover_start 
    
    @property
    def cover_end(self):
        return self.thirdpartypolicy.cover_end  
    
    @property
    def tenure(self):
        return self.thirdpartypolicy.tenure
    
    def __str__(self):
        return f"{self.thirdpartycustomer} - {self.thirdpartypolicy} - {self.thirdpartystatus}"

class Question(models.Model):
    customer= models.ForeignKey(Customer, on_delete=models.CASCADE)
    description =models.CharField(max_length=500)
    admin_comment=models.CharField(max_length=200,default='Nothing')
    asked_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.description