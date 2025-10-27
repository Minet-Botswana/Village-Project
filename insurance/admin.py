from django.contrib import admin
from .models import Category, Policy, PolicyRecord, Question, ThirdpartyPolicy, ThirdpartyPolicyRecord, PolicyWording
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'creation_date')

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_name', 'category', 'insured', 'sum_assurance', 'premium', 'tenure', 'creation_date', 'cover_start', 'cover_end', 'policy_number')
    search_fields = ['policy_name', 'policy_number']

@admin.register(ThirdpartyPolicy)
class ThirdpartyPolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_name', 'category', 'insured', 'premium', 'tenure', 'creation_date', 'cover_start', 'cover_end', 'policy_number')
    search_fields = ['policy_name', 'policy_number']

@admin.register(PolicyRecord)
class PolicyRecordAdmin(admin.ModelAdmin):
    list_display = ('customer', 'Policy', 'status', 'creation_date', 'cover_start', 'cover_end', 'tenure')
    search_fields = ['customer__first_name', 'customer__last_name', 'Policy__policy_name']

@admin.register(ThirdpartyPolicyRecord)
class ThirdpartyPolicyRecordAdmin(admin.ModelAdmin):
    list_display = ('thirdpartycustomer', 'thirdpartypolicy', 'thirdpartystatus', 'thirdpartycreation_date', 'cover_start', 'cover_end', 'tenure')
    search_fields = ['thirdpartycustomer__first_name', 'thirdpartycustomer__last_name', 'thirdpartypolicy__policy_name']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'description', 'admin_comment', 'answered_by', 'answered_date', 'asked_date')
    search_fields = ['customer__first_name', 'customer__last_name', 'description']
    list_filter = ('answered_by', 'asked_date')
    readonly_fields = ('asked_date', 'answered_by', 'answered_date')
    
    def save_model(self, request, obj, form, change):
        # If admin_comment is being changed from 'Nothing' to something else, record who answered
        if change:
            old_obj = Question.objects.get(pk=obj.pk)
            if old_obj.admin_comment == 'Nothing' and obj.admin_comment != 'Nothing':
                obj.answered_by = request.user
                from django.utils import timezone
                obj.answered_date = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(PolicyWording)
class PolicyWordingAdmin(admin.ModelAdmin):
    list_display = ('title', 'policy_type', 'version', 'effective_date', 'status_badge', 'uploaded_by', 'created_at')
    list_filter = ('policy_type', 'is_active', 'effective_date')
    search_fields = ['title', 'version', 'description']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Policy Information', {
            'fields': ('title', 'policy_type', 'version', 'description')
        }),
        ('Document Details', {
            'fields': ('document', 'effective_date', 'is_active')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">Inactive</span>'
            )
    status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
