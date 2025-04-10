from django.contrib.auth.decorators import user_passes_test

def customer_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_authenticated and u.role == 'Customer')(view_func)
    return decorated_view_func

def technician_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_authenticated and u.role == 'Technician')(view_func)
    return decorated_view_func

def admin_required(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)
    return decorated_view_func
