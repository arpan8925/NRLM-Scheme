from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import manager_required
from accounts.models import Employee, Manager, User
from django.db.models import Count
from django.contrib import messages
from django.utils.crypto import get_random_string

@login_required
@manager_required
def dashboard(request):
    # Get statistics
    if request.user.is_superuser:
        # For superuser, show all employees
        total_employees = Employee.objects.count()
        employees = Employee.objects.all().select_related('user')
        manager = None  # Superuser might not have a manager profile
    else:
        # For regular manager, show only their employees
        manager = Manager.objects.get(user=request.user)
        total_employees = Employee.objects.filter(manager=manager).count()
        employees = Employee.objects.filter(manager=manager).select_related('user')
    
    recent_submissions = 0  # You can add submission count logic later
    pending_forms = 0  # You can add pending forms count logic later
    
    context = {
        'manager': manager,
        'total_employees': total_employees,
        'recent_submissions': recent_submissions,
        'pending_forms': pending_forms,
        'employees': employees,
        'user': request.user,
    }
    
    return render(request, 'managerdashboard/dashboard.html', context)

@login_required
@manager_required
def employee_list(request):
    if request.user.is_superuser:
        # For superuser, show all employees
        employees = Employee.objects.all().select_related('user')
    else:
        # For regular manager, show only their employees
        manager = Manager.objects.get(user=request.user)
        employees = Employee.objects.filter(manager=manager).select_related('user')
    
    context = {
        'employees': employees,
        'user': request.user,
    }
    
    return render(request, 'managerdashboard/employee_list.html', context)

@login_required
@manager_required
def add_employee(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        employee_id = request.POST.get('employee_id')
        position = request.POST.get('position')
        department = request.POST.get('department')
        hire_date = request.POST.get('hire_date') or None
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please use a different email.')
            return render(request, 'managerdashboard/add_employee.html')
        
        # Check if employee ID already exists
        if Employee.objects.filter(employee_id=employee_id).exists():
            messages.error(request, 'Employee ID already exists. Please use a different ID.')
            return render(request, 'managerdashboard/add_employee.html')
        
        try:
            # Create user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Get manager
            if request.user.is_superuser:
                # If superuser is creating employee, assign to first manager or None
                try:
                    manager = Manager.objects.first()
                except Manager.DoesNotExist:
                    manager = None
            else:
                # If regular manager is creating employee, assign to themselves
                manager = Manager.objects.get(user=request.user)
            
            # Create employee
            employee = Employee.objects.create(
                user=user,
                manager=manager,
                employee_id=employee_id,
                position=position,
                department=department
            )
            
            messages.success(request, f'Employee {first_name} {last_name} created successfully!')
            return redirect('managerdashboard:employee_list')
            
        except Exception as e:
            messages.error(request, f'Error creating employee: {str(e)}')
    
    return render(request, 'managerdashboard/add_employee.html')
