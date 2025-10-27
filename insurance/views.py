from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.auth.models import User
from customer import models as CMODEL
from customer import forms as CFORM
from .models import CustomModelName, PolicyRecord
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views import View
from .forms import PolicyForm 
from customer.models import Customer 
from .models import Category
from django.http import JsonResponse

#@login_required
@login_required(login_url='adminlogin')
def custom_dashboard(request):
    user = request.user
    return render(request, 'insurance/adminbase.html', {'user': user})

def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request,'insurance/index.html')


def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


def afterlogin_view(request):
    if is_customer(request.user):      
        return redirect('customer:customer-dashboard')
    else:
        return redirect('admin-dashboard')
    
def logout_redirect(request):
        return redirect('adminlogin')



def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict={
        'total_user':CMODEL.Customer.objects.all().count(),
        'total_policy':models.Policy.objects.all().count(),
        'total_thirdpartypolicy':models.ThirdpartyPolicy.objects.all().count(),
        'total_category':models.Category.objects.all().count(),
        'total_question':models.Question.objects.all().count(),
        'total_policy_holder':models.PolicyRecord.objects.all().count(),
        'approved_policy_holder':models.PolicyRecord.objects.all().filter(status='Approved').count(),
        'disapproved_policy_holder':models.PolicyRecord.objects.all().filter(status='Disapproved').count(),
        'waiting_policy_holder':models.PolicyRecord.objects.all().filter(status='Pending').count(),
        'total_thirdpartypolicy_holder':models.ThirdpartyPolicyRecord.objects.all().count(),
        'approved_thirdpartypolicy_holder':models.ThirdpartyPolicyRecord.objects.all().filter(thirdpartystatus='Approved').count(),
        'disapproved_thirdpartypolicy_holder':models.ThirdpartyPolicyRecord.objects.all().filter(thirdpartystatus='Disapproved').count(),
        'waiting_thirdpartypolicy_holder':models.ThirdpartyPolicyRecord.objects.all().filter(thirdpartystatus='Pending').count(),
    }
    return render(request,'insurance/admin_dashboard.html',context=dict)

'''
from django.db.models import Count
@login_required(login_url='adminlogin')
def admin_view_customer_view(request):
    customers= CMODEL.Customer.objects.filter(user__groups__name='CUSTOMER')
    return render(request,'insurance/admin_view_customer.html',{'customers':customers})
'''
import json
from django.db.models import Count
from .models import Customer
@login_required(login_url='adminlogin')
def admin_view_customer_view(request):
    customers = Customer.objects.filter(user__groups__name='CUSTOMER')

    # Count the number of users for each gender
    gender_distribution = customers.values('gender').annotate(count=Count('gender'))
    # Count the number of customers for each marital status
    marital_status_distribution = customers.values('marital_status').annotate(count=Count('marital_status'))

    total_users = customers.count()
    total_customers = customers.count()

    # Calculate the percentage of each gender category
    gender_percentage = {}
    for entry in gender_distribution:
        gender_percentage[entry['gender']] = (entry['count'] / total_users) * 100

    # Serialize gender_percentage dictionary to JSON
    gender_percentage_json = json.dumps(gender_percentage)
    
    # Extract marital status counts
    marital_status_counts = {}
    for entry in marital_status_distribution:
        marital_status_counts[entry['marital_status']] = entry['count']
        
    # Get individual counts for template use
    male_count = customers.filter(gender='M').count()
    female_count = customers.filter(gender='F').count()
    married_count = customers.filter(marital_status='M').count()
    single_count = customers.filter(marital_status='S').count()
        
    # Serialize marital_status_counts dictionary to JSON
    marital_status_counts_json = json.dumps(marital_status_counts)
    print("Marital Status Counts:", marital_status_counts)
    print("gender_percentage", gender_percentage_json)

    context = {
        'customers': customers, 
        'gender_percentage_json': gender_percentage_json,
        'marital_status_counts_json': marital_status_counts_json,
        'male_count': male_count,
        'female_count': female_count,
        'married_count': married_count,
        'single_count': single_count,
    }
    
    return render(request, 'insurance/admin_view_customer.html', context)


# In your views.py
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import sweetify

