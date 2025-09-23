#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurancemanagement.settings')
django.setup()

from django.contrib.auth.models import User, Group
from customer.models import Customer

users = User.objects.all()
print(f'Total users: {users.count()}')

for user in users:
    groups = [g.name for g in user.groups.all()]
    customer_exists = hasattr(user, 'customer')
    print(f'User: {user.username}, Groups: {groups}, Customer exists: {customer_exists}')
    
    # Try to get customer object
    try:
        customer = Customer.objects.get(user=user)
        print(f'  Customer ID: {customer.id}, Name: {customer.user.first_name} {customer.user.last_name}')
    except Customer.DoesNotExist:
        print(f'  No Customer record found for user: {user.username}')

# Check groups
print(f'\nAvailable groups:')
for group in Group.objects.all():
    print(f'Group: {group.name}, Members: {group.user_set.count()}')
