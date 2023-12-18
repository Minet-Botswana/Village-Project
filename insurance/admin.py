from django.contrib import admin
from .models import Category, Policy, PolicyRecord, Question

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'creation_date')

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_name', 'category', 'insured', 'sum_assurance', 'premium', 'tenure', 'creation_date', 'cover_start', 'cover_end', 'policy_number')
    search_fields = ['policy_name', 'policy_number']

@admin.register(PolicyRecord)
class PolicyRecordAdmin(admin.ModelAdmin):
    list_display = ('customer', 'Policy', 'status', 'creation_date', 'cover_start', 'cover_end', 'tenure')
    search_fields = ['customer__first_name', 'customer__last_name', 'Policy__policy_name']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'description', 'admin_comment', 'asked_date')
    search_fields = ['customer__first_name', 'customer__last_name']