from django.http import HttpResponseRedirect
@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    print("Entering update_customer_view")
    customer = CMODEL.Customer.objects.get(pk=pk)
    user = CMODEL.User.objects.get(id=customer.user_id)

    if request.method == 'POST':
        print("Processing POST request")
        
        # Use the update form (without password requirement)
        userForm = CFORM.CustomerUserUpdateForm(request.POST, instance=user)
        customerForm = CFORM.CustomerForm(request.POST, request.FILES, instance=customer)

        if userForm.is_valid() and customerForm.is_valid():
            print("Forms are valid")
            user = userForm.save(commit=False)
            user.save()
            customerForm.save()
            print("Customer updated successfully")
            messages.success(request, "User details updated successfully!")
            return redirect(reverse('admin-view-customer') + '?customer_updated=True')
        else:
            print("User Form Errors:", userForm.errors)
            print("Customer Form Errors:", customerForm.errors)
    else:
        print("Rendering update form")
        userForm = CFORM.CustomerUserUpdateForm(instance=user)
        customerForm = CFORM.CustomerForm(instance=customer)
        
    mydict = {'userForm': userForm, 'customerForm': customerForm, 'customer': customer}
    return render(request, 'insurance/update_customer.html', context=mydict)

@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=CMODEL.Customer.objects.get(id=pk)
    user=User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    messages.success(request, "User deleted successfully!")
    return HttpResponseRedirect('/admin-view-customer')

def admin_category_view(request):
    return render(request,'insurance/admin_category.html')

def admin_add_category_view(request):
    categoryForm=forms.CategoryForm() 
    if request.method=='POST':
        categoryForm=forms.CategoryForm(request.POST)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('admin-view-category')
    return render(request,'insurance/admin_add_category.html',{'categoryForm':categoryForm})

def admin_view_category_view(request):
    categories = models.Category.objects.all()
    return render(request,'insurance/admin_view_category.html',{'categories':categories})

def admin_delete_category_view(request):
    categories = models.Category.objects.all()
    return render(request,'insurance/admin_delete_category.html',{'categories':categories})
    
def delete_category_view(request,pk):
    category = models.Category.objects.get(id=pk)
    category.delete()
    return redirect('admin-delete-category')

def admin_update_category_view(request):
    categories = models.Category.objects.all()
    return render(request,'insurance/admin_update_category.html',{'categories':categories})

@login_required(login_url='adminlogin')
def update_category_view(request,pk):
    category = models.Category.objects.get(id=pk)
    categoryForm=forms.CategoryForm(instance=category)
    
    if request.method=='POST':
        categoryForm=forms.CategoryForm(request.POST,instance=category)
        
        if categoryForm.is_valid():

            categoryForm.save()
            return redirect('admin-update-category')
    return render(request,'insurance/update_category.html',{'categoryForm':categoryForm})
  
  

def admin_policy_view(request):
    return render(request,'insurance/admin_policy.html')

from datetime import timedelta, date
import calendar

# Function to generate months with their actual number of days in that particular year
def add_months(start_date, months):
    # Function to add months to a date
    month = start_date.month - 1 + months
    year = start_date.year + month // 12
    month = month % 12 + 1
    last_day_of_month = calendar.monthrange(year, month)[1]
    day = min(start_date.day, last_day_of_month)
    return date(year, month, day)

# Function to generate policy_number based on your specific logic
def generate_policy_number(policy):
    # You can implement your logic here to generate the policy_number
    # For example, if you have it stored as an attribute of the Policy model:
    return policy.policy_number

from .forms import PolicyForm, ThirdpartyPolicyForm

def admin_add_policy_view(request):
    policyForm = PolicyForm()
    print("Request method:", request.method)
    if request.method == 'POST':
        policyForm = PolicyForm(request.POST)
        print("Policy Form:", policyForm)
        if policyForm.is_valid():
            print("Form is valid")
            id_number = request.POST.get('id_number')
            print("ID Number:", id_number)
            category_id = request.POST.get('category')
            print("Category ID:", category_id)
            category = Category.objects.get(id=category_id)
            print("Category:", category)
            try:
                customer = models.Customer.objects.get(id_number=id_number)
                print("Customer:", customer)
            except models.Customer.DoesNotExist:
                print('Customer with ID number', id_number, 'does not exist')
                return render(request, 'insurance/error_template.html', {'error_message': 'Customer not found'})

            policy = policyForm.save(commit=False)
            print("Policy before assignment:", policy)
            policy.category = category
            policy.insured = customer
            policy.cover_start = policyForm.cleaned_data['cover_start']
            policy.tenure = policyForm.cleaned_data['tenure']
            policy.cover_end = add_months(policy.cover_start, policy.tenure)
            print("Policy after assignment:", policy)

            # Save the policy
            policy.save()
            messages.success(request, "Cover created Successfully!")
            print("Policy successfully saved!")
            print("Policy Number:", policy.policy_number)
            print("Cover End:", policy.cover_end)

            return redirect('admin-view-policy')

    return render(request, 'insurance/admin_add_policy.html', {'policyForm': policyForm})

