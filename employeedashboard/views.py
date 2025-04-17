from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from form_builder.models import Form, FormSubmission
from accounts.models import User
import json

def is_employee(user):
    # Check if the user has an employee role
    return user.role in [User.DISTRICT_EMPLOYEE, User.BLOCK_EMPLOYEE]

@login_required
@user_passes_test(is_employee)
def dashboard(request):
    # Get the user
    user = request.user

    # Get employee specific stats
    # Check if the employee field exists in FormSubmission model
    try:
        # Count form submissions by this employee
        total_submissions = FormSubmission.objects.filter(employee=user).count()

        # Get published forms that are available to employees
        available_forms = Form.objects.filter(is_published=True).count()

        # Count completed forms (forms that have been submitted by this employee)
        completed_forms = total_submissions

        # Pending forms are available forms minus completed forms
        pending_forms = max(0, available_forms - completed_forms)
    except Exception as e:
        # If the migration hasn't been applied yet, use default values
        total_submissions = 0
        available_forms = Form.objects.filter(is_published=True).count()
        completed_forms = 0
        pending_forms = available_forms

    context = {
        'total_submissions': total_submissions,
        'pending_forms': pending_forms,
        'completed_forms': completed_forms,
        'user': request.user,
        'employee': user,
    }

    return render(request, 'employeedashboard/dashboard.html', context)

@login_required
@user_passes_test(is_employee)
def my_forms(request):
    # Get all published forms
    forms = Form.objects.filter(is_published=True)

    context = {
        'forms': forms,
        'user': request.user,
    }

    return render(request, 'employeedashboard/my_forms.html', context)

@login_required
@user_passes_test(is_employee)
def view_form(request, slug):
    # Get the form
    form = get_object_or_404(Form, slug=slug, is_published=True)
    form_fields = json.loads(form.fields) if form.fields else []

    context = {
        'form': form,
        'form_fields': form_fields,
        'user': request.user,
    }

    return render(request, 'employeedashboard/view_form.html', context)

@login_required
@user_passes_test(is_employee)
def my_submissions(request):
    # Get the user
    user = request.user

    # Get all submissions by this employee
    try:
        submissions = FormSubmission.objects.filter(employee=user).order_by('-created_at')
    except Exception:
        # If the migration hasn't been applied yet, return an empty queryset
        submissions = FormSubmission.objects.none()

    context = {
        'submissions': submissions,
        'user': request.user,
    }

    return render(request, 'employeedashboard/my_submissions.html', context)

@login_required
@user_passes_test(is_employee)
def profile(request):
    # Get the user
    user = request.user

    context = {
        'employee': user,
        'user': request.user,
    }

    return render(request, 'employeedashboard/profile.html', context)
