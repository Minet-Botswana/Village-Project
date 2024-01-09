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
from insurance import models as CMODEL
from insurance import forms as CFORM
from django.contrib.auth.models import User
from insurance.models import Policy
from django.views import View
from django.template.loader import get_template
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import timedelta, date
import calendar


def customerclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'customer/customerclick.html')

''''
def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'customer/customersignup.html',context=mydict)
'''
def customer_signup_view(request):
    user_form = forms.CustomerUserForm()
    customer_form = forms.CustomerForm()
    mydict = {'userForm': user_form, 'customerForm': customer_form}

    if request.method == 'POST':
        user_form = forms.CustomerUserForm(request.POST)
        customer_form = forms.CustomerForm(request.POST, request.FILES)

        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            customer = customer_form.save(commit=False)
            customer.user = user

            # Upload profile picture
            profile_pic = request.FILES.get('profile_pic')
            if profile_pic:
                pro_pic_url = models.Customer.upload_image(profile_pic, profile_pic.name)
                customer.profile_pic = pro_pic_url

            customer.save()

            # Add user to CUSTOMER group
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)

            return HttpResponseRedirect('customerlogin')

    return render(request, 'customer/customersignup.html', context=mydict)


def success_page(request):
    return render(request, 'customer/success_page.html')  # Use the actual template path


def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()

@login_required(login_url='customerlogin')
def customer_dashboard_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = Policy.objects.filter(insured__id_number=customer.id_number)
    dict={
        'customer':models.Customer.objects.get(user_id=request.user.id),
        'available_policy':CMODEL.Policy.objects.all().count(),
        'applied_policy':CMODEL.PolicyRecord.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        'total_category':CMODEL.Category.objects.all().count(),
        'total_question':CMODEL.Question.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        'policies': policies,
    }
    return render(request,'customer/customer_dashboard.html',context=dict)

#def apply_policy_view(request):
    #customer = models.Customer.objects.get(user_id=request.user.id)
    #policies = CMODEL.Policy.objects.all()
    #return render(request,'customer/apply_policy.html',{'policies':policies,'customer':customer})

def available_policy_view(request):
    # Assuming the user is logged in
    customer = models.Customer.objects.get(user_id=request.user.id)
    # Filter policies based on the customer's id_number
    policies = Policy.objects.filter(insured__id_number=customer.id_number)
    print("Number of policies:", policies.count())  # Debug statement

    return render(request, 'customer/available_policies.html', {'policies': policies, 'customer': customer})

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

from insurance.forms import PolicyForm
from insurance.models import Category

def apply_policy_view(request):
    policyForm = PolicyForm()
    if request.method == 'POST':
        policyForm = PolicyForm(request.POST)
        if policyForm.is_valid():
            id_number = request.POST.get('id_number')  # Get the ID number from the form
            category_id = request.POST.get('category')
            category = Category.objects.get(id=category_id)

            # Get the existing Customer based on the provided ID number
            try:
                customer = models.Customer.objects.get(id_number=id_number)
            except models.Customer.DoesNotExist:
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

            return redirect('available-policies')

    return render(request, 'customer/apply_policy.html', {'policyForm': policyForm})