def admin_apply_thirdparty_view(request):
    thirdpartypolicyForm = ThirdpartyPolicyForm()
    print("Request method:", request.method)
    if request.method == 'POST':
        thirdpartypolicyForm = ThirdpartyPolicyForm(request.POST)
        print("Policy Form:", thirdpartypolicyForm)
        if thirdpartypolicyForm.is_valid():
            print("Form is valid")
            id_number = request.POST.get('id_number')
            print("ID Number:", id_number)
            category_id = request.POST.get('category')
            print("Category ID:", category_id)
            category = Category.objects.get(id=category_id)
            print("Category:", category)
            try:
                customer = models.Customer.objects.get(id_number=id_number)
                print("Customer:", customer)
            except models.Customer.DoesNotExist:
                print('Customer with ID number', id_number, 'does not exist')
                return render(request, 'insurance/error_template.html', {'error_message': 'Customer not found'})

            # Check if customer has approved homeowners coverage
            approved_homeowners = PolicyRecord.objects.filter(
                customer=customer, 
                status__in=['Approved', 'Active']
            ).exists()
            
            if not approved_homeowners:
                messages.error(request, 
                    f"Customer {customer.get_name()} (ID: {id_number}) does not have approved homeowners coverage. "
                    "Motor insurance can only be offered as an add-on to existing homeowners coverage. "
                    "Please ensure the customer has approved homeowners insurance first."
                )
                return render(request, 'insurance/admin_add_thirdparty.html', {'thirdpartypolicyForm': thirdpartypolicyForm})

            policy = thirdpartypolicyForm.save(commit=False)
            print("Policy before assignment:", policy)
            policy.category = category
            policy.insured = customer
            policy.cover_start = thirdpartypolicyForm.cleaned_data['cover_start']
            policy.tenure = thirdpartypolicyForm.cleaned_data['tenure']
            policy.cover_end = add_months(policy.cover_start, policy.tenure)
            print("Policy after assignment:", policy)

            # Save the policy
            policy.save()
            messages.success(request, f"Motor insurance add-on created successfully for {customer.get_name()}!")
            print("Policy successfully saved!")
            print("Policy Number:", policy.policy_number)
            print("Cover End:", policy.cover_end)
        return redirect('admin-view-thirdpartypolicy')

    return render(request, 'insurance/admin_add_thirdparty.html', {'thirdpartypolicyForm': thirdpartypolicyForm})

def get_user_details_view(request, id_number):
    if request.method == 'GET':
        try:
            customer = models.Customer.objects.get(id_number=id_number)
            user_details = {
                'name': customer.user.get_full_name(),
                'address': customer.address,
                'mobile': customer.mobile,
                'id_number': customer.id_number,
                'postal_address': customer.postal_address,
                'physical_address': customer.physical_address,
                'occupation': customer.occupation,
                'alternate_phone': customer.alternate_phone,
                'date_of_birth': customer.date_of_birth,
                'gender': customer.gender,
                'marital_status': customer.marital_status         
            }
            return JsonResponse({'success': True, 'user': user_details})
        except models.Customer.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'Customer not found'})
    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})




def admin_view_policy_view(request):
    policies = models.Policy.objects.all()
    
    # Fetch customer details for each policy based on insured_id
    customers = Customer.objects.filter(id_number__in=[policy.insured_id for policy in policies])

    # Create a dictionary to map customer id_numbers to customer details
    customer_details = {customer.id_number: customer for customer in customers}

    # Add customer details to each policy
    for policy in policies:
        policy.customer_details = customer_details.get(policy.insured_id)
        
    return render(request,'insurance/admin_view_policy.html',{'policies':policies})

