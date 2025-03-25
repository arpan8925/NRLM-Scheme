from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import manager_required
from accounts.models import Employee, Manager, User
from django.db.models import Count
from django.contrib import messages
from django.utils.crypto import get_random_string
from form_builder.models import Form
from django.views.generic import ListView
import logging
import json
from django.http import JsonResponse
from django.urls import reverse

logger = logging.getLogger(__name__)

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

@login_required
@manager_required
def forms_list(request):
    logger.info(f"Forms list view accessed by user: {request.user.email}")
    try:
        if request.user.is_superuser:
            logger.info("Superuser accessing forms")
            forms = Form.objects.all().order_by('-created_at')
        else:
            logger.info("Regular manager accessing forms")
            try:
                manager = Manager.objects.get(user=request.user)
                forms = Form.objects.filter(creator=manager).order_by('-created_at')
            except Manager.DoesNotExist:
                logger.error(f"Manager profile not found for user: {request.user.email}")
                messages.error(request, 'Manager profile not found.')
                return redirect('managerdashboard:manager_dashboard')
        
        context = {
            'forms': forms,
            'draft_count': forms.filter(status='draft').count(),
            'published_count': forms.filter(status='published').count(),
            'archived_count': forms.filter(status='archived').count(),
            'trash_count': forms.filter(status='trash').count(),
            'user': request.user,
        }
        
        logger.info(f"Forms loaded successfully. Total forms: {forms.count()}")
        return render(request, 'managerdashboard/forms_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in forms_list view: {str(e)}", exc_info=True)
        messages.error(request, f'Error loading forms: {str(e)}')
        return redirect('managerdashboard:manager_dashboard')

@login_required
@manager_required
def create_form(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            manager = Manager.objects.get(user=request.user) if not request.user.is_superuser else None
            
            form = Form.objects.create(
                title=data['title'],
                creator=manager,
                status='draft',
                form_data=data.get('fields', [])
            )
            
            return JsonResponse({
                'success': True,
                'form_id': form.id,
                'redirect_url': reverse('managerdashboard:edit_form', kwargs={'slug': form.slug})
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return render(request, 'managerdashboard/create_form.html')

@login_required
@manager_required
def update_form(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = Form.objects.get(id=data['form_id'])
            
            # Verify ownership
            if not request.user.is_superuser and form.creator.user != request.user:
                raise PermissionError("You don't have permission to edit this form")
            
            form.title = data['title']
            form.status = data['status']
            form.form_data = data['fields']
            form.save()
            
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('managerdashboard:forms_list')
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

@login_required
@manager_required
def edit_form(request, slug):
    try:
        form = Form.objects.get(slug=slug)
        if not request.user.is_superuser and form.creator.user != request.user:
            messages.error(request, 'You do not have permission to edit this form.')
            return redirect('managerdashboard:forms_list')
            
        if request.method == 'POST':
            form.title = request.POST.get('title')
            form.description = request.POST.get('description')
            form.save()
            messages.success(request, 'Form updated successfully!')
            return redirect('managerdashboard:forms_list')
            
        return render(request, 'managerdashboard/edit_form.html', {'form': form})
    except Form.DoesNotExist:
        messages.error(request, 'Form not found.')
        return redirect('managerdashboard:forms_list')

@login_required
@manager_required
def duplicate_form(request, slug):
    try:
        original_form = Form.objects.get(slug=slug)
        if not request.user.is_superuser and original_form.creator.user != request.user:
            messages.error(request, 'You do not have permission to duplicate this form.')
            return redirect('managerdashboard:forms_list')
            
        # Create a new form with copied data
        manager = Manager.objects.get(user=request.user) if not request.user.is_superuser else None
        new_form = Form.objects.create(
            title=f"{original_form.title} (Copy)",
            description=original_form.description,
            creator=manager,
            status='draft',
            form_data=original_form.form_data
        )
        messages.success(request, 'Form duplicated successfully!')
        return redirect('managerdashboard:edit_form', slug=new_form.slug)
    except Form.DoesNotExist:
        messages.error(request, 'Form not found.')
        return redirect('managerdashboard:forms_list')

@login_required
@manager_required
def delete_form(request, slug):
    try:
        form = Form.objects.get(slug=slug)
        if not request.user.is_superuser and form.creator.user != request.user:
            messages.error(request, 'You do not have permission to delete this form.')
            return redirect('managerdashboard:forms_list')
            
        form.delete()
        messages.success(request, 'Form deleted successfully!')
        return redirect('managerdashboard:forms_list')
    except Form.DoesNotExist:
        messages.error(request, 'Form not found.')
        return redirect('managerdashboard:forms_list')
