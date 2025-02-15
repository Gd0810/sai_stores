#### **accounts/views.py**

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import CustomUser
from django.core.mail import send_mail
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import format_html
import random

# Global variable to store OTPs for simplicity (use a model in production)
otp_storage = {}

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('store:index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

def logout_user(request):
    logout(request)
    return redirect('accounts:login')

import random
import time
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import CustomUser

otp_storage = {}  # Format: {email: {"otp": 123456, "timestamp": 1700000000}}



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = CustomUser.objects.filter(email=email).first()
        if user:
            otp = random.randint(100000, 999999)
            otp_storage[email] = otp  # Store OTP for verification

            subject = "Password Reset OTP"

            # Plain text version (fallback for email clients without HTML support)
            text_content = f"Hi {user.username}, Your OTP for resetting the password is: {otp}"

            # HTML version with styling
            html_content = format_html(
                """
                <p>From Vellore Cart User Authentication Team</p>
                <p>Hi <strong>{}</strong>, Your OTP for resetting the password is:</p>
                <h2 style="color: #0DA487; font-size: 50px; display: flex; justify-content: center; font-weight: bold;">{}</h2>
                <p>Please enter this OTP to reset your password.</p>
                """,
                user.username, otp
            )

            # Send email with both text and HTML content
            email_message = EmailMultiAlternatives(subject, text_content, 'no-reply@VelloreCart.com', [email])
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

            messages.success(request, 'OTP has been sent to your Gmail')
            return redirect('accounts:reset_password')
        else:
            messages.error(request, 'Email not found.')

    return render(request, 'accounts/forgot_password.html')



def reset_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        otp = int(request.POST['otp'])
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        if email in otp_storage and otp_storage[email] == otp:
            if new_password == confirm_password:
                user = CustomUser.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                del otp_storage[email]
                messages.success(request, 'Password reset successfully!')
                return redirect('accounts:login')
            else:
                messages.error(request, 'Passwords do not match.')
        else:
            messages.error(request, 'Invalid OTP.')
    return render(request, 'accounts/reset_password.html')