def admin_view_thirdpartypolicy_view(request):
    policies = models.ThirdpartyPolicy.objects.all()
    
    # Fetch customer details for each policy based on insured_id
    customers = Customer.objects.filter(id_number__in=[policy.insured_id for policy in policies])

    # Create a dictionary to map customer id_numbers to customer details
    customer_details = {customer.id_number: customer for customer in customers}

    # Add customer details to each policy
    for policy in policies:
        policy.customer_details = customer_details.get(policy.insured_id)
        
    return render(request,'insurance/admin_view_thirdpartypolicy.html',{'policies':policies})
'''
def admin_view_thirdpartypolicy_view(request):
    policies = models.ThirdpartyPolicy.objects.all()
    
    # Fetch customer details for each policy based on insured_id
    customers = Customer.objects.filter(id_number__in=[policy.insured_id for policy in policies])

    # Create a dictionary to map customer id_numbers to customer details
    customer_details = {customer.id_number: customer for customer in customers}

    # Add customer details to each policy
    for policy in policies:
        policy.customer_details = customer_details.get(policy.insured_id)
        
    return render(request,'insurance/admin_view_policy.html',{'policies':policies})
'''


def admin_update_policy_view(request):
    policies = models.Policy.objects.all()
    return render(request,'insurance/admin_update_policy.html',{'policies':policies})

@login_required(login_url='adminlogin')
def update_policy_view(request,pk):
    policy = models.Policy.objects.get(id=pk)
    policyForm=forms.PolicyForm(instance=policy)
    
    if request.method=='POST':
        policyForm=forms.PolicyForm(request.POST,instance=policy)
        
        if policyForm.is_valid():

            categoryid = request.POST.get('category')
            category = models.Category.objects.get(id=categoryid)
            
            policy = policyForm.save(commit=False)
            policy.category=category
            policy.save()
           
            return redirect('admin-update-policy')
    return render(request,'insurance/update_policy.html',{'policyForm':policyForm})
  
  
def admin_delete_policy_view(request):
    policies = models.Policy.objects.all()
    return render(request,'insurance/admin_delete_policy.html',{'policies':policies})
    
def delete_policy_view(request,pk):
    policy = models.Policy.objects.get(id=pk)
    policy.delete()
    return redirect('admin-delete-policy')

def admin_view_policy_holder_view(request):
    # Get all homeowners policy records
    homeowners_records = models.PolicyRecord.objects.select_related('Policy', 'customer__user').all()
    
    # Get all third-party policy records  
    thirdparty_records = models.ThirdpartyPolicyRecord.objects.select_related('thirdpartypolicy', 'thirdpartycustomer__user').all()
    
    # Calculate counts for homeowners policies
    homeowners_pending = homeowners_records.filter(status='Pending').count()
    homeowners_approved = homeowners_records.filter(status='Approved').count()
    homeowners_rejected = homeowners_records.filter(status='Rejected').count()
    
    # Calculate counts for third-party policies
    thirdparty_pending = thirdparty_records.filter(thirdpartystatus='Pending').count()
    thirdparty_approved = thirdparty_records.filter(thirdpartystatus='Approved').count()
    thirdparty_rejected = thirdparty_records.filter(thirdpartystatus='Rejected').count()
    
    # Total counts
    total_pending = homeowners_pending + thirdparty_pending
    total_approved = homeowners_approved + thirdparty_approved
    total_rejected = homeowners_rejected + thirdparty_rejected
    total_applications = homeowners_records.count() + thirdparty_records.count()
    
    # Create customer policy relationships to show motor insurance dependencies
    customer_policies = {}
    
    # Track homeowners policies by customer
    for record in homeowners_records:
        customer_id = record.customer.id
        if customer_id not in customer_policies:
            customer_policies[customer_id] = {
                'customer': record.customer,
                'homeowners': [],
                'motor': [],
                'total_premium': 0
            }
        customer_policies[customer_id]['homeowners'].append(record)
        customer_policies[customer_id]['total_premium'] += float(record.Policy.premium)
    
    # Track motor policies by customer and link to homeowners
    for record in thirdparty_records:
        customer_id = record.thirdpartycustomer.id
        if customer_id not in customer_policies:
            customer_policies[customer_id] = {
                'customer': record.thirdpartycustomer,
                'homeowners': [],
                'motor': [],
                'total_premium': 0
            }
        customer_policies[customer_id]['motor'].append(record)
        customer_policies[customer_id]['total_premium'] += float(record.thirdpartypolicy.premium)
    
    return render(request,'insurance/admin_view_policy_holder.html',{
        'homeowners_records': homeowners_records,
        'thirdparty_records': thirdparty_records,
        'customer_policies': customer_policies,
        'total_applications': total_applications,
        'pending_count': total_pending,
        'approved_count': total_approved,
        'rejected_count': total_rejected,
        'homeowners_pending': homeowners_pending,
        'homeowners_approved': homeowners_approved,
        'homeowners_rejected': homeowners_rejected,
        'thirdparty_pending': thirdparty_pending,
        'thirdparty_approved': thirdparty_approved,
        'thirdparty_rejected': thirdparty_rejected,
    })