def apply_view(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = CMODEL.Policy.objects.get(id=pk)
    policyrecord = CMODEL.PolicyRecord()
    policyrecord.Policy = policy
    policyrecord.customer = customer
    policyrecord.save()
    return redirect('customer:history')

def history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.PolicyRecord.objects.all().filter(customer=customer)
    return render(request,'customer/history.html',{'policies':policies,'customer':customer})

def ask_question_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    questionForm=CFORM.QuestionForm() 
    
    if request.method=='POST':
        questionForm=CFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            
            question = questionForm.save(commit=False)
            question.customer=customer
            question.save()
            return redirect('customer:question-history')
    return render(request,'customer/ask_question.html',{'questionForm':questionForm,'customer':customer})

def question_history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    questions = CMODEL.Question.objects.all().filter(customer=customer)
    return render(request,'customer/question_history.html',{'questions':questions,'customer':customer})

#################### VIEWS FOR FORMS #########################################
from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
def client_forms(request):
    user = request.user
    customer = user.customer
    return render(request, 'customer/client_forms.html')


def direct_debit_view(request):
    return render(request, 'customer/direct_debit.html')

def homeowners_insurance_view(request):
    return render(request, 'customer/homeowners_insurance.html')

def motor_insurance_view(request):
    return render(request, 'customer/motor_insurance.html')

from .forms import HomeownersCoverForm
from django.shortcuts import get_object_or_404
from django.contrib import messages

def create_homeowners_cover(request):
    homeownersForm = HomeownersCoverForm()
    homeownersdict = {'homeownersForm': homeownersForm}

    if request.method == 'POST':
        homeownersForm = HomeownersCoverForm(request.POST, request.FILES)

        if homeownersForm.is_valid():
            homeowners_cover = homeownersForm.save(commit=False)

            # Assuming there is a one-to-one relationship between User and Customer
            user_instance = request.user
            customer_instance = get_object_or_404(models.Customer, user=user_instance)

            homeowners_cover.customer = customer_instance
            homeowners_cover.save()

            print("Form data:", request.POST)  # Debugging line
            print("Saved homeowners_cover:", homeowners_cover.__dict__)  # Debugging line

        else:
            print(homeownersForm.errors)  # Print form errors for debugging
            messages.error(request, 'Please correct the errors in the form.')

    return render(request, 'customer/homeowners_insurance.html', context=homeownersdict)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import HomeownersCover

@login_required
def display_user_homeowners_covers(request):
    homeowners_covers = HomeownersCover.objects.filter(customer__user=request.user)
    return render(request, 'customer/update_homeowners_cover.html', {'homeowners_covers': homeowners_covers})





from .forms import ThirdPartyCarInsuranceForm
from django.shortcuts import get_object_or_404

def create_thirdpartycar_cover(request):
    thirdpartycarForm = ThirdPartyCarInsuranceForm()
    thirdpartycardict = {'thirdpartycarForm': thirdpartycarForm}

    if request.method == 'POST':
        thirdpartycarForm = ThirdPartyCarInsuranceForm(request.POST, request.FILES)

        if thirdpartycarForm.is_valid():
            thirdpartycar_cover = thirdpartycarForm.save(commit=False)

            # Assuming there is a one-to-one relationship between User and Customer
            user_instance = request.user
            customer_instance = get_object_or_404(models.Customer, user=user_instance)

            thirdpartycar_cover.customer = customer_instance
            thirdpartycar_cover.save()

            print("Form data:", request.POST)  # Debugging line
            print("Saved thirdpartycar_cover:", thirdpartycar_cover.__dict__)  # Debugging line

        else:
            print(thirdpartycarForm.errors)  # Print form errors for debugging

    return render(request, 'customer/motor_insurance.html', context=thirdpartycardict)

'''
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import KYCuploadForm
from .models import KYCform, Customer

def upload_kyc_form(request):
    if request.method == 'POST':
        form = KYCuploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Ensure the user is authenticated
            if request.user.is_authenticated:
                # Get or create the associated Customer instance for the user
                customer, created = Customer.objects.get_or_create(user=request.user)

                # Save the form data to the database
                kyc_instance = form.save(commit=False)
                kyc_instance.customer = customer  # Associate the KYC form with the Customer

                # Upload the form to Google Cloud Storage
                form_file = request.FILES['kyc_form']
                filename = form_file.name
                form_file_url = KYCform.upload_form(form_file, filename)

                if form_file_url:
                    # Save the Google Cloud Storage URL to the model instance
                    kyc_instance.kyc_form = form_file_url
                    kyc_instance.save()

                    messages.success(request, 'KYC form uploaded successfully!')
                    return redirect('customer:upload_kyc_form')

                else:
                    messages.error(request, 'Failed to upload KYC form.')
            else:
                messages.error(request, 'User is not authenticated.')

        else:
            messages.error(request, 'Form submission failed. Please check the form data.')

    else:
        form = KYCuploadForm()

    return render(request, 'customer/client_forms.html', {'form': form})
'''
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import KYCuploadForm, CopyOfOmangForm
from .models import KYCform, Customer, CopyOfOmang

def upload_kyc_form(request):
    user = request.user
    customer = get_object_or_404(Customer, user=user)

    # Check if a KYCform instance exists for the current customer
    existing_kyc_form = KYCform.objects.filter(customer=customer).first()

    if existing_kyc_form:
        # KYC form has already been submitted
        submit_button_disabled = True
        submit_button_text = 'Form Submitted'
    else:
        submit_button_disabled = False
        submit_button_text = 'Submit Form'

    if request.method == 'POST':
        form = KYCuploadForm(request.POST, request.FILES)
        if form.is_valid():
            if not existing_kyc_form:
                # Save the form data to the database only if a form hasn't been submitted already
                kyc_instance = form.save(commit=False)
                kyc_instance.customer = customer
                form_file = request.FILES['kyc_form']
                filename = form_file.name
                form_file_url = KYCform.upload_form(form_file, filename)

                if form_file_url:
                    kyc_instance.kyc_form = form_file_url
                    kyc_instance.save()

                    messages.success(request, 'KYC form uploaded successfully!')
                    return redirect('customer:upload_kyc_form')
                else:
                    messages.error(request, 'Failed to upload KYC form to Google Cloud Storage.')

    else:
        form = KYCuploadForm()

    return render(request, 'customer/client_forms.html', {
        'form': form,
        'submit_button_disabled': submit_button_disabled,
        'submit_button_text': submit_button_text,
        'existing_kyc_form': existing_kyc_form,
    })
    
#Omang View
def upload_copy_of_omang(request):
    user = request.user
    customer = get_object_or_404(Customer, user=user)

    # Check if a KYCform instance exists for the current customer
    existing_copy_of_omang =  CopyOfOmang.objects.filter(customer=customer).first()

    if existing_copy_of_omang:
        # KYC form has already been submitted
        submit_button_disabled = True
        submit_button_text = 'Form Submitted'
    else:
        submit_button_disabled = False
        submit_button_text = 'Submit Form'

    if request.method == 'POST':
        form = CopyOfOmangForm(request.POST, request.FILES)
        if form.is_valid():
            if not existing_copy_of_omang:
                # Save the form data to the database only if a form hasn't been submitted already
                copy_of_omang_instance = form.save(commit=False)
                copy_of_omang_instance.customer = customer
                form_file = request.FILES['copy_of_omang']
                filename = form_file.name
                form_file_url = CopyOfOmang.upload_form(form_file, filename)

                if form_file_url:
                    copy_of_omang_instance.copy_of_omang = form_file_url
                    copy_of_omang_instance.save()

                    messages.success(request, 'Omang File uploaded successfully!')
                    return redirect('customer:upload_copy_of_omang')
                else:
                    messages.error(request, 'Failed to upload Omang File to Google Cloud Storage.')

    else:
        form = CopyOfOmangForm()

    return render(request, 'customer/client_forms.html', {
        'form': form,
        'submit_button_disabled': submit_button_disabled,
        'submit_button_text': submit_button_text,
        'existing_copy_of_omang': existing_copy_of_omang,
    })

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import HomeownersCover
from .forms import HomeownersCoverForm  # Assuming you have a form for your model

def update_homeowners_cover(request, cover_id):
    homeowners_cover = get_object_or_404(HomeownersCover, id=cover_id)

    if request.method == 'POST':
        form = HomeownersCoverForm(request.POST, instance=homeowners_cover)
        if form.is_valid():
            form.save()
            # Redirect to a success page or display a success message
            return redirect('success_page')  # Replace 'success_page' with the actual URL name
    else:
        form = HomeownersCoverForm(instance=homeowners_cover)

    return render(request, 'customer/update_homeowners_cover.html', {'form': form, 'homeowners_cover': homeowners_cover})


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('customerlogin')  # Redirect to the login page or another appropriate page
