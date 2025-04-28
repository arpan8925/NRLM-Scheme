from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from form_builder.models import Form, FormSubmission
from accounts.models import User
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