def admin_view_thirdpartypolicy_holder_view(request):
    #policyrecords = models.ThirdpartyPolicyRecord.objects.all()
    policyrecords = models.ThirdpartyPolicyRecord.objects.select_related('thirdpartypolicy').all()
    return render(request,'insurance/admin_view_thirdpartypolicy_holder.html',{'policyrecords':policyrecords})

def admin_view_approved_policy_holder_view(request):
    # Get approved homeowners and motor policies
    homeowners_records = models.PolicyRecord.objects.filter(status='Approved').select_related('Policy', 'customer__user')
    thirdparty_records = models.ThirdpartyPolicyRecord.objects.filter(thirdpartystatus='Approved').select_related('thirdpartypolicy', 'thirdpartycustomer__user')
    
    # Calculate counts
    homeowners_approved = homeowners_records.count()
    thirdparty_approved = thirdparty_records.count()
    total_approved = homeowners_approved + thirdparty_approved
    
    # Create customer policy relationships
    customer_policies = {}
    
    for record in homeowners_records:
        customer_id = record.customer.id
        if customer_id not in customer_policies:
            customer_policies[customer_id] = {
                'customer': record.customer,
                'homeowners': [],
                'motor': [],
                'total_premium': 0
            }
        customer_policies[customer_id]['homeowners'].append(record)
        customer_policies[customer_id]['total_premium'] += float(record.Policy.premium)
    
    for record in thirdparty_records:
        customer_id = record.thirdpartycustomer.id
        if customer_id not in customer_policies:
            customer_policies[customer_id] = {
                'customer': record.thirdpartycustomer,
                'homeowners': [],
                'motor': [],
                'total_premium': 0
            }
        customer_policies[customer_id]['motor'].append(record)
        customer_policies[customer_id]['total_premium'] += float(record.thirdpartypolicy.premium)
    
    return render(request,'insurance/admin_view_approved_policy_holder.html',{
        'customer_policies': customer_policies,
        'homeowners_records': homeowners_records,
        'thirdparty_records': thirdparty_records,
        'approved_count': total_approved,
        'homeowners_approved': homeowners_approved,
        'thirdparty_approved': thirdparty_approved,
    })

def admin_view_approved_thirdpartypolicy_holder_view(request):
    policyrecords = models.ThirdpartyPolicyRecord.objects.all().filter(thirdpartystatus='Approved')
    return render(request,'insurance/admin_view_approved_thirdpartypolicy_holder.html',{'policyrecords':policyrecords})

def admin_view_disapproved_policy_holder_view(request):
    # Get rejected homeowners and motor policies
    homeowners_records = models.PolicyRecord.objects.filter(status='Rejected').select_related('Policy', 'customer__user')
    thirdparty_records = models.ThirdpartyPolicyRecord.objects.filter(thirdpartystatus='Rejected').select_related('thirdpartypolicy', 'thirdpartycustomer__user')
    
    # Calculate counts
    homeowners_rejected = homeowners_records.count()
    thirdparty_rejected = thirdparty_records.count()
    total_rejected = homeowners_rejected + thirdparty_rejected
    
    # Create customer policy relationships
    customer_policies = {}
    
    for record in homeowners_records:
        customer_id = record.customer.id
        if customer_id not in customer_policies:
            customer_policies[customer_id] = {
                'customer': record.customer,
                'homeowners': [],
                'motor': [],
                'total_premium': 0
            }
        customer_policies[customer_id]['homeowners'].append(record)
        customer_policies[customer_id]['total_premium'] += float(record.Policy.premium)
    
    for record in thirdparty_records:
        customer_id = record.thirdpartycustomer.id
        if customer_id not in customer_policies:
            customer_policies[customer_id] = {
                'customer': record.thirdpartycustomer,
                'homeowners': [],
                'motor': [],
                'total_premium': 0
            }
        customer_policies[customer_id]['motor'].append(record)
        customer_policies[customer_id]['total_premium'] += float(record.thirdpartypolicy.premium)
    
    return render(request,'insurance/admin_view_disapproved_policy_holder.html',{
        'customer_policies': customer_policies,
        'homeowners_records': homeowners_records,
        'thirdparty_records': thirdparty_records,
        'rejected_count': total_rejected,
        'homeowners_rejected': homeowners_rejected,
        'thirdparty_rejected': thirdparty_rejected,
    })

