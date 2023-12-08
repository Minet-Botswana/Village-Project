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


def customerclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'customer/customerclick.html')


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

def apply_policy_view(request):
    # Assuming the user is logged in
    customer = models.Customer.objects.get(user_id=request.user.id)
    # Filter policies based on the customer's id_number
    policies = Policy.objects.filter(insured__id_number=customer.id_number)
    print("Number of policies:", policies.count())  # Debug statement

    return render(request, 'customer/apply_policy.html', {'policies': policies, 'customer': customer})

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

    return render(request, 'customer/homeowners_insurance.html', context=homeownersdict)


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


from .forms import KYCuploadForm
def upload_kyc_form(request):
    KYC_Form = KYCuploadForm()
    KYCdict = {'KYC_Form': KYC_Form}

    if request.method == 'POST':
        KYC_Form = KYCuploadForm(request.POST, request.FILES)

        if KYC_Form.is_valid():
            kyc_cover = KYC_Form.save(commit=False)

            # Assuming there is a one-to-one relationship between User and Customer
            user_instance = request.user
            customer_instance = get_object_or_404(models.Customer, user=user_instance)

            kyc_cover.customer = customer_instance
            kyc_cover.save()

            print("Form data:", request.POST)  # Debugging line
            print("Saved KYC Uploads:", kyc_cover.__dict__)  # Debugging line

        else:
            print(KYC_Form.errors)  # Print form errors for debugging

    return render(request, 'customer/client_forms.html', context=KYCdict)

