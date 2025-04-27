from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import manager_required
from accounts.models import User
from django.db.models import Count
from django.contrib import messages
from django.utils.crypto import get_random_string
from form_builder.models import Form, FormSubmission
from django.views.generic import ListView
import logging
import json
import csv
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

# Removed the generate_unique_employee_id function as it's no longer needed

@login_required
@manager_required
def dashboard(request):
    # Get statistics
    # Show all employees (users with employee roles)
    total_employees = User.objects.filter(role__in=[User.DISTRICT_EMPLOYEE, User.BLOCK_EMPLOYEE]).count()
    employees = User.objects.filter(role__in=[User.DISTRICT_EMPLOYEE, User.BLOCK_EMPLOYEE])

    # Current admin user
    manager = request.user

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
    # Show all employees (users with employee roles)
    employees = User.objects.filter(role__in=[User.DISTRICT_EMPLOYEE, User.BLOCK_EMPLOYEE])

    context = {
        'employees': employees,
        'user': request.user,
    }

    return render(request, 'managerdashboard/employee_list.html', context)

@login_required
@manager_required
def add_employee(request):
    if request.method == 'POST':
        # Get form data
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Validate required fields
        if not email or not password or not first_name or not last_name:
            messages.error(request, 'Email, password, first name, and last name are required.')
            return render(request, 'managerdashboard/add_employee.html', {
                'form_data': request.POST,
            })

        # Check if email already exists - case insensitive check
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, f'Email {email} already exists. Please use a different email.')
            return render(request, 'managerdashboard/add_employee.html', {
                'form_data': request.POST,  # Return the form data to repopulate the form
            })

        # We'll generate the employee ID automatically

        try:
            # Normalize email to lowercase
            email = email.lower()

            # Double-check if email exists (case insensitive)
            if User.objects.filter(email__iexact=email).exists():
                messages.error(request, f'Email {email} already exists. Please use a different email.')
                return render(request, 'managerdashboard/add_employee.html', {
                    'form_data': request.POST,
                })

            # Get role from form
            role = request.POST.get('role')

            # Create user with all fields at once
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                state=request.POST.get('state', ''),
                district=request.POST.get('district', ''),
                block=request.POST.get('block', '') if role == User.BLOCK_EMPLOYEE else ''
            )

            messages.success(request, f'Employee {first_name} {last_name} created successfully!')
            return redirect('managerdashboard:employee_list')

        except Exception as e:
            error_message = str(e)
            print(f"Error creating employee: {error_message}")

            if 'UNIQUE constraint failed: accounts_user.email' in error_message:
                messages.error(request, f'Email {email} already exists. Please use a different email.')
            # Removed employee_id related error handling
            else:
                messages.error(request, f'Error creating employee: {error_message}')

            # Return the form data to repopulate the form
            return render(request, 'managerdashboard/add_employee.html', {
                'form_data': request.POST,
            })

    return render(request, 'managerdashboard/add_employee.html')

@login_required
@manager_required
def forms_list(request):
    if request.user.is_superuser:
        # Superuser can see all forms
        forms = Form.objects.all()
    else:
        # Regular users see only their forms
        forms = Form.objects.filter(creator=request.user)

    # Get count for published forms
    published_count = forms.filter(is_published=True).count()

    context = {
        'forms': forms,
        'published_count': published_count,
    }

    return render(request, 'managerdashboard/forms_list.html', context)

@login_required
@manager_required
def create_form(request):
    return render(request, 'managerdashboard/form_builder.html')

