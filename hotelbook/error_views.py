import logging
from django.shortcuts import render
security_logger = logging.getLogger('security')

def bad_request(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def permission_denied(request, exception=None):
    user = request.user.username if request.user.is_authenticated else 'anonymous'
    security_logger.warning(f"403 | path={request.path} | user={user}")
    return render(request, 'errors/403.html', status=403)

def page_not_found(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def server_error(request):
    security_logger.error(f"500 | path={request.path}")
    return render(request, 'errors/500.html', status=500)
