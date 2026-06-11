from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',                                     views.dashboard,              name='dashboard'),
    path('rooms/',                                         views.room_list,              name='room_list'),
    path('reservations/',                                  views.reservation_list,       name='reservation_list'),
    path('reservations/new/',                              views.reservation_create,     name='reservation_create'),
    path('reservations/new/<int:room_pk>/',                views.reservation_create,     name='reservation_create_room'),
    path('reservations/<uuid:pk>/',                        views.reservation_detail,     name='reservation_detail'),
    path('reservations/<uuid:pk>/edit/',                   views.reservation_edit,       name='reservation_edit'),
    path('reservations/<uuid:pk>/cancel/',                 views.reservation_cancel,     name='reservation_cancel'),

    # Management URLs — using manage/ prefix to avoid conflict with Django /admin/ panel
    path('manage/rooms/',                                  views.admin_room_list,        name='admin_room_list'),
    path('manage/rooms/new/',                              views.admin_room_create,      name='admin_room_create'),
    path('manage/rooms/<int:pk>/edit/',                    views.admin_room_edit,        name='admin_room_edit'),
    path('manage/reservations/',                           views.admin_reservations,     name='admin_reservations'),
    path('manage/reservations/<uuid:pk>/approve/',         views.reservation_approve,    name='reservation_approve'),
    path('manage/reservations/<uuid:pk>/checkin/',         views.reservation_checkin,    name='reservation_checkin'),
    path('manage/reservations/<uuid:pk>/checkout/',        views.reservation_checkout,   name='reservation_checkout'),
]