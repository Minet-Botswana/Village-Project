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
    thirdpartypolicy = ThirdpartyPolicy.objects.filter(insured__id_number=customer.id_number)
    dict={
        'customer':models.Customer.objects.get(user_id=request.user.id),
        'available_policy':CMODEL.Policy.objects.all().count(),
        'applied_policy':CMODEL.PolicyRecord.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        'total_category':CMODEL.Category.objects.all().count(),
        'total_question':CMODEL.Question.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        'policies': policies,
        'thirdpartypolicy':thirdpartypolicy,
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

from insurance.models import ThirdpartyPolicy

def available_thirdpartypolicy_view(request):
    # Assuming the user is logged in
    customer = models.Customer.objects.get(user_id=request.user.id)
    # Filter policies based on the customer's id_number
    policies = ThirdpartyPolicy.objects.filter(insured__id_number=customer.id_number)
    print("Number of policies:", policies.count())  # Debug statement

    return render(request, 'customer/available_thirdpartypolicies.html', {'policies': policies, 'customer': customer})

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

from insurance.forms import PolicyForm, ThirdpartyPolicyForm
from insurance.models import Category

def apply_thirdparty_view(request):
    thirdpartypolicyForm = ThirdpartyPolicyForm()
    print("Request method:", request.method)
    if request.method == 'POST':
        thirdpartypolicyForm = ThirdpartyPolicyForm(request.POST)
        print("Policy Form:", thirdpartypolicyForm)
        if thirdpartypolicyForm.is_valid():
            print("Form is valid")
            
            # Check for form validation errors
            if not thirdpartypolicyForm.is_valid():
               print("Form errors:", thirdpartypolicyForm.errors)
               # Here you can render the form again with errors if you want
               return render(request, 'customer/apply_thirdparty.html', {'thirdpartypolicyForm': thirdpartypolicyForm})
        
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
            messages.success(request, "Cover created Successfully!")
            print("Policy successfully saved!")
            print("Policy Number:", policy.policy_number)
            print("Cover End:", policy.cover_end)

            return redirect('customer:available-policies')

    return render(request, 'customer/apply_thirdparty.html', {'thirdpartypolicyForm': thirdpartypolicyForm})

from datetime import timedelta

def apply_policy_view(request):
    policyForm = PolicyForm()
    print("Request method:", request.method)
    if request.method == 'POST':
        policyForm = PolicyForm(request.POST)
        if policyForm.is_valid():
            id_number = request.POST.get('id_number')
            category_id = request.POST.get('category')
            category = Category.objects.get(id=category_id)
            try:
                customer = models.Customer.objects.get(id_number=id_number)
            except models.Customer.DoesNotExist:
                return render(request, 'insurance/error_template.html', {'error_message': 'Customer not found'})

            policy = policyForm.save(commit=False)
            policy.category = category
            policy.insured = customer
            policy.cover_start = policyForm.cleaned_data['cover_start']
            policy.tenure = policyForm.cleaned_data['tenure']
            policy.cover_end = add_months(policy.cover_start, policy.tenure)

            # Save the policy
            policy.save()
            messages.success(request, "Cover created Successfully!")
            return redirect('customer:available-policies')

    return render(request, 'customer/apply_policy.html', {'policyForm': policyForm})

'''
def apply_view(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = CMODEL.Policy.objects.get(id=pk)
    policyrecord = CMODEL.PolicyRecord()
    policyrecord.Policy = policy
    policyrecord.customer = customer
    policyrecord.save()
    return redirect('customer:history')
'''
def apply_view(request, pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = CMODEL.Policy.objects.get(id=pk)
    policyrecord = CMODEL.PolicyRecord()
    policyrecord.Policy = policy
    policyrecord.customer = customer
    policyrecord.save()
    return redirect('customer:history')



def thirdpartyapply_view(request,pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = CMODEL.ThirdpartyPolicy.objects.get(id=pk)
    policyrecord = CMODEL.ThirdpartyPolicyRecord()
    policyrecord.thirdpartypolicy = policy
    policyrecord.thirdpartycustomer = customer
    policyrecord.save()
    return redirect('customer:thirdpartyhistory')

def history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.PolicyRecord.objects.all().filter(customer=customer)
    return render(request,'customer/history.html',{'policies':policies,'customer':customer})

def thirdpartyhistory_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.ThirdpartyPolicyRecord.objects.filter(thirdpartycustomer=customer)
    return render(request,'customer/thirdpartyhistory.html',{'policies':policies,'customer':customer})

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

@login_required
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
            return redirect('customer:display_user_homeowners_covers')
        
            print("Form data:", request.POST)  # Debugging line
            print("Saved homeowners_cover:", homeowners_cover.__dict__)  # Debugging line

        else:
            print(homeownersForm.errors)  # Print form errors for debugging
            messages.error(request, 'Please correct the errors in the form.')

    return render(request, 'customer/homeowners_insurance.html', context=homeownersdict)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import HomeownersCover, ThirdPartyCarInsurance

@login_required
def display_user_homeowners_covers(request):
    homeowners_covers = HomeownersCover.objects.filter(customer__user=request.user)
    return render(request, 'customer/update_homeowners_cover.html', {'homeowners_covers': homeowners_covers})

@login_required
def display_user_thirdparty_covers(request):
    thirdparty_covers = ThirdPartyCarInsurance.objects.filter(customer__user=request.user)
    return render(request, 'customer/update_thirdparty_cover.html', {'thirdparty_covers': thirdparty_covers})


from .forms import ThirdPartyCarInsuranceForm
from django.shortcuts import get_object_or_404

@login_required
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
            return redirect('customer:display_user_thirdparty_covers')


        else:
            print(thirdpartycarForm.errors)  # Print form errors for debugging

    return render(request, 'customer/motor_insurance.html', context=thirdpartycardict)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import KYCuploadForm, CopyOfOmangForm, ResidenceProofForm, IncomeProofForm
from .models import KYCform, Customer, CopyOfOmang, ResidenceProof, IncomeProof
@login_required
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
@login_required
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
    
#Proof of Residence Proof
@login_required
def upload_residence_proof(request):
    user = request.user
    customer = get_object_or_404(Customer, user=user)

    # Check if a KYCform instance exists for the current customer
    existing_residence_proof =  ResidenceProof.objects.filter(customer=customer).first()

    if existing_residence_proof:
        # KYC form has already been submitted
        submit_button_disabled = True
        submit_button_text = 'Form Submitted'
    else:
        submit_button_disabled = False
        submit_button_text = 'Submit Form'

    if request.method == 'POST':
        form = ResidenceProofForm(request.POST, request.FILES)
        if form.is_valid():
            if not existing_residence_proof:
                # Save the form data to the database only if a form hasn't been submitted already
                residence_proof_instance = form.save(commit=False)
                residence_proof_instance.customer = customer
                form_file = request.FILES['residence_proof']
                filename = form_file.name
                form_file_url = ResidenceProof.upload_form(form_file, filename)

                if form_file_url:
                    residence_proof_instance.residence_proof = form_file_url
                    residence_proof_instance.save()

                    messages.success(request, 'residence_proof uploaded successfully!')
                    return redirect('customer:upload_residence_proof')
                else:
                    messages.error(request, 'Failed to upload residence_proof to Google Cloud Storage.')

    else:
        form = ResidenceProofForm()

    return render(request, 'customer/client_forms.html', {
        'form': form,
        'submit_button_disabled': submit_button_disabled,
        'submit_button_text': submit_button_text,
        'existing_residence_proof': existing_residence_proof,
    })

@login_required
def upload_income_proof(request):
    user = request.user
    customer = get_object_or_404(Customer, user=user)

    # Check if a KYCform instance exists for the current customer
    existing_income_proof =  IncomeProof.objects.filter(customer=customer).first()

    if existing_income_proof:
        # KYC form has already been submitted
        submit_button_disabled = True
        submit_button_text = 'Form Submitted'
    else:
        submit_button_disabled = False
        submit_button_text = 'Submit Form'

    if request.method == 'POST':
        form = IncomeProofForm(request.POST, request.FILES)
        if form.is_valid():
            if not existing_income_proof:
                # Save the form data to the database only if a form hasn't been submitted already
                income_proof_instance = form.save(commit=False)
                income_proof_instance.customer = customer
                form_file = request.FILES['income_proof']
                filename = form_file.name
                form_file_url = IncomeProof.upload_form(form_file, filename)

                if form_file_url:
                    income_proof_instance.income_proof = form_file_url
                    income_proof_instance.save()

                    messages.success(request, 'income_proof uploaded successfully!')
                    return redirect('customer:upload_income_proof')
                else:
                    messages.error(request, 'Failed to upload income_proof to Google Cloud Storage.')

    else:
        form = IncomeProofForm()

    return render(request, 'customer/client_forms.html', {
        'form': form,
        'submit_button_disabled': submit_button_disabled,
        'submit_button_text': submit_button_text,
        'existing_income_proof': existing_income_proof,
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import HomeownersCover
from .forms import HomeownersCoverForm
from django.contrib.auth.decorators import login_required

@login_required
def update_homeowners_cover(request, id):
    homeowners_cover = get_object_or_404(HomeownersCover, id=id)

    if request.method == 'POST':
        form = HomeownersCoverForm(request.POST, request.FILES, instance=homeowners_cover)
        if form.is_valid():
            # Save the form to get the updated title_deed URL
            updated_cover = form.save(commit=False)

            # Check if a new title_deed file is provided
            if 'title_deed' in request.FILES:
                file = request.FILES['title_deed']
                # Upload title_deed to Google Cloud Storage or other storage
                public_url = HomeownersCover.upload_form(file, file.name)
                # Set the title_deed field to the storage URL
                updated_cover.title_deed.name = public_url

            # Save the updated cover with the new title_deed URL
            updated_cover.save()

            # Redirect to a success page or display a success message
            return redirect('customer:display_user_homeowners_covers')
    else:
        form = HomeownersCoverForm(instance=homeowners_cover)

    return render(request, 'customer/update_homeowners_cover.html', {'form': form, 'homeowners_cover': homeowners_cover})

@login_required
def update_thirdparty_cover(request, id):
    thirdparty_cover = get_object_or_404(ThirdPartyCarInsurance, id=id)

    if request.method == 'POST':
        form = ThirdPartyCarInsuranceForm(request.POST, request.FILES, instance=thirdparty_cover)
        if form.is_valid():
            # Save the form to get the updated blue_book URL
            updated_cover = form.save(commit=False)

            # Check if a new blue_book file is provided
            if 'blue_book' in request.FILES:
                file = request.FILES['blue_book']
                # Upload blue_book to Google Cloud Storage or other storage
                public_url = ThirdPartyCarInsurance.upload_form(file, file.name)
                # Set the blue_book field to the storage URL
                updated_cover.blue_book.name = public_url

                # Save the updated cover with the new blue_book URL
                updated_cover.save()
                print("Updated Cover Data:", updated_cover.__dict__)

                # Redirect to a success page or display a success message 
                return redirect('customer:display_user_thirdparty_covers')
    else:
        form = ThirdPartyCarInsuranceForm(instance=thirdparty_cover)

    return render(request, 'customer/update_thirdparty_cover.html', {'form': form, 'thirdparty_cover': thirdparty_cover})


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('customerlogin')  # Redirect to the login page or another appropriate page
