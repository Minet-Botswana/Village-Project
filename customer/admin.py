# app_name/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from django.utils import timezone
from .models import Customer, KYCform, DirectDebitForm, HomeownersCover, ThirdPartyCarInsurance, IncomeProof, ResidenceProof, CopyOfOmang

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'id_number', 'mobile', 'kyc_status_badge', 'kyc_expiry_info', 'kyc_days_until_expiry', 'occupation', 'gender', 'date_of_birth')
    list_filter = ('kyc_status', 'gender', 'marital_status', 'id_type')
    search_fields = ('user__first_name', 'user__last_name', 'id_number', 'mobile', 'occupation')
    readonly_fields = ('kyc_last_updated',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'id_type', 'id_number', 'gender', 'date_of_birth', 'marital_status')
        }),
        ('Contact Information', {
            'fields': ('mobile', 'alternate_phone', 'address', 'postal_address', 'physical_address')
        }),
        ('Professional Information', {
            'fields': ('occupation',)
        }),
        ('KYC Compliance', {
            'fields': ('kyc_status', 'kyc_approval_date', 'kyc_expiry_date', 'kyc_reviewed_by', 'kyc_notes', 'kyc_last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_kyc_action', 'reject_kyc_action', 'mark_for_renewal_action']

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_name.short_description = 'Customer Name'
    
    def kyc_status_badge(self, obj):
        colors = {
            'Compliant': '#28a745',
            'Pending': '#ffc107',
            'Non-Compliant': '#dc3545',
            'Renewal Required': '#fd7e14'
        }
        color = colors.get(obj.kyc_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color, obj.kyc_status
        )
    kyc_status_badge.short_description = 'KYC Status'
    
    def kyc_expiry_info(self, obj):
        if obj.kyc_expiry_date:
            if obj.kyc_is_expired:
                return format_html('<span style="color: red; font-weight: bold;">Expired</span>')
            elif obj.kyc_expires_soon:
                return format_html('<span style="color: orange; font-weight: bold;">Expires Soon</span>')
            else:
                return format_html('<span style="color: green;">Valid</span>')
        return format_html('<span style="color: gray;">N/A</span>')
    kyc_expiry_info.short_description = 'Expiry Status'
    
    def kyc_days_until_expiry(self, obj):
        days = obj.days_until_kyc_expiry
        if days is not None:
            if days < 0:
                return format_html('<span style="color: red;">{} days ago</span>', abs(days))
            elif days <= 30:
                return format_html('<span style="color: orange;">{} days</span>', days)
            else:
                return format_html('<span style="color: green;">{} days</span>', days)
        return 'N/A'
    kyc_days_until_expiry.short_description = 'Days Until Expiry'
    
    def approve_kyc_action(self, request, queryset):
        for customer in queryset:
            customer.approve_kyc(reviewed_by=request.user, expiry_months=12, notes="Approved by admin")
        self.message_user(request, f"{queryset.count()} customers' KYC approved (valid for 12 months)")
    approve_kyc_action.short_description = "Approve KYC (12 months validity)"
    
    def reject_kyc_action(self, request, queryset):
        for customer in queryset:
            customer.reject_kyc(reviewed_by=request.user, reason="Rejected by admin - please review documents")
        self.message_user(request, f"{queryset.count()} customers' KYC rejected")
    reject_kyc_action.short_description = "Reject KYC"
    
    def mark_for_renewal_action(self, request, queryset):
        for customer in queryset:
            customer.mark_kyc_for_renewal()
        self.message_user(request, f"{queryset.count()} customers marked for KYC renewal")
    mark_for_renewal_action.short_description = "Mark for KYC renewal"

admin.site.register(Customer, CustomerAdmin)
admin.site.register(KYCform)
admin.site.register(IncomeProof)
admin.site.register(ResidenceProof)
admin.site.register(CopyOfOmang)

admin.site.register(DirectDebitForm)
admin.site.register(HomeownersCover)
admin.site.register(ThirdPartyCarInsurance)

