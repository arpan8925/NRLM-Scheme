from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def is_employee(user):
    return not user.is_staff

@login_required
@user_passes_test(is_employee)
def dashboard(request):
    # Get employee specific stats
    total_submissions = 0  # You can add submission count logic later
    pending_forms = 0  # You can add pending forms count logic later
    completed_forms = 0  # You can add completed forms count logic later
    
    context = {
        'total_submissions': total_submissions,
        'pending_forms': pending_forms,
        'completed_forms': completed_forms,
        'user': request.user,
    }
    
    return render(request, 'employeedashboard/dashboard.html', context)
