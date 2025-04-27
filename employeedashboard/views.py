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
def my_submissions(request):
    # Get all form submissions for the current user
    submissions = FormSubmission.objects.filter(employee=request.user).order_by('-submitted_at')

    context = {
        'submissions': submissions,
        'user': request.user,
    }

    return render(request, 'employeedashboard/my_submissions.html', context)

@login_required
@user_passes_test(is_employee)
def profile(request):
    context = {
        'user': request.user,
    }
    return render(request, 'employeedashboard/profile.html', context)

@login_required
@user_passes_test(is_employee)
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
