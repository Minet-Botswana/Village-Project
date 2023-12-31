from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from .views import client_forms
from .views import update_homeowners_cover

app_name = 'customer'

urlpatterns = [
    path('customerclick', views.customerclick_view,name='customerclick'),
    path('customersignup', views.customer_signup_view,name='customersignup'),
    path('customer-dashboard', views.customer_dashboard_view,name='customer-dashboard'),
    path('customerlogin', LoginView.as_view(template_name='insurance/adminlogin.html'),name='customerlogin'),

    path('available-policies', views.available_policy_view,name='available-policies'),
    path('apply-policy', views.apply_policy_view,name='apply-policy'),
    path('apply/<int:pk>', views.apply_view,name='apply'),
    path('history', views.history_view,name='history'),

    path('ask-question', views.ask_question_view,name='ask-question'),
    path('question-history', views.question_history_view,name='question-history'),
    path('forms', views.client_forms, name='client_forms'),
    path('customer/forms/', client_forms, name='client_forms'),
    
    path('form/direct_debit.html/', views.direct_debit_view, name='direct_debit'),
    path('form/homeowners_insurance.html/', views.homeowners_insurance_view, name='homeowners_insurance'),
    path('forms/motor_insurance.html/', views.motor_insurance_view, name='motor_insurance'),
    path('customer/success/', views.success_page, name='success_page'),
    
    path('customer/create_homeowners_cover/', views.create_homeowners_cover, name='create_homeowners_cover'),
    path('customer/create_thirdpartycar_cover/', views.create_thirdpartycar_cover, name='create_thirdpartycar_cover'),
    path('customer/upload_kyc_form/', views.upload_kyc_form, name='upload_kyc_form'),
    
    # Example URL pattern in urls.py with namespace
    path('display_user_homeowners_covers/', views.display_user_homeowners_covers, name='display_user_homeowners_covers'),
    path('update_homeowners_cover/<int:id>/', views.update_homeowners_cover, name='update_homeowners_cover'),

]