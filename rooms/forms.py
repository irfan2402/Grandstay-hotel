import re
from datetime import date, timedelta
from django import forms
from .models import Room, Reservation
from .utils import validate_room_image

SAFE_TEXT_RE = re.compile(r'^[\w\s\.,!\?\-\(\)@#:\/]{0,500}$')


class ReservationForm(forms.ModelForm):
    class Meta:
        model  = Reservation
        fields = ['room', 'check_in', 'check_out', 'guests_count', 'special_requests']
        widgets = {
            'check_in':  forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'maxlength': 500}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(is_available=True)

    def clean_check_in(self):
        d = self.cleaned_data['check_in']
        if d < date.today():
            raise forms.ValidationError('Check-in cannot be in the past.')
        if d > date.today() + timedelta(days=365):
            raise forms.ValidationError('Cannot book more than 1 year in advance.')
        return d

    def clean_check_out(self):
        d  = self.cleaned_data.get('check_out')
        ci = self.cleaned_data.get('check_in')
        if d and ci:
            if d <= ci:
                raise forms.ValidationError('Check-out must be after check-in.')
            if (d - ci).days > 30:
                raise forms.ValidationError('Maximum stay is 30 nights.')
        return d

    def clean_guests_count(self):
        n    = self.cleaned_data.get('guests_count', 1)
        room = self.cleaned_data.get('room')
        if room and n > room.capacity:
            raise forms.ValidationError(f'This room fits max {room.capacity} guests.')
        return n

    def clean_special_requests(self):
        t = self.cleaned_data.get('special_requests', '').strip()
        if t and not SAFE_TEXT_RE.match(t):
            raise forms.ValidationError('Special requests contain invalid characters.')
        return t


class AdminReservationForm(forms.ModelForm):
    class Meta:
        model  = Reservation
        fields = ['room', 'check_in', 'check_out', 'guests_count', 'special_requests', 'status']
        widgets = {
            'check_in':  forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'maxlength': 500}),
        }

    def clean_special_requests(self):
        t = self.cleaned_data.get('special_requests', '').strip()
        if t and not SAFE_TEXT_RE.match(t):
            raise forms.ValidationError('Invalid characters.')
        return t


class RoomForm(forms.ModelForm):
    """
    Admin form for creating / editing rooms.

    FILE UPLOAD SECURITY (OWASP ASVS V12 / Checklist item 6):
      - Extension whitelist enforced in clean_image()
      - MIME / magic-byte check via imghdr in clean_image()
      - 5 MB size cap enforced in clean_image()
      - Filename is renamed to a random UUID by Room.image.upload_to
      - MEDIA_ROOT is set outside the web-served static tree (settings.py)
    """

    class Meta:
        model  = Room
        fields = [
            'name', 'room_number', 'room_type', 'description',
            'price_per_night', 'capacity', 'floor',
            'is_available', 'amenities', 'image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_name(self):
        n = self.cleaned_data['name'].strip()
        if not re.match(r'^[\w\s\-]{2,100}$', n):
            raise forms.ValidationError('Invalid room name.')
        return n

    def clean_room_number(self):
        rn = self.cleaned_data['room_number'].strip()
        if not re.match(r'^[A-Za-z0-9\-]{1,10}$', rn):
            raise forms.ValidationError('Invalid room number format.')
        return rn

    def clean_amenities(self):
        a = self.cleaned_data.get('amenities', '').strip()
        if a and not re.match(r'^[\w\s,\-]{0,300}$', a):
            raise forms.ValidationError('Invalid characters in amenities.')
        return a

    def clean_image(self):
        """
        Validate the uploaded room image.

        Controls applied (Manual Code Review Checklist #6):
          ✔ Extension whitelist  (.jpg/.jpeg/.png/.webp only)
          ✔ Magic-byte MIME check (imghdr — not just filename)
          ✔ Max file size        (5 MB)
          ✔ UUID rename          (handled by upload_to in model)
          ✔ Stored outside web root (MEDIA_ROOT = media_private/)
        """
        f = self.cleaned_data.get('image')
        if not f:
            return f  # field is optional — no image is fine

        # File is a new upload (InMemoryUploadedFile / TemporaryUploadedFile)
        # Skip re-validation if this is an existing stored file (no 'size' attr)
        if hasattr(f, 'size'):
            try:
                validate_room_image(f)
            except ValueError as exc:
                raise forms.ValidationError(str(exc))

        return f
