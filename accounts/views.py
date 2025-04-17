from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User
from django.urls import reverse

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # If user is superuser, redirect to choice page
            if user.is_superuser:
                return render(request, 'accounts/superuser_choice.html')

            # Redirect based on user role
            if user.role == User.ADMIN:
                return redirect(reverse('managerdashboard:manager_dashboard'))
            elif user.role in [User.DISTRICT_EMPLOYEE, User.BLOCK_EMPLOYEE]:
                return redirect(reverse('employeedashboard:employee_dashboard'))
            else:
                # Default redirect
                return redirect('login')  # Redirect back to login if no role found
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
