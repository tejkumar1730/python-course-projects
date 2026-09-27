from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Profile


def role_required(role):
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not Profile.objects.filter(user=request.user, role=role).exists():
                raise PermissionDenied("This page is for a different account role.")
            return view(request, *args, **kwargs)
        return wrapped
    return decorator
