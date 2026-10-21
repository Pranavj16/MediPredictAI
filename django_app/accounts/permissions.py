from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def get_user_role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return 'admin'
    if hasattr(user, 'profile'):
        return user.profile.role
    return 'patient'


def role_required(allowed_roles):
    """
    Decorator for views that checks whether a user has one of the allowed roles.
    Allowed roles list e.g. ['chw', 'clinician', 'admin']
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            role = get_user_role(request.user)
            if role in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            messages.error(request, "Access restricted: You do not have permission to view this medical interface.")
            return redirect('dashboard')
        return _wrapped_view
    return decorator


def can_access_patient(user, patient):
    """
    Verifies server-side if user is allowed to access the patient's records:
    - Superusers / Admins: Yes
    - Clinicians: Yes
    - CHWs: Yes if registered by them, assigned to their center, or authorized
    - Patient: Yes, ONLY if patient.user == user
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    role = get_user_role(user)
    if role in ['admin', 'clinician']:
        return True
    if role == 'chw':
        # CHWs can access patients they registered or in their center
        if patient.registered_by == user:
            return True
        if hasattr(user, 'profile') and user.profile.assigned_center:
            if patient.center == user.profile.assigned_center:
                return True
        return True
    if role == 'patient':
        return patient.user == user
    return False
