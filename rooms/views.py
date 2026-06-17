# rooms/views.py — HARDENED VERSION
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied

from .models import Room, Reservation
from .forms import ReservationForm, AdminReservationForm, RoomForm
from audit.models import AuditLog

logger = logging.getLogger('security')


def _ip(r):
    xff = r.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else r.META.get('REMOTE_ADDR', 'unknown')


def _is_admin(user):
    try:
        return user.profile.is_admin
    except Exception:
        return False


def _admin_required(request):
    """Raise PermissionDenied (→ 403) — never a silent 404 — if not admin."""
    if not _is_admin(request.user):
        logger.warning(
            f"UNAUTHORIZED_ADMIN_ACCESS | user={request.user.username} | path={request.path}"
        )
        raise PermissionDenied


# ── Dashboard ─────────────────────────────────────────────────────────────────
@login_required
@never_cache
def dashboard(request):
    if _is_admin(request.user):
        reservations = Reservation.objects.select_related('guest', 'room').all()[:10]
        return render(request, 'rooms/dashboard.html', {
            'reservations': reservations,
            'total':    Reservation.objects.count(),
            'pending':  Reservation.objects.filter(status='pending').count(),
            'checkins': Reservation.objects.filter(status='checked_in').count(),
            'rooms':    Room.objects.count(),
            'is_admin': True,
        })
    reservations = Reservation.objects.filter(guest=request.user).select_related('room')[:5]
    return render(request, 'rooms/dashboard.html', {'reservations': reservations, 'is_admin': False})


# ── Room browsing ──────────────────────────────────────────────────────────────
@login_required
@never_cache
def room_list(request):
    room_type = request.GET.get('type', '')
    rooms = Room.objects.filter(is_available=True)
    if room_type in dict(Room.ROOM_TYPES):
        rooms = rooms.filter(room_type=room_type)
    return render(request, 'rooms/room_list.html', {
        'rooms': rooms, 'room_types': Room.ROOM_TYPES, 'selected_type': room_type,
    })


# ── Reservations ───────────────────────────────────────────────────────────────
@login_required
@never_cache
def reservation_list(request):
    res = Reservation.objects.filter(guest=request.user).select_related('room')
    page = Paginator(res, 10).get_page(request.GET.get('page', 1))
    return render(request, 'rooms/reservation_list.html', {
        'page': page, 'is_admin': _is_admin(request.user),
    })


@login_required
@never_cache
@require_http_methods(['GET', 'POST'])
def reservation_create(request, room_pk=None):
    initial = {}
    if room_pk:
        room = get_object_or_404(Room, pk=room_pk, is_available=True)
        initial['room'] = room
    form = ReservationForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        res = form.save(commit=False)
        res.guest = request.user
        res.save()
        AuditLog.objects.create(
            user=request.user, action='RESERVATION_CREATE',
            details=f'Reserved {res.room.name} | {res.check_in} - {res.check_out}',
            ip_address=_ip(request),
        )
        messages.success(request, f'Room reserved! Total: RM {res.total_price:.2f}')
        return redirect('reservation_list')
    return render(request, 'rooms/reservation_form.html', {'form': form, 'title': 'New Reservation'})


@login_required
@never_cache
def reservation_detail(request, pk):
    # IDOR fix: restrict to owner unless admin
    if _is_admin(request.user):
        res = get_object_or_404(Reservation, pk=pk)
    else:
        res = get_object_or_404(Reservation, pk=pk, guest=request.user)
    steps = [
        ("pending",    "Pending",    "#888"),
        ("confirmed",  "Confirmed",  "#22c55e"),
        ("checked_in", "Checked In", "#3b82f6"),
        ("checked_out","Checked Out","#a855f7"),
    ]
    return render(request, 'rooms/reservation_detail.html', {
        "res": res, "is_admin": _is_admin(request.user), "steps": steps,
    })


@login_required
@never_cache
@require_http_methods(['GET', 'POST'])
def reservation_edit(request, pk):
    if _is_admin(request.user):
        res        = get_object_or_404(Reservation, pk=pk)
        form_class = AdminReservationForm
    else:
        # Ownership check — prevents IDOR
        res = get_object_or_404(Reservation, pk=pk, guest=request.user)
        if res.status != 'pending':
            messages.error(request, 'Only pending reservations can be edited.')
            return redirect('reservation_detail', pk=pk)
        form_class = ReservationForm

    form = form_class(request.POST or None, instance=res)
    if request.method == 'POST' and form.is_valid():
        form.save()
        AuditLog.objects.create(
            user=request.user, action='RESERVATION_EDIT',
            details=f'Edited reservation {res.id}', ip_address=_ip(request),
        )
        messages.success(request, 'Reservation updated.')
        return redirect('reservation_detail', pk=pk)
    return render(request, 'rooms/reservation_form.html', {
        'form': form, 'title': 'Edit Reservation', 'res': res,
    })


