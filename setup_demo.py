import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotelbook.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from rooms.models import Room

def run():
    print("=== GrandStay Hotel Demo Setup ===\n")

    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_user('admin', 'admin@grandstay.local', 'Admin@12345', first_name='Admin', last_name='Manager')
        p, _ = UserProfile.objects.get_or_create(user=admin)
        p.role = 'admin'; p.save()
        print("✓ Admin  → username: admin | password: Admin@12345")

    if not User.objects.filter(username='guest1').exists():
        u = User.objects.create_user('guest1', 'guest@grandstay.local', 'Guest@12345', first_name='Sarah', last_name='Lim')
        UserProfile.objects.get_or_create(user=u, defaults={'role':'guest','nationality':'Malaysian'})
        print("✓ Guest  → username: guest1 | password: Guest@12345")

    rooms = [
        {'name':'Garden View Standard','room_number':'101','room_type':'standard','price_per_night':180,'capacity':2,'floor':1,'amenities':'WiFi, TV, Air-conditioning','description':'Cozy standard room with peaceful garden view.'},
        {'name':'City View Standard',  'room_number':'102','room_type':'standard','price_per_night':200,'capacity':2,'floor':1,'amenities':'WiFi, TV, Mini-fridge','description':'Modern standard room overlooking the city skyline.'},
        {'name':'Deluxe King Room',    'room_number':'201','room_type':'deluxe',  'price_per_night':320,'capacity':2,'floor':2,'amenities':'WiFi, Smart TV, Mini-bar, Bathtub','description':'Spacious deluxe room with king bed and premium furnishings.'},
        {'name':'Deluxe Twin Room',    'room_number':'202','room_type':'deluxe',  'price_per_night':300,'capacity':3,'floor':2,'amenities':'WiFi, Smart TV, Mini-bar','description':'Elegant twin room perfect for families or colleagues.'},
        {'name':'Junior Suite',        'room_number':'301','room_type':'suite',   'price_per_night':550,'capacity':3,'floor':3,'amenities':'WiFi, Smart TV, Mini-bar, Living area, Bathtub','description':'Luxurious junior suite with a separate living area.'},
        {'name':'Grand Suite',         'room_number':'302','room_type':'suite',   'price_per_night':800,'capacity':4,'floor':3,'amenities':'WiFi, Smart TV, Full kitchen, Jacuzzi, Butler service','description':'Our most prestigious suite with panoramic city views.'},
        {'name':'Presidential Penthouse','room_number':'401','room_type':'penthouse','price_per_night':1500,'capacity':6,'floor':4,'amenities':'WiFi, Home theatre, Private pool, Full kitchen, Butler service','description':'The ultimate luxury experience atop GrandStay.'},
    ]
    for r in rooms:
        obj, created = Room.objects.get_or_create(room_number=r['room_number'], defaults={**r,'is_available':True})
        if created: print(f"✓ Room: {r['name']}")

    print("\n=== Setup complete! ===")
    print("Run: python manage.py runserver")
    print("Open: http://127.0.0.1:8000")

if __name__ == '__main__': run()