@require_http_methods(["POST"])
def save_form(request):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        title = data.get('title', 'Untitled Form')
        fields = data.get('fields', [])

        # Log the received data
        print("Received form data:", data)

        # Clean up the fields data to remove any empty options
        cleaned_fields = []
        for field in fields:
            cleaned_field = {
                'type': field['type'],
                'label': field['label'],
                'required': field.get('required', False)
            }

            # Only add placeholder if it exists and has a value
            if field.get('placeholder'):
                cleaned_field['placeholder'] = field['placeholder']

            # Only add options for select, radio, checkbox fields if they exist
            if field['type'] in ['select', 'radio', 'checkbox'] and field.get('options'):
                cleaned_field['options'] = field['options']

            # Add accept attribute for file upload fields
            if field['type'] == 'file' and field.get('accept'):
                cleaned_field['accept'] = field['accept']

            cleaned_fields.append(cleaned_field)

        # Create form instance with cleaned data
        form = Form.objects.create(
            title=title,
            fields=json.dumps(cleaned_fields),
            is_published=False
        )

        return JsonResponse({
            'success': True,
            'form_id': form.id,
            'redirect_url': reverse('managerdashboard:forms_list'),
            'form_data': {
                'title': form.title,
                'fields': json.loads(form.fields),
                'created_at': form.created_at.isoformat(),
                'is_published': form.is_published
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print("Error saving form:", str(e))
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@manager_required
def update_form(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = Form.objects.get(slug=data['slug'])

            # Verify ownership
            if not request.user.is_superuser and form.created_by != request.user:
                raise PermissionError("You don't have permission to edit this form")

            # Clean up the fields data
            cleaned_fields = []
            for field in data['fields']:
                cleaned_field = {
                    'type': field['type'],
                    'label': field['label'],
                    'required': field.get('required', False)
                }

                # Only add placeholder if it exists and has a value
                if field.get('placeholder'):
                    cleaned_field['placeholder'] = field['placeholder']

                # Only add options for select, radio, checkbox fields if they exist
                if field['type'] in ['select', 'radio', 'checkbox'] and field.get('options'):
                    cleaned_field['options'] = field['options']

                # Add accept attribute for file upload fields
                if field['type'] == 'file' and field.get('accept'):
                    cleaned_field['accept'] = field['accept']

                cleaned_fields.append(cleaned_field)

            # Update form
            form.title = data['title']
            form.fields = json.dumps(cleaned_fields)
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

        # Verify ownership
        if not request.user.is_superuser and form.created_by != request.user:
            messages.error(request, "You don't have permission to edit this form")
            return redirect('managerdashboard:forms_list')

        # Load form fields from JSON
        try:
            form_fields = json.loads(form.fields)
        except json.JSONDecodeError:
            form_fields = []

        context = {
            'form': form,
            'form_fields': json.dumps(form_fields),
            'user': request.user,
        }

        return render(request, 'managerdashboard/edit_form.html', context)

    except Form.DoesNotExist:
        messages.error(request, 'Form not found')
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
        manager = request.user.dashboard_manager if not request.user.is_superuser else None
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

@login_required
@manager_required
def publish_form(request, slug):
    try:
        form = Form.objects.get(slug=slug)

        # Check if user has permission to publish this form
        if not request.user.is_superuser and form.created_by != request.user:
            messages.error(request, 'You do not have permission to publish this form.')
            return redirect('managerdashboard:forms_list')

        # Check if form is already published
        if form.is_published:
            messages.error(request, 'This form is already published.')
            return redirect('managerdashboard:forms_list')

        # Update form to published
        form.is_published = True
        form.save()

        messages.success(request, 'Form published successfully!')
    except Form.DoesNotExist:
        messages.error(request, 'Form not found.')
    except Exception as e:
        messages.error(request, f'Error publishing form: {str(e)}')

    return redirect('managerdashboard:forms_list')


@login_required
@manager_required
def export_form_submissions(request, slug):
    """
    Export form submissions as CSV
    """
    try:
        form = Form.objects.get(slug=slug)

        # Check if user has permission to export this form's submissions
        if not request.user.is_superuser and form.created_by != request.user:
            messages.error(request, 'You do not have permission to export submissions for this form.')
            return redirect('managerdashboard:forms_list')

        # Get all submissions for this form
        submissions = FormSubmission.objects.filter(form=form).order_by('-created_at')

        if not submissions.exists():
            messages.warning(request, 'No submissions found for this form.')
            return redirect('managerdashboard:forms_list')

        # Create the HttpResponse with CSV header
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{form.slug}_submissions_{timestamp}.csv"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # Create CSV writer
        writer = csv.writer(response)

        # Get form fields from the first submission to determine columns
        first_submission = submissions.first()
        responses_data = json.loads(first_submission.responses)

        # Create header row with field labels and add submission timestamp and employee info
        header_row = ['Submission Date', 'Employee Email']
        header_row.extend(responses_data.keys())
        writer.writerow(header_row)

        # Write data rows
        for submission in submissions:
            responses_data = json.loads(submission.responses)

            # Create a row with submission timestamp and employee info
            row = [
                submission.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                submission.employee.email if submission.employee else 'Anonymous'
            ]

            # Add response data for each field
            for field_label in responses_data.keys():
                value = responses_data.get(field_label, '')

                # Handle list values (like checkbox responses)
                if isinstance(value, list):
                    row.append(', '.join(value))
                else:
                    row.append(value)

            writer.writerow(row)

        return response

    except Form.DoesNotExist:
        messages.error(request, 'Form not found.')
        return redirect('managerdashboard:forms_list')
    except Exception as e:
        messages.error(request, f'Error exporting submissions: {str(e)}')
        return redirect('managerdashboard:forms_list')