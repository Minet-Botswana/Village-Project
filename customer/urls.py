from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from .views import client_forms

urlpatterns = [
    path('customerclick', views.customerclick_view,name='customerclick'),
    path('customersignup', views.customer_signup_view,name='customersignup'),
    path('customer-dashboard', views.customer_dashboard_view,name='customer-dashboard'),
    path('customerlogin', LoginView.as_view(template_name='insurance/adminlogin.html'),name='customerlogin'),

    path('apply-policy', views.apply_policy_view,name='apply-policy'),
    path('apply/<int:pk>', views.apply_view,name='apply'),
    path('history', views.history_view,name='history'),

    path('ask-question', views.ask_question_view,name='ask-question'),
    path('question-history', views.question_history_view,name='question-history'),
    path('forms', views.client_forms, name='client_forms'),
    path('customer/forms/', client_forms, name='client_forms'),
    
    path('form/direct_debit.html/', views.direct_debit_view, name='direct_debit'),
    path('form/homeowners_insurance.html/', views.homeowners_insurance_view, name='homeowners_insurance'),
    path('form/motor_insurance.html/', views.motor_insurance_view, name='motor_insurance'),
]