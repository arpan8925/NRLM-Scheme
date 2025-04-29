from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from form_builder.models import Form, FormSubmission
from accounts.models import User
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from datetime import datetime, timedelta
import json

def is_employee(user):
    # Check if the user has an employee role
    return user.role in [User.DISTRICT_EMPLOYEE, User.BLOCK_EMPLOYEE]

def is_block_employee(user):
    # Check if the user is specifically a block employee
    return user.role == User.BLOCK_EMPLOYEE

# Custom decorator to redirect DISTRICT_EMPLOYEE users to dashboard
def district_employee_redirect(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == User.DISTRICT_EMPLOYEE:
            messages.warning(request, "This page is not accessible for District Employees.")
            return redirect('employeedashboard:employee_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@user_passes_test(is_employee)
def dashboard(request):
    # Get total submissions count
    total_submissions = FormSubmission.objects.filter(employee=request.user).count()

    # Get pending forms count (forms that haven't been submitted by this user)
    pending_forms = Form.objects.filter(is_published=True).exclude(
        submissions__employee=request.user
    ).count()

    # Get completed forms count
    completed_forms = Form.objects.filter(
        is_published=True,
        submissions__employee=request.user
    ).distinct().count()

    context = {
        'total_submissions': total_submissions,
        'pending_forms': pending_forms,
        'completed_forms': completed_forms,
        'user': request.user,
    }

    # Add a message for DISTRICT_EMPLOYEE users
    if request.user.role == User.DISTRICT_EMPLOYEE:
        messages.info(request, "As a District Employee, you have access to the dashboard only. Other features are restricted.")

    return render(request, 'employeedashboard/dashboard.html', context)

@login_required
@district_employee_redirect
def my_forms(request):
    # Get all published forms
    forms = Form.objects.filter(is_published=True)

    context = {
        'forms': forms,
        'user': request.user,
    }

    return render(request, 'employeedashboard/my_forms.html', context)

@login_required
@user_passes_test(is_block_employee)
def my_submissions(request):
    # Get all form submissions for the current user
    submissions = FormSubmission.objects.filter(employee=request.user).order_by('-submitted_at')

    context = {
        'submissions': submissions,
        'user': request.user,
    }

    return render(request, 'employeedashboard/my_submissions.html', context)

@login_required
@user_passes_test(is_block_employee)
def profile(request):
    context = {
        'user': request.user,
    }
    return render(request, 'employeedashboard/profile.html', context)

@login_required
@user_passes_test(is_block_employee)
def view_form(request, slug):
    # Get the form by slug
    form = get_object_or_404(Form, slug=slug, is_published=True)
    form_fields = json.loads(form.fields) if form.fields else []

    context = {
        'form': form,
        'form_fields': form_fields,
        'user': request.user,
    }

    return render(request, 'form_builder/view_form.html', context)

@login_required
@user_passes_test(is_employee)
def reports(request):
    """
    Display reports and visualizations for all forms
    """
    # Get all forms
    forms = Form.objects.filter(is_published=True)

    # Get all submissions
    submissions = FormSubmission.objects.all()

    # Get all blocks that have submissions
    blocks = User.objects.filter(
        role=User.BLOCK_EMPLOYEE,
        form_submissions__isnull=False
    ).values('block').distinct()

    # Get submission counts by form
    form_submission_counts = Form.objects.filter(
        is_published=True
    ).annotate(
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
                'form_slug': form.slug,
                'block_counts': list(block_counts)
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

    # Get submission counts by month
    month_submission_counts = FormSubmission.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        submission_count=Count('id')
    ).order_by('month')

    # Get detailed breakdown of Block, Form, and Submission count
    detailed_submission_counts = []

    # Query to get all combinations of block, form, and count
    block_form_counts = FormSubmission.objects.filter(
        employee__role=User.BLOCK_EMPLOYEE
    ).values(
        'employee__block',
        'form__title',
        'form__slug'
    ).annotate(
        submission_count=Count('id')
    ).order_by('employee__block', 'form__title')

    # Convert to a more usable format
    for item in block_form_counts:
        detailed_submission_counts.append({
            'block': item['employee__block'],
            'form': item['form__title'],
            'form_slug': item['form__slug'],
            'count': item['submission_count']
        })

    context = {
        'forms': forms,
        'submissions_count': submissions.count(),
        'blocks': blocks,
        'form_submission_counts': list(form_submission_counts),
        'block_submission_counts': list(block_submission_counts),
        'form_block_submission_counts': form_block_submission_counts,
        'date_submission_counts': list(date_submission_counts),
        'month_submission_counts': list(month_submission_counts),
        'detailed_submission_counts': detailed_submission_counts,
        'user': request.user,
    }

    return render(request, 'employeedashboard/reports.html', context)

@login_required
@user_passes_test(is_employee)
def form_reports(request, slug):
    """
    Display reports and visualizations for a specific form
    """
    # Get the form
    form = get_object_or_404(Form, slug=slug, is_published=True)

    # Get all submissions for this form
    submissions = FormSubmission.objects.filter(form=form)

    # Get all blocks that have submissions for this form
    blocks = User.objects.filter(
        role=User.BLOCK_EMPLOYEE,
        form_submissions__form=form
    ).values('block').distinct()

    # Get submission counts by block for this form
    block_submission_counts = User.objects.filter(
        role=User.BLOCK_EMPLOYEE,
        form_submissions__form=form
    ).values('block').annotate(
        submission_count=Count('form_submissions')
    ).order_by('-submission_count')

    # Get submission counts by date (last 30 days) for this form
    thirty_days_ago = datetime.now() - timedelta(days=30)
    date_submission_counts = FormSubmission.objects.filter(
        form=form,
        created_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        submission_count=Count('id')
    ).order_by('date')

    # Get submission counts by month for this form
    month_submission_counts = FormSubmission.objects.filter(
        form=form
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        submission_count=Count('id')
    ).order_by('month')

    # Get detailed breakdown of Block and Submission count for this form
    detailed_submission_counts = []

    # Query to get all blocks and their submission counts for this form
    block_counts = FormSubmission.objects.filter(
        form=form,
        employee__role=User.BLOCK_EMPLOYEE
    ).values(
        'employee__block'
    ).annotate(
        submission_count=Count('id')
    ).order_by('-submission_count')

    # Convert to a more usable format
    for item in block_counts:
        detailed_submission_counts.append({
            'block': item['employee__block'],
            'count': item['submission_count']
        })

    context = {
        'form': form,
        'submissions_count': submissions.count(),
        'blocks': blocks,
        'block_submission_counts': list(block_submission_counts),
        'date_submission_counts': list(date_submission_counts),
        'month_submission_counts': list(month_submission_counts),
        'detailed_submission_counts': detailed_submission_counts,
        'user': request.user,
    }

    return render(request, 'employeedashboard/form_reports.html', context)