def admin_view_disapproved_thirdpartypolicy_holder_view(request):
    policyrecords = models.ThirdpartyPolicyRecord.objects.all().filter(thirdpartystatus='Disapproved')
    return render(request,'insurance/admin_view_disapproved_thirdpartypolicy_holder.html',{'policyrecords':policyrecords})

def admin_view_waiting_policy_holder_view(request):
    # Get pending homeowners and motor policies
    homeowners_records = models.PolicyRecord.objects.filter(status='Pending').select_related('Policy', 'customer__user')
    thirdparty_records = models.ThirdpartyPolicyRecord.objects.filter(thirdpartystatus='Pending').select_related('thirdpartypolicy', 'thirdpartycustomer__user')
    
    # Calculate counts
    homeowners_pending = homeowners_records.count()
    thirdparty_pending = thirdparty_records.count()
    total_pending = homeowners_pending + thirdparty_pending
    
    # Create customer policy relationships
    customer_policies = {}
    
    for record in homeowners_records:
        customer_id = record.customer.id
        if customer_id not in customer_policies:
            customer_policies[customer_id] = {
                'customer': record.customer,
                'homeowners': [],
                'motor': [],
                'total_premium': 0
            }
        customer_policies[customer_id]['homeowners'].append(record)
        customer_policies[customer_id]['total_premium'] += float(record.Policy.premium)
    
    for record in thirdparty_records:
        customer_id = record.thirdpartycustomer.id
        if customer_id not in customer_policies:
            customer_policies[customer_id] = {
                'customer': record.thirdpartycustomer,
                'homeowners': [],
                'motor': [],
                'total_premium': 0
            }
        customer_policies[customer_id]['motor'].append(record)
        customer_policies[customer_id]['total_premium'] += float(record.thirdpartypolicy.premium)
    
    return render(request,'insurance/admin_view_waiting_policy_holder.html',{
        'customer_policies': customer_policies,
        'homeowners_records': homeowners_records,
        'thirdparty_records': thirdparty_records,
        'pending_count': total_pending,
        'homeowners_pending': homeowners_pending,
        'thirdparty_pending': thirdparty_pending,
    })

def admin_view_waiting_thirdpartypolicy_holder_view(request):
    policyrecords = models.ThirdpartyPolicyRecord.objects.all().filter(thirdpartystatus='Pending')
    return render(request,'insurance/admin_view_waiting_thirdpartypolicy_holder.html',{'policyrecords':policyrecords})

def approve_request_view(request,pk):
    policyrecords = models.PolicyRecord.objects.get(id=pk)
    policyrecords.status='Approved'
    policyrecords.save()
    return redirect('admin-view-policy-holder')

def disapprove_request_view(request,pk):
    policyrecords = models.PolicyRecord.objects.get(id=pk)
    policyrecords.status='Disapproved'
    policyrecords.save()
    return redirect('admin-view-policy-holder')

def approve_thirdpartyrequest_view(request,pk):
    policyrecords = models.ThirdpartyPolicyRecord.objects.get(id=pk)
    policyrecords.thirdpartystatus='Approved'
    policyrecords.save()
    return redirect('admin-view-thirdpartypolicy-holder')

def disapprove_thirdpartyrequest_view(request,pk):
    policyrecords = models.ThirdpartyPolicyRecord.objects.get(id=pk)
    policyrecords.thirdpartystatus='Disapproved'
    policyrecords.save()
    return redirect('admin-view-thirdpartypolicy-holder')


def admin_question_view(request):
    questions = models.Question.objects.all()
    return render(request,'insurance/admin_question.html',{'questions':questions})

from customer.models import Customer, KYCform, CopyOfOmang, ResidenceProof, IncomeProof, HomeownersCover, ThirdPartyCarInsurance

