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
from .models import CustomModelName
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
        return redirect('customer/customer-dashboard')
    else:
        return redirect('admin-dashboard')
    
def logout_redirect(request):
        return redirect('logout')



def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict={
        'total_user':CMODEL.Customer.objects.all().count(),
        'total_policy':models.Policy.objects.all().count(),
        'total_category':models.Category.objects.all().count(),
        'total_question':models.Question.objects.all().count(),
        'total_policy_holder':models.PolicyRecord.objects.all().count(),
        'approved_policy_holder':models.PolicyRecord.objects.all().filter(status='Approved').count(),
        'disapproved_policy_holder':models.PolicyRecord.objects.all().filter(status='Disapproved').count(),
        'waiting_policy_holder':models.PolicyRecord.objects.all().filter(status='Pending').count(),
    }
    return render(request,'insurance/admin_dashboard.html',context=dict)



@login_required(login_url='adminlogin')
def admin_view_customer_view(request):
    customers= CMODEL.Customer.objects.filter(user__groups__name='CUSTOMER')
    return render(request,'insurance/admin_view_customer.html',{'customers':customers})


@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    customer = CMODEL.Customer.objects.get(id=pk)
    user = CMODEL.User.objects.get(id=customer.user_id)

    if request.method == 'POST':
        userForm = CFORM.CustomerUserForm(request.POST, instance=user)
        customerForm = CFORM.CustomerForm(request.POST, request.FILES, instance=customer)

        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save(commit=False)

            # Check if password is present in the form
            if 'password' in request.POST:
                user.set_password(userForm.cleaned_data['password'])
            user.save()

            # Check if profile_pic is empty in the form data
            if not request.FILES.get('profile_pic'):
                # If empty, set profile_pic to the current value from the database
                customerForm.instance.profile_pic = customer.profile_pic

            # Save the customer form
            customerForm.save()

            return redirect('admin-view-customer')
    else:
        userForm = CFORM.CustomerUserForm(instance=user)
        customerForm = CFORM.CustomerForm(instance=customer)
        
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    return render(request, 'insurance/update_customer.html', context=mydict)


@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=CMODEL.Customer.objects.get(id=pk)
    user=User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
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

def admin_add_policy_view(request):
    policyForm = PolicyForm()
    if request.method == 'POST':
        policyForm = PolicyForm(request.POST)
        if policyForm.is_valid():
            id_number = request.POST.get('id_number')  # Get the ID number from the form
            category_id = request.POST.get('category')
            category = Category.objects.get(id=category_id)

            # Get the existing Customer based on the provided ID number
            try:
                customer = Customer.objects.get(id_number=id_number)
            except Customer.DoesNotExist:
                # Handle the case where the customer with the provided ID number doesn't exist
                # display an error message or take appropriate action
                return render(request, 'insurance/error_template.html', {'error_message': 'Customer not found'})

            policy = policyForm.save(commit=False)
            policy.category = category
            policy.insured = customer  # Link the policy to the Customer
            
            policy.cover_start = policyForm.cleaned_data['cover_start']
            policy.tenure = policyForm.cleaned_data['tenure']

            # Calculate and set cover_end based on cover_start and tenure
            if policy.cover_start and policy.tenure:
                policy.cover_end = add_months(policy.cover_start, policy.tenure)
                
            # Save the policy to get the auto-generated policy_number
            policy.save()
            
            print("Policy Number:", policy.policy_number)
            print("Cover End:", policy.cover_end)

            return redirect('admin-view-policy')

    return render(request, 'insurance/admin_add_policy.html', {'policyForm': policyForm})

def get_user_details_view(request, id_number):
    if request.method == 'GET':
        try:
            customer = models.Customer.objects.get(id_number=id_number)
            user_details = {
                'name': customer.user.get_full_name(),
                'address': customer.address,
                'mobile': customer.mobile,
                'profile_pic': str(customer.profile_pic),
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
    policyrecords = models.PolicyRecord.objects.all()
    return render(request,'insurance/admin_view_policy_holder.html',{'policyrecords':policyrecords})

def admin_view_approved_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Approved')
    return render(request,'insurance/admin_view_approved_policy_holder.html',{'policyrecords':policyrecords})

def admin_view_disapproved_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Disapproved')
    return render(request,'insurance/admin_view_disapproved_policy_holder.html',{'policyrecords':policyrecords})

def admin_view_waiting_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Pending')
    return render(request,'insurance/admin_view_waiting_policy_holder.html',{'policyrecords':policyrecords})

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


def admin_question_view(request):
    questions = models.Question.objects.all()
    return render(request,'insurance/admin_question.html',{'questions':questions})

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

