from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Manager, Employee
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
            
            # If user has manager profile, redirect to manager dashboard
            try:
                if hasattr(user, 'dashboard_manager') or hasattr(user, 'account_manager'):
                    return redirect(reverse('managerdashboard:manager_dashboard'))
            except:
                pass
                
            # Default redirect
            return redirect('home')  # or wherever you want to redirect normal users
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
            
    return render(request, 'accounts/login.html')
