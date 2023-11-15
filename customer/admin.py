# app_name/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'address', 'mobile', 'display_profile_pic')

    def display_profile_pic(self, obj):
        if obj.profile_pic:
            image_url = '{}{}'.format(settings.STATIC_URL, obj.profile_pic.url)
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', image_url)
        else:
            return 'No Image'

    display_profile_pic.allow_tags = True
    display_profile_pic.short_description = 'Profile Picture'

admin.site.register(Customer, CustomerAdmin)
