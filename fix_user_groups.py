#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurancemanagement.settings')
django.setup()

from django.contrib.auth.models import User, Group
from customer.models import Customer

# Get or create CUSTOMER group
customer_group, created = Group.objects.get_or_create(name='CUSTOMER')
print(f'CUSTOMER group {"created" if created else "already exists"}')

# Find all users who have Customer records but are not in CUSTOMER group
customers = Customer.objects.all()
print(f'\nFound {customers.count()} customer records')

fixed_count = 0
for customer in customers:
    user = customer.user
    if not user.groups.filter(name='CUSTOMER').exists():
        print(f'Adding user "{user.username}" to CUSTOMER group')
        customer_group.user_set.add(user)
        fixed_count += 1
    else:
        print(f'User "{user.username}" already in CUSTOMER group')

print(f'\nFixed {fixed_count} users')

# Verify the fix
print(f'\nVerification:')
users = User.objects.all()
for user in users:
    groups = [g.name for g in user.groups.all()]
    customer_exists = Customer.objects.filter(user=user).exists()
    print(f'User: {user.username}, Groups: {groups}, Has Customer record: {customer_exists}')
