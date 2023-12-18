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

class Policy(models.Model):
    category= models.ForeignKey('Category', on_delete=models.CASCADE)
    insured = models.ForeignKey(Customer, on_delete=models.CASCADE, to_field='id_number', null=True, related_name='policies')
    policy_name=models.CharField(max_length=205)
    sum_assurance=models.PositiveIntegerField()
    premium=models.PositiveIntegerField()
    tenure=models.PositiveIntegerField()
    creation_date =models.DateField(auto_now=True)
    cover_start = models.DateField(null=True)  # New field for cover start date
    cover_end = models.DateField(null=True) 
    policy_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    def __str__(self):
        return self.policy_name
    
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
    customer= models.ForeignKey(Customer, on_delete=models.CASCADE)
    Policy= models.ForeignKey(Policy, on_delete=models.CASCADE)
    status = models.CharField(max_length=100,default='Pending')
    creation_date =models.DateField(auto_now=True)
    
    @property
    def cover_start(self):
        return self.policy.cover_start  
    
    @property
    def cover_end(self):
        return self.policy.cover_end  
    
    @property
    def tenure(self):
        return self.policy.tenure
    
    def __str__(self):
        return f"{self.customer} - {self.Policy} - {self.status}"

class Question(models.Model):
    customer= models.ForeignKey(Customer, on_delete=models.CASCADE)
    description =models.CharField(max_length=500)
    admin_comment=models.CharField(max_length=200,default='Nothing')
    asked_date =models.DateField(auto_now=True)
    def __str__(self):
        return self.description