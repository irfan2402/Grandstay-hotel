from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('rooms.urls')),
    path('audit/', include('audit.urls')),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
]

handler400 = 'hotelbook.error_views.bad_request'
handler403 = 'hotelbook.error_views.permission_denied'
handler404 = 'hotelbook.error_views.page_not_found'
handler500 = 'hotelbook.error_views.server_error'
