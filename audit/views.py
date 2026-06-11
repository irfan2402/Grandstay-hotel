from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from django.http import Http404
from .models import AuditLog

def _is_admin(user):
    try: return user.profile.is_admin
    except: return False

@login_required
@never_cache
def audit_log(request):
    if not _is_admin(request.user): raise Http404
    logs = AuditLog.objects.select_related('user').all()
    action_filter = request.GET.get('action','')
    if action_filter: logs = logs.filter(action=action_filter)
    paginator = Paginator(logs, 25)
    page = paginator.get_page(request.GET.get('page',1))
    return render(request, 'audit/log.html', {
        'page': page, 'action_filter': action_filter,
        'action_choices': AuditLog.ACTION_CHOICES,
    })
