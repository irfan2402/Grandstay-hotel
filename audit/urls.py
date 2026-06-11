from django.urls import path
from . import views
urlpatterns = [path('logs/', views.audit_log, name='audit_log')]