def admin_customerforms(request):
    # Fetch all customers and related documents
    customers = Customer.objects.all()
    
    customer_data = []
    kyc_forms_count = 0
    copy_of_omang_count = 0
    residence_proof_count = 0
    income_proof_count = 0
    
    for customer in customers:
        kyc_form = KYCform.objects.filter(customer=customer).first()
        copy_of_omang = CopyOfOmang.objects.filter(customer=customer).first()
        residence_proof = ResidenceProof.objects.filter(customer=customer).first()
        income_proof = IncomeProof.objects.filter(customer=customer).first()
        
        # Count submitted documents
        if kyc_form:
            kyc_forms_count += 1
        if copy_of_omang:
            copy_of_omang_count += 1
        if residence_proof:
            residence_proof_count += 1
        if income_proof:
            income_proof_count += 1
        
        customer_data.append({
            'customer': customer,
            'kyc_form': kyc_form,
            'copy_of_omang': copy_of_omang,
            'residence_proof': residence_proof,
            'income_proof': income_proof,
        })
    
    context = {
        'customer_data': customer_data,
        'kyc_forms_count': kyc_forms_count,
        'copy_of_omang_count': copy_of_omang_count,
        'residence_proof_count': residence_proof_count,
        'income_proof_count': income_proof_count,
    }
    return render(request, 'insurance/admin_customerforms.html', context)

def admin_homeownersview(request):
    # Fetch all customers and related documents
    customers = Customer.objects.all()
    
    homeowners_data = []
    
    for customer in customers:
        homeowners_cover = HomeownersCover.objects.filter(customer=customer).first()
        
        homeowners_data.append({
            'customer': customer,
            'homeowners_cover': homeowners_cover,
        })
    
    context = {'homeowners_data': homeowners_data}
    return render(request, 'insurance/admin_homeownersview.html', context)

def admin_thirdpartyview(request):
    # Fetch all customers and related documents
    customers = Customer.objects.all()
    
    thirdparty_data = []
    
    for customer in customers:
        thirdparty_cover = ThirdPartyCarInsurance.objects.filter(customer=customer).first()
        
        thirdparty_data.append({
            'customer': customer,
            'thirdparty_cover': thirdparty_cover,
        })
    
    context = {'thirdparty_data': thirdparty_data}
    return render(request, 'insurance/admin_thirdpartyview.html', context)


from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Customer

@require_POST
def delete_selected(request):
    customer_ids = request.POST.getlist('selected_items')

    try:
        customers_to_delete = Customer.objects.filter(id__in=customer_ids)
        customers_to_delete.delete()
        messages.success(request, 'Selected items deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting items: {e}')

    return redirect('insurance/admin_customerforms.html')



def update_question_view(request,pk):
    question = models.Question.objects.get(id=pk)
    questionForm=forms.QuestionForm(instance=question)
    
    if request.method=='POST':
        questionForm=forms.QuestionForm(request.POST,instance=question)
        
        if questionForm.is_valid():

            admin_comment = request.POST.get('admin_comment')
            
            
            question = questionForm.save(commit=False)
            question.admin_comment=admin_comment
            question.save()
           
            return redirect('admin-question')
    return render(request,'insurance/update_question.html',{'questionForm':questionForm})


def aboutus_view(request):
    return render(request,'insurance/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'insurance/contactussuccess.html')
    return render(request, 'insurance/contactus.html', {'form':sub})


from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('afterlogin')  # Redirect to the home page after successful login
        else:
            messages.error(request, 'Incorrect username or password.')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')
    
from django.shortcuts import render

def benefits(request):
    return render(request, 'insurance/benefits.html')

def covers(request):
    return render(request, 'insurance/covers.html')

def claims_view(request):
    return render(request, 'insurance/claims.html')

def claims_guidelines_view(request):
    return render(request, 'insurance/claims_guidelines.html')

@login_required(login_url='adminlogin')
def admin_policy_holder_details_view(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    homeowners = models.PolicyRecord.objects.filter(customer=customer).select_related('Policy')
    motor = models.ThirdpartyPolicyRecord.objects.filter(thirdpartycustomer=customer).select_related('thirdpartypolicy')
    return render(request, 'insurance/admin_policy_holder_details.html', {
        'customer': customer,
        'homeowners': homeowners,
        'motor': motor,
    })
