from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_only(view_func):
    """
    Decorator to restrict access strictly to Super Admin or django superusers.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('login')
        if request.user.role == 'SUPER_ADMIN' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def role_required(allowed_roles):
    """
    Decorator to restrict access based on user role.
    allowed_roles can be a single role string or a list of role strings.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('login')
            if request.user.role in allowed_roles or request.user.role == 'SUPER_ADMIN' or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator

