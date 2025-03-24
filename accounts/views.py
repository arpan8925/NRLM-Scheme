from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Manager, Employee

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # If user is superuser, show them all options
            if user.is_superuser:
                return render(request, 'accounts/superuser_choice.html')
            
            # Check if user is manager or employee
            try:
                manager = Manager.objects.get(user=user)
                return redirect('managerdashboard:manager_dashboard')
            except Manager.DoesNotExist:
                try:
                    employee = Employee.objects.get(user=user)
                    return redirect('employee_dashboard')
                except Employee.DoesNotExist:
                    messages.error(request, 'User profile not found.')
                    return redirect('login')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')
