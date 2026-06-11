import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from .forms import GuestRegistrationForm, SecureLoginForm, ProfileUpdateForm
from audit.models import AuditLog

logger = logging.getLogger('security')

def _ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR','unknown')

@never_cache
@require_http_methods(['GET','POST'])
def register_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    form = GuestRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        AuditLog.objects.create(user=user, action='REGISTER', details=f'New guest: {user.username}', ip_address=_ip(request))
        logger.info(f"REGISTER | user={user.username} | ip={_ip(request)}")
        messages.success(request, 'Welcome! Please sign in.')
        return redirect('login')
    return render(request, 'accounts/register.html', {'form': form})

@never_cache
@require_http_methods(['GET','POST'])
def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    form = SecureLoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            AuditLog.objects.create(user=user, action='LOGIN', details='Successful login', ip_address=_ip(request))
            logger.info(f"LOGIN | user={user.username} | ip={_ip(request)}")
            next_url = request.GET.get('next', '/dashboard/')
            if not next_url.startswith('/'): next_url = '/dashboard/'
            return redirect(next_url)
        else:
            logger.warning(f"LOGIN_FAIL | ip={_ip(request)} | username={request.POST.get('username','?')}")
            AuditLog.objects.create(user=None, action='LOGIN_FAIL', details=f"Failed: {request.POST.get('username','?')}", ip_address=_ip(request))
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    AuditLog.objects.create(user=request.user, action='LOGOUT', details='Logged out', ip_address=_ip(request))
    logout(request)
    return redirect('login')

@login_required
@never_cache
def profile_view(request):
    profile = request.user.profile
    form = ProfileUpdateForm(request.POST or None, instance=profile, user=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        AuditLog.objects.create(user=request.user, action='PROFILE_UPDATE', details='Profile updated', ip_address=_ip(request))
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

def locked_view(request):
    return render(request, 'accounts/locked.html', status=403)
