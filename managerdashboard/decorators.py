from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from accounts.models import User

def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Allow superuser access
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Check if user has admin role
        if request.user.role == User.ADMIN:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')
    return _wrapped_view