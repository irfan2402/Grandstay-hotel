import uuid
from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    ROOM_TYPES = [
        ('standard',  'Standard Room'),
        ('deluxe',    'Deluxe Room'),
        ('suite',     'Suite'),
        ('penthouse', 'Penthouse'),
    ]
    name         = models.CharField(max_length=100)
    room_number  = models.CharField(max_length=10, unique=True)
    room_type    = models.CharField(max_length=20, choices=ROOM_TYPES, default='standard')
    description  = models.TextField(blank=True, max_length=1000)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    capacity     = models.PositiveIntegerField(default=2)
    floor        = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    amenities    = models.CharField(max_length=300, blank=True, help_text='Comma-separated, e.g. WiFi, TV, Mini-bar')
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room_number} — {self.name}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in','Checked In'),
        ('checked_out','Checked Out'),
        ('cancelled', 'Cancelled'),
    ]
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    room         = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    check_in     = models.DateField()
    check_out    = models.DateField()
    guests_count = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True, max_length=500)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Reservation {self.id} — {self.guest.username} — {self.room}"

    def nights(self):
        return (self.check_out - self.check_in).days

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            nights = (self.check_out - self.check_in).days
            self.total_price = self.room.price_per_night * nights
        super().save(*args, **kwargs)
