from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import manager_required
from accounts.models import User
from django.db.models import Count, Q
from django.contrib import messages
from django.utils.crypto import get_random_string
from form_builder.models import Form, FormSubmission
from django.views.generic import ListView
import logging
import json
import csv
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek

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
def view_employee(request, employee_id):
    try:
        employee = User.objects.get(id=employee_id, role__in=[User.DISTRICT_EMPLOYEE, User.BLOCK_EMPLOYEE])

        context = {
            'employee': employee,
            'user': request.user,
        }

        return render(request, 'managerdashboard/view_employee.html', context)
    except User.DoesNotExist:
        messages.error(request, 'Employee not found.')
        return redirect('managerdashboard:employee_list')

@login_required
@manager_required
def edit_employee(request, employee_id):
    try:
        employee = User.objects.get(id=employee_id, role__in=[User.DISTRICT_EMPLOYEE, User.BLOCK_EMPLOYEE])

        if request.method == 'POST':
            # Get form data
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            role = request.POST.get('role')

            # Validate required fields
            if not first_name or not last_name or not role:
                messages.error(request, 'First name, last name, and role are required.')
                return render(request, 'managerdashboard/edit_employee.html', {
                    'employee': employee,
                })

            # Update employee information
            employee.first_name = first_name
            employee.last_name = last_name
            employee.role = role
            employee.state = request.POST.get('state', '')
            employee.district = request.POST.get('district', '')
            employee.block = request.POST.get('block', '') if role == User.BLOCK_EMPLOYEE else ''

            # Update password if provided
            new_password = request.POST.get('password')
            if new_password:
                employee.set_password(new_password)

            employee.save()

            messages.success(request, f'Employee {first_name} {last_name} updated successfully!')
            return redirect('managerdashboard:employee_list')

        context = {
            'employee': employee,
            'user': request.user,
        }

        return render(request, 'managerdashboard/edit_employee.html', context)
    except User.DoesNotExist:
        messages.error(request, 'Employee not found.')
        return redirect('managerdashboard:employee_list')

@login_required
@manager_required
def delete_employee(request, employee_id):
    try:
        employee = User.objects.get(id=employee_id, role__in=[User.DISTRICT_EMPLOYEE, User.BLOCK_EMPLOYEE])

        if request.method == 'POST':
            employee_name = f"{employee.first_name} {employee.last_name}"
            employee.delete()
            messages.success(request, f'Employee {employee_name} deleted successfully!')
            return redirect('managerdashboard:employee_list')

        context = {
            'employee': employee,
            'user': request.user,
        }

        return render(request, 'managerdashboard/delete_employee.html', context)
    except User.DoesNotExist:
        messages.error(request, 'Employee not found.')
        return redirect('managerdashboard:employee_list')

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
            'form_slug': form.slug,
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

            # Verify ownership - only superusers can edit forms
            if not request.user.is_superuser:
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
                'form_id': form.id,
                'form_slug': form.slug,
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

        # Verify ownership - only superusers can edit forms
        if not request.user.is_superuser:
            messages.error(request, "You don't have permission to edit this form")
            return redirect('managerdashboard:forms_list')

        # Load form fields from JSON
        try:
            # Print the raw fields data if DEBUG is True
            if settings.DEBUG:
                print(f"Raw form fields data: {form.fields}")

            form_fields = json.loads(form.fields)

            # Print the parsed fields data if DEBUG is True
            if settings.DEBUG:
                print(f"Parsed form fields: {form_fields}")

            # Ensure form_fields is a list
            if not isinstance(form_fields, list):
                if settings.DEBUG:
                    print(f"Warning: form_fields is not a list, it's a {type(form_fields)}")
                if isinstance(form_fields, dict):
                    form_fields = [form_fields]
                else:
                    form_fields = []
        except json.JSONDecodeError as e:
            if settings.DEBUG:
                print(f"JSON decode error: {e}")
            form_fields = []
        except Exception as e:
            if settings.DEBUG:
                print(f"Unexpected error parsing form fields: {e}")
            form_fields = []

        # Log the form fields for debugging
        logger.debug(f"Form fields for {form.slug}: {form_fields}")
        if settings.DEBUG:
            print(f"Form fields for {form.slug}: {form_fields}")

        context = {
            'form': form,
            'form_fields': json.dumps(form_fields),
            'user': request.user,
            'debug': settings.DEBUG,  # Pass DEBUG setting to the template
        }

        # Print the context only if DEBUG is True
        if settings.DEBUG:
            print(f"Context form_fields: {context['form_fields']}")

        return render(request, 'managerdashboard/edit_form.html', context)

    except Form.DoesNotExist:
        messages.error(request, 'Form not found')
        return redirect('managerdashboard:forms_list')

