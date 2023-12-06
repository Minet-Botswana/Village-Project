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
    return redirect('history')

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
            return redirect('question-history')
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

    # Fetch user-specific form instances for each form type
    kyc_forms = models.KYCForm.objects.filter(customer=customer)


    # Initialize form instances for each form type (for uploading)
    kyc_form = forms.KYCFormModelForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'kyc':
            form = forms.KYCFormModelForm(request.POST, request.FILES)
            if form.is_valid():
                kyc_form_instance = form.save(commit=False)
                kyc_form_instance.customer = customer
                kyc_form_instance.save()
                messages.success(request, 'KYC Form submitted successfully.')
                return redirect('client_forms')
            
    context = {
        'kyc_forms': kyc_forms,}


    return render(request, 'customer/client_forms.html', context)


def direct_debit_view(request):
    return render(request, 'customer/direct_debit.html')

def homeowners_insurance_view(request):
    return render(request, 'customer/homeowners_insurance.html')

def motor_insurance_view(request):
    return render(request, 'customer/motor_insurance.html')

def create_homeowners_cover(request):
    if request.method == 'POST':
        form = forms.HomeownersCoverForm(request.POST, request.FILES)
        if form.is_valid():
            homeowners_cover = form.save(commit=False)
            homeowners_cover.customer = request.user
            homeowners_cover.save()
            return redirect('success_page')  # Redirect to a success page
    else:
        form = forms.HomeownersCoverForm()

    return render(request, 'customer/homeowners_insurance.html', {'form': form})

