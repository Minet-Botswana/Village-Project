# app_name/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import Customer, KYCForm, DirectDebitForm, HomeownersCover, ThirdPartyCarInsurance

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'address', 'mobile', 'id_number', 'postal_address', 'physical_address', 'occupation', 'alternate_phone', 'gender', 'date_of_birth', 'marital_status', 'display_profile_pic')

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def display_profile_pic(self, obj):
        if obj.profile_pic:
            image_url = '{}{}'.format(settings.STATIC_URL, obj.profile_pic.url)
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', image_url)
        else:
            return 'No Image'

    get_name.short_description = 'Name'
    display_profile_pic.allow_tags = True
    display_profile_pic.short_description = 'Profile Picture'

admin.site.register(Customer, CustomerAdmin)
admin.site.register(KYCForm)
admin.site.register(DirectDebitForm)
admin.site.register(HomeownersCover)
admin.site.register(ThirdPartyCarInsurance)