@login_required
@manager_required
def duplicate_form(request, slug):
    try:
        original_form = Form.objects.get(slug=slug)
        if not request.user.is_superuser:
            messages.error(request, 'You do not have permission to duplicate this form.')
            return redirect('managerdashboard:forms_list')

        # Create a new form with copied data
        new_form = Form.objects.create(
            title=f"{original_form.title} (Copy)",
            description=original_form.description,
            fields=original_form.fields,
            is_published=False
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
        if not request.user.is_superuser:
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
        if not request.user.is_superuser:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': 'You do not have permission to publish this form.'})
            messages.error(request, 'You do not have permission to publish this form.')
            return redirect('managerdashboard:forms_list')

        # Check if form is already published
        if form.is_published:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': 'This form is already published.'})
            messages.error(request, 'This form is already published.')
            return redirect('managerdashboard:forms_list')

        # Update form to published
        form.is_published = True
        form.save()

        # If it's an AJAX request, return JSON response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'message': 'Form published successfully!',
                'form_id': form.id,
                'form_slug': form.slug,
                'form_data': {
                    'title': form.title,
                    'fields': json.loads(form.fields),
                    'is_published': form.is_published,
                },
                'public_url': request.build_absolute_uri(f'/form/{form.slug}'),
                'redirect_url': reverse('managerdashboard:forms_list')
            })

        # Otherwise, redirect with a success message
        messages.success(request, 'Form published successfully!')
        return redirect('managerdashboard:forms_list')

    except Form.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'success': False, 'error': 'Form not found.'})
        messages.error(request, 'Form not found.')
        return redirect('managerdashboard:forms_list')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'success': False, 'error': f'Error publishing form: {str(e)}'})
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
        if not request.user.is_superuser:
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


@login_required
@manager_required
def form_submissions(request, slug):
    """
    Display all submissions for a specific form in a tabular format
    """
    try:
        form = Form.objects.get(slug=slug)

        # Check if user has permission to view this form's submissions
        if not request.user.is_superuser:
            messages.error(request, 'You do not have permission to view submissions for this form.')
            return redirect('managerdashboard:forms_list')

        # Get all submissions for this form
        submissions = FormSubmission.objects.filter(form=form).order_by('-created_at')

        # Get form fields from the form definition
        form_fields = json.loads(form.fields) if form.fields else []

        # Extract field labels for table headers
        field_labels = [field['label'] for field in form_fields]

        # Process submissions data for the table
        submissions_data = []
        for submission in submissions:
            # Parse the JSON responses
            responses = json.loads(submission.responses)

            # Create a submission data object
            submission_data = {
                'id': submission.id,
                'employee': submission.employee.email if submission.employee else 'Anonymous',
                'created_at': submission.created_at,
                'responses': responses
            }

            submissions_data.append(submission_data)

        context = {
            'form': form,
            'field_labels': field_labels,
            'submissions': submissions_data,
            'submissions_count': submissions.count(),
        }

        return render(request, 'managerdashboard/form_submissions.html', context)

    except Form.DoesNotExist:
        messages.error(request, 'Form not found.')
        return redirect('managerdashboard:forms_list')


@login_required
@manager_required
def reports(request):
    """
    Display reports and visualizations for form submissions by block
    """
    # Get all forms
    forms = Form.objects.all()

    # Get all submissions
    submissions = FormSubmission.objects.all()

    # Get all blocks that have submissions
    blocks = User.objects.filter(
        role=User.BLOCK_EMPLOYEE,
        form_submissions__isnull=False
    ).values('block').distinct()

    # Get submission counts by form
    form_submission_counts = Form.objects.annotate(
        submission_count=Count('submissions')
    ).values('title', 'submission_count').order_by('-submission_count')

    # Get submission counts by block
    block_submission_counts = User.objects.filter(
        role=User.BLOCK_EMPLOYEE,
        form_submissions__isnull=False
    ).values('block').annotate(
        submission_count=Count('form_submissions')
    ).order_by('-submission_count')

    # Get submission counts by form and block
    form_block_submission_counts = []
    for form in forms:
        block_counts = User.objects.filter(
            role=User.BLOCK_EMPLOYEE,
            form_submissions__form=form
        ).values('block').annotate(
            submission_count=Count('form_submissions')
        ).order_by('-submission_count')

        if block_counts:
            form_block_submission_counts.append({
                'form_title': form.title,
                'form_id': form.id,
                'block_counts': list(block_counts)
            })

    # Get detailed breakdown of Block, Form, and Submission count
    detailed_submission_counts = []

    # Query to get all combinations of block, form, and count
    block_form_counts = FormSubmission.objects.filter(
        employee__role=User.BLOCK_EMPLOYEE
    ).values(
        'employee__block',
        'form__title'
    ).annotate(
        submission_count=Count('id')
    ).order_by('employee__block', 'form__title')

    # Convert to a more usable format
    for item in block_form_counts:
        detailed_submission_counts.append({
            'block': item['employee__block'],
            'form': item['form__title'],
            'count': item['submission_count']
        })

    # Get submission counts by date (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    date_submission_counts = FormSubmission.objects.filter(
        created_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        submission_count=Count('id')
    ).order_by('date')

    # Get submission counts by week
    week_submission_counts = FormSubmission.objects.annotate(
        week=TruncWeek('created_at')
    ).values('week').annotate(
        submission_count=Count('id')
    ).order_by('week')

    # Get submission counts by month
    month_submission_counts = FormSubmission.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        submission_count=Count('id')
    ).order_by('month')

    context = {
        'forms': forms,
        'submissions_count': submissions.count(),
        'blocks': blocks,
        'form_submission_counts': list(form_submission_counts),
        'block_submission_counts': list(block_submission_counts),
        'form_block_submission_counts': form_block_submission_counts,
        'date_submission_counts': list(date_submission_counts),
        'week_submission_counts': list(week_submission_counts),
        'month_submission_counts': list(month_submission_counts),
        'detailed_submission_counts': detailed_submission_counts,
        'user': request.user,
    }

    return render(request, 'managerdashboard/reports.html', context)