@login_required
@require_http_methods(['POST'])
def reservation_cancel(request, pk):
    if _is_admin(request.user):
        res = get_object_or_404(Reservation, pk=pk)
    else:
        # Ownership check
        res = get_object_or_404(Reservation, pk=pk, guest=request.user)

    if res.status in ('pending', 'confirmed'):
        res.status = 'cancelled'
        res.save()
        AuditLog.objects.create(
            user=request.user, action='RESERVATION_CANCEL',
            details=f'Cancelled reservation {res.id}', ip_address=_ip(request),
        )
        messages.success(request, 'Reservation cancelled.')
    else:
        messages.error(request, 'This reservation cannot be cancelled.')
    return redirect('reservation_list')


# ── Admin Room Management ──────────────────────────────────────────────────────
@login_required
@never_cache
def admin_room_list(request):
    _admin_required(request)
    rooms = Room.objects.all()
    return render(request, 'rooms/admin_room_list.html', {'rooms': rooms})


@login_required
@never_cache
@require_http_methods(['GET', 'POST'])
def admin_room_create(request):
    _admin_required(request)
    # enctype="multipart/form-data" required in template for file upload
    form = RoomForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        room = form.save()
        AuditLog.objects.create(
            user=request.user, action='ROOM_CREATE',
            details=f'Created room: {room.name}', ip_address=_ip(request),
        )
        messages.success(request, 'Room added.')
        return redirect('admin_room_list')
    return render(request, 'rooms/room_form.html', {'form': form, 'title': 'Add Room'})


@login_required
@never_cache
@require_http_methods(['GET', 'POST'])
def admin_room_edit(request, pk):
    _admin_required(request)
    room = get_object_or_404(Room, pk=pk)
    form = RoomForm(request.POST or None, request.FILES or None, instance=room)
    if request.method == 'POST' and form.is_valid():
        form.save()
        AuditLog.objects.create(
            user=request.user, action='ROOM_EDIT',
            details=f'Edited room: {room.name}', ip_address=_ip(request),
        )
        messages.success(request, 'Room updated.')
        return redirect('admin_room_list')
    return render(request, 'rooms/room_form.html', {'form': form, 'title': 'Edit Room', 'room': room})


@login_required
@never_cache
def admin_reservations(request):
    _admin_required(request)
    status_filter = request.GET.get('status', '')
    qs = Reservation.objects.select_related('guest', 'room').all()
    if status_filter in dict(Reservation.STATUS_CHOICES):
        qs = qs.filter(status=status_filter)
    page = Paginator(qs, 20).get_page(request.GET.get('page', 1))
    return render(request, 'rooms/admin_reservations.html', {
        'page': page, 'status_filter': status_filter,
        'status_choices': Reservation.STATUS_CHOICES,
    })


@login_required
@require_http_methods(['POST'])
def reservation_approve(request, pk):
    _admin_required(request)
    res = get_object_or_404(Reservation, pk=pk)
    if res.status == 'pending':
        res.status = 'confirmed'
        res.save()
        AuditLog.objects.create(
            user=request.user, action='RESERVATION_EDIT',
            details=f'Approved reservation {res.id} for {res.guest.username}',
            ip_address=_ip(request),
        )
        messages.success(request, f'Reservation approved for {res.guest.first_name or res.guest.username}.')
    else:
        messages.error(request, 'Only pending reservations can be approved.')
    return redirect('admin_reservations')


@login_required
@require_http_methods(['POST'])
def reservation_checkin(request, pk):
    _admin_required(request)
    res = get_object_or_404(Reservation, pk=pk)
    if res.status == 'confirmed':
        res.status = 'checked_in'
        res.save()
        AuditLog.objects.create(
            user=request.user, action='RESERVATION_EDIT',
            details=f'Checked in {res.guest.username} for reservation {res.id}',
            ip_address=_ip(request),
        )
        messages.success(request, f'Guest {res.guest.first_name or res.guest.username} checked in successfully.')
    else:
        messages.error(request, 'Only confirmed reservations can be checked in.')
    return redirect('admin_reservations')


@login_required
@require_http_methods(['POST'])
def reservation_checkout(request, pk):
    _admin_required(request)
    res = get_object_or_404(Reservation, pk=pk)
    if res.status == 'checked_in':
        res.status = 'checked_out'
        res.save()
        AuditLog.objects.create(
            user=request.user, action='RESERVATION_EDIT',
            details=f'Checked out {res.guest.username} for reservation {res.id}',
            ip_address=_ip(request),
        )
        messages.success(request, f'Guest {res.guest.first_name or res.guest.username} checked out successfully.')
    else:
        messages.error(request, 'Only checked-in reservations can be checked out.')
    return redirect('admin_reservations')
