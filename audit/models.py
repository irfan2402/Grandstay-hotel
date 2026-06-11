from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN','Login'), ('LOGIN_FAIL','Failed Login'), ('LOGOUT','Logout'),
        ('REGISTER','Register'), ('PROFILE_UPDATE','Profile Update'),
        ('RESERVATION_CREATE','Reservation Created'), ('RESERVATION_EDIT','Reservation Edited'),
        ('RESERVATION_CANCEL','Reservation Cancelled'),
        ('ROOM_CREATE','Room Created'), ('ROOM_EDIT','Room Edited'),
    ]
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action     = models.CharField(max_length=30, choices=ACTION_CHOICES)
    details    = models.TextField(blank=True, max_length=500)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.action}"
