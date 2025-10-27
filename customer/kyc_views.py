"""
KYC Compliance Monitoring Views
Handles KYC status tracking, approval, rejection, and renewal notifications
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Customer, KYCform, CopyOfOmang, ResidenceProof, IncomeProof
from datetime import timedelta


def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_kyc_compliance_dashboard(request):
    """
    Admin dashboard showing all customers' KYC compliance status
    with filtering and bulk actions
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    customers = Customer.objects.select_related('user', 'kyc_reviewed_by').all()
    
    # Apply status filter
    if status_filter != 'all':
        customers = customers.filter(kyc_status=status_filter)
    
    # Apply search filter
    if search_query:
        customers = customers.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(id_number__icontains=search_query) |
            Q(mobile__icontains=search_query)
        )
    
    # Calculate statistics
    total_customers = Customer.objects.count()
    compliant_count = Customer.objects.filter(kyc_status='Compliant').count()
    pending_count = Customer.objects.filter(kyc_status='Pending').count()
    non_compliant_count = Customer.objects.filter(kyc_status='Non-Compliant').count()
    renewal_required_count = Customer.objects.filter(kyc_status='Renewal Required').count()
    
    # Get customers with expiring KYC (within 30 days)
    thirty_days_from_now = timezone.now().date() + timedelta(days=30)
    expiring_soon = Customer.objects.filter(
        kyc_status='Compliant',
        kyc_expiry_date__lte=thirty_days_from_now,
        kyc_expiry_date__gte=timezone.now().date()
    ).count()
    
    # Get expired KYC
    expired_count = Customer.objects.filter(
        kyc_expiry_date__lt=timezone.now().date()
    ).count()
    
    context = {
        'customers': customers,
        'total_customers': total_customers,
        'compliant_count': compliant_count,
        'pending_count': pending_count,
        'non_compliant_count': non_compliant_count,
        'renewal_required_count': renewal_required_count,
        'expiring_soon': expiring_soon,
        'expired_count': expired_count,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'customer/admin_kyc_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_kyc_customer_detail(request, customer_id):
    """
    Detailed view of a specific customer's KYC information
    Shows all uploaded documents and compliance history
    """
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Get all KYC documents
    kyc_form = KYCform.objects.filter(customer=customer).first()
    omang_copy = CopyOfOmang.objects.filter(customer=customer).first()
    residence_proof = ResidenceProof.objects.filter(customer=customer).first()
    income_proof = IncomeProof.objects.filter(customer=customer).first()
    
    # Calculate document completeness
    documents_submitted = sum([
        bool(kyc_form and kyc_form.kyc_form),
        bool(omang_copy and omang_copy.copy_of_omang),
        bool(residence_proof and residence_proof.residence_proof),
        bool(income_proof and income_proof.income_proof)
    ])
    total_documents = 4
    completeness_percentage = (documents_submitted / total_documents) * 100
    
    context = {
        'customer': customer,
        'kyc_form': kyc_form,
        'omang_copy': omang_copy,
        'residence_proof': residence_proof,
        'income_proof': income_proof,
        'documents_submitted': documents_submitted,
        'total_documents': total_documents,
        'completeness_percentage': completeness_percentage,
    }
    
    return render(request, 'customer/admin_kyc_customer_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_approve_kyc(request, customer_id):
    """
    Approve a customer's KYC with specified validity period
    """
    if request.method == 'POST':
        customer = get_object_or_404(Customer, id=customer_id)
        expiry_months = int(request.POST.get('expiry_months', 12))
        notes = request.POST.get('notes', '')
        
        customer.approve_kyc(
            reviewed_by=request.user,
            expiry_months=expiry_months,
            notes=notes
        )
        
        messages.success(request, f'KYC approved for {customer.get_name} (valid for {expiry_months} months)')
        return redirect('customer:admin-kyc-customer-detail', customer_id=customer_id)
    
    return redirect('customer:admin-kyc-dashboard')


@login_required
@user_passes_test(is_admin)
def admin_reject_kyc(request, customer_id):
    """
    Reject a customer's KYC with reason
    """
    if request.method == 'POST':
        customer = get_object_or_404(Customer, id=customer_id)
        reason = request.POST.get('reason', 'Document verification failed')
        
        customer.reject_kyc(
            reviewed_by=request.user,
            reason=reason
        )
        
        messages.warning(request, f'KYC rejected for {customer.get_name}')
        return redirect('customer:admin-kyc-customer-detail', customer_id=customer_id)
    
    return redirect('customer:admin-kyc-dashboard')


@login_required
@user_passes_test(is_admin)
def admin_mark_kyc_renewal(request, customer_id):
    """
    Mark a customer's KYC for renewal
    """
    customer = get_object_or_404(Customer, id=customer_id)
    customer.mark_kyc_for_renewal()
    
    messages.info(request, f'KYC marked for renewal for {customer.get_name}. Customer will be notified.')
    return redirect('customer:admin-kyc-customer-detail', customer_id=customer_id)


@login_required
def customer_kyc_status(request):
    """
    Customer-facing view showing their KYC status and documents
    with alerts for renewal or non-compliance
    """
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        messages.error(request, 'Customer profile not found')
        return redirect('customer:customerdashboard')
    
    # Get all KYC documents
    kyc_form = KYCform.objects.filter(customer=customer).first()
    omang_copy = CopyOfOmang.objects.filter(customer=customer).first()
    residence_proof = ResidenceProof.objects.filter(customer=customer).first()
    income_proof = IncomeProof.objects.filter(customer=customer).first()
    
    # Calculate document completeness
    documents_submitted = sum([
        bool(kyc_form and kyc_form.kyc_form),
        bool(omang_copy and omang_copy.copy_of_omang),
        bool(residence_proof and residence_proof.residence_proof),
        bool(income_proof and income_proof.income_proof)
    ])
    total_documents = 4
    completeness_percentage = (documents_submitted / total_documents) * 100
    
    # Determine if action is required
    action_required = customer.kyc_status in ['Pending', 'Non-Compliant', 'Renewal Required']
    show_renewal_alert = customer.kyc_expires_soon or customer.kyc_is_expired
    
    context = {
        'customer': customer,
        'kyc_form': kyc_form,
        'omang_copy': omang_copy,
        'residence_proof': residence_proof,
        'income_proof': income_proof,
        'documents_submitted': documents_submitted,
        'total_documents': total_documents,
        'completeness_percentage': completeness_percentage,
        'action_required': action_required,
        'show_renewal_alert': show_renewal_alert,
    }
    
    return render(request, 'customer/customer_kyc_status.html', context)


@login_required
@user_passes_test(is_admin)
def admin_bulk_kyc_action(request):
    """
    Handle bulk KYC actions (approve, reject, mark for renewal)
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        customer_ids = request.POST.getlist('customer_ids')
        
        if not customer_ids:
            messages.warning(request, 'No customers selected')
            return redirect('customer:admin-kyc-dashboard')
        
        customers = Customer.objects.filter(id__in=customer_ids)
        
        if action == 'approve':
            expiry_months = int(request.POST.get('expiry_months', 12))
            for customer in customers:
                customer.approve_kyc(
                    reviewed_by=request.user,
                    expiry_months=expiry_months,
                    notes=f'Bulk approved by {request.user.get_full_name()}'
                )
            messages.success(request, f'{customers.count()} customers approved')
        
        elif action == 'reject':
            reason = request.POST.get('reason', 'Bulk rejection - please review documents')
            for customer in customers:
                customer.reject_kyc(
                    reviewed_by=request.user,
                    reason=reason
                )
            messages.warning(request, f'{customers.count()} customers rejected')
        
        elif action == 'mark_renewal':
            for customer in customers:
                customer.mark_kyc_for_renewal()
            messages.info(request, f'{customers.count()} customers marked for renewal')
        
        return redirect('customer:admin-kyc-dashboard')
    
    return redirect('customer:admin-kyc-dashboard')


@login_required
@user_passes_test(is_admin)
def admin_kyc_statistics(request):
    """
    API endpoint returning KYC compliance statistics
    """
    stats = {
        'total': Customer.objects.count(),
        'compliant': Customer.objects.filter(kyc_status='Compliant').count(),
        'pending': Customer.objects.filter(kyc_status='Pending').count(),
        'non_compliant': Customer.objects.filter(kyc_status='Non-Compliant').count(),
        'renewal_required': Customer.objects.filter(kyc_status='Renewal Required').count(),
        'expiring_soon': Customer.objects.filter(
            kyc_status='Compliant',
            kyc_expiry_date__lte=timezone.now().date() + timedelta(days=30),
            kyc_expiry_date__gte=timezone.now().date()
        ).count(),
        'expired': Customer.objects.filter(
            kyc_expiry_date__lt=timezone.now().date()
        ).count(),
    }
    
    return JsonResponse(stats)
