
from django.contrib import admin
from insurance import views
from django.contrib.auth.views import LogoutView,LoginView
from django.urls import path,include
from insurance.views import custom_dashboard, logout_redirect

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('customer/',include('customer.urls')),
    
    path('',views.home_view,name='home'),
    path('logout/', LogoutView.as_view(template_name='insurance/logout.html'), name='logout'),
    path('logout-redirect/', views.logout_redirect, name='logout_redirect'),
    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),
    
    path('adminlogin', LoginView.as_view(template_name='insurance/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),
    path('custom_dashboard/', custom_dashboard, name='custom_dashboard'),

    path('admin-view-customer', views.admin_view_customer_view,name='admin-view-customer'),
    path('update-customer/<int:pk>', views.update_customer_view,name='update-customer'),
    path('delete-customer/<int:pk>', views.delete_customer_view,name='delete-customer'),
    
    

    path('admin-category', views.admin_category_view,name='admin-category'),
    path('admin-view-category', views.admin_view_category_view,name='admin-view-category'),
    path('admin-update-category', views.admin_update_category_view,name='admin-update-category'),
    path('update-category/<int:pk>', views.update_category_view,name='update-category'),
    path('admin-add-category', views.admin_add_category_view,name='admin-add-category'),
    path('admin-delete-category', views.admin_delete_category_view,name='admin-delete-category'),
    path('delete-category/<int:pk>', views.delete_category_view,name='delete-category'),


    path('admin-policy', views.admin_policy_view,name='admin-policy'),
    path('admin-add-policy', views.admin_add_policy_view,name='admin-add-policy'),
    path('admin-add-thirdparty-policy', views.admin_apply_thirdparty_view,name='admin-add-thirdparty-policy'),
    path('admin-get-user/<str:id_number>/', views.get_user_details_view,name='admin-get-user'),
    path('admin-view-policy', views.admin_view_policy_view,name='admin-view-policy'),
    path('admin-view-thirdpartypolicy', views.admin_view_thirdpartypolicy_view,name='admin-view-thirdpartypolicy'),
    path('admin-view-thirdpartypolicy', views.admin_view_thirdpartypolicy_view,name='admin-view-thirdpartypolicy'),
    path('admin-update-policy', views.admin_update_policy_view,name='admin-update-policy'),
    path('update-policy/<int:pk>', views.update_policy_view,name='update-policy'),
    path('admin-delete-policy', views.admin_delete_policy_view,name='admin-delete-policy'),
    path('delete-policy/<int:pk>', views.delete_policy_view,name='delete-policy'),

    path('admin-view-policy-holder', views.admin_view_policy_holder_view,name='admin-view-policy-holder'),
    path('admin-view-thirdpartypolicy-holder', views.admin_view_thirdpartypolicy_holder_view,name='admin-view-thirdpartypolicy-holder'),
    path('admin-view-approved-policy-holder', views.admin_view_approved_policy_holder_view,name='admin-view-approved-policy-holder'),
    path('admin-view-disapproved-policy-holder', views.admin_view_disapproved_policy_holder_view,name='admin-view-disapproved-policy-holder'),
    path('admin-view-waiting-policy-holder', views.admin_view_waiting_policy_holder_view,name='admin-view-waiting-policy-holder'),
    path('admin-view-approved-thirdpartypolicy-holder', views.admin_view_approved_thirdpartypolicy_holder_view,name='admin-view-approved-thirdpartypolicy-holder'),
    path('admin-view-disapproved-thirdpartypolicy-holder', views.admin_view_disapproved_thirdpartypolicy_holder_view,name='admin-view-disapproved-thirdpartypolicy-holder'),
    path('admin-view-waiting-thirdpartypolicy-holder', views.admin_view_waiting_thirdpartypolicy_holder_view,name='admin-view-waiting-thirdpartypolicy-holder'),
    path('approve-request/<int:pk>', views.approve_request_view,name='approve-request'),
    path('reject-request/<int:pk>', views.disapprove_request_view,name='reject-request'),
    path('approve-thirdpartyrequest/<int:pk>', views.approve_thirdpartyrequest_view,name='approve-thirdpartyrequest'),
    path('reject-thirdpartyrequest/<int:pk>', views.disapprove_thirdpartyrequest_view,name='reject-thirdpartyrequest'),

    path('admin-question', views.admin_question_view,name='admin-question'),
    path('admin-customerforms', views.admin_customerforms,name='admin_customerforms'),
    path('admin-homeownersview', views.admin_homeownersview,name='admin_homeownersview'),
    path('admin-thirdpartyview', views.admin_thirdpartyview,name='admin_thirdpartyview'),
    path('delete_selected', views.delete_selected, name='delete_selected'),
    
    path('update-question/<int:pk>', views.update_question_view,name='update-question'),
    #path('reset-password/', auth_views.PasswordResetView.as_view(), name='reset-password'),

]

# Serve static files from Google Cloud Storage in production
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
