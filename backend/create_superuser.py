#!/usr/bin/env python
"""
Script to create a superuser for testing
Run this after migrations
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_api.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin'
email = 'admin@topmate.io'
password = 'admin123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser created successfully!')
    print(f'Username: {username}')
    print(f'Password: {password}')
else:
    print('Superuser already exists')
