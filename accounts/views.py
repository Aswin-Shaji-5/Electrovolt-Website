from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from products.forms import ProductForm
from .forms import UpdateUserForm, UpdateProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings

#  REGISTER
# REGISTER
def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')

        email = request.POST.get('email')

        password = request.POST.get('password')

        role = request.POST.get('role')

        # Check username
        if User.objects.filter(username=username).exists():

            messages.error(request,"Username already exists")

            return redirect('register')

        # Check email
        if User.objects.filter(email=email).exists():

            messages.error(request,"Email already exists")

            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create profile
        profile, created = UserProfile.objects.get_or_create(user=user)

        profile.role = role
        profile.save()

        # =====================================
        # SEND WELCOME EMAIL
        # =====================================

        subject = "Welcome to ElectroVolt 🎉"

        message = f"""
Hello {username},

Your account has been created successfully.

====================================

LOGIN DETAILS

Username : {username}

Password : {password}

Role : {role}

====================================

You can now login to your account.

Thank you for joining ElectroVolt ❤️
"""

        send_mail(

            subject,

            message,

            settings.EMAIL_HOST_USER,

            [email],

            fail_silently=False
        )

        messages.success(request,"Account created successfully ✅")

        return redirect('login')

    return render(request,'accounts/register.html')

#  LOGIN
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect('home')

        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')


#  LOGOUT
def user_logout(request):
    logout(request)
    return redirect('login')


#  ADD PRODUCT (SELLER ONLY)
@login_required
def add_product(request):

    if request.user.userprofile.role != 'seller':
        messages.error(request, "Only sellers can add products")
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)  
            product.user = request.user        
            product.save()

            messages.success(request, "Product added successfully")
            return redirect('home')

    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})


@login_required
def update_profile(request):
    user_form = UpdateUserForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':

        if 'update_profile' in request.POST:
            user_form = UpdateUserForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Profile updated ✅")
                return redirect('home')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed 🔒")
                return redirect('home')

    return render(request, 'accounts/update_profile.html', {
        'user_form': user_form,
        'password_form': password_form
    })