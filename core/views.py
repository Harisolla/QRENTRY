from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages,auth
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth.models import User
from django.http import QueryDict
from django.core.paginator import Paginator
from .forms import ChooseRoleForm

import uuid
import json
import os

from .models import Event, Booking, Payment, CheckinLog, Profile
from .forms import SignUpForm, EventForm
from core.utils import generate_qr_code
from django.utils import timezone

# Home
def home(request):
    today = timezone.now().date()
    events = Event.objects.filter(date__gte=today).order_by('date')[:6]
    return render(request, "home.html", {"events": events})


# Event list and detail views
def event_list(request):
    events = Event.objects.all()

    # Filters
    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    price_max = request.GET.get('price_max')

    if search:
        events = events.filter(name__icontains=search)

    if date_from:
        events = events.filter(date__gte=date_from)

    if date_to:
        events = events.filter(date__lte=date_to)

    if price_max:
        events = events.filter(price__lte=price_max)

    # Pagination
    paginator = Paginator(events, 6)  # 6 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Preserve query params except 'page'
    querydict = request.GET.copy()
    if 'page' in querydict:
        querydict.pop('page')
    querystring = querydict.urlencode()

    return render(request, 'event_list.html', {
        'events': page_obj,
        'querystring': querystring,  # Pass to template
    })


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'event_detail.html', {'event': event})


from django.contrib.auth.decorators import login_required

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings.html', {'bookings': bookings})


# API: All Events
def api_event_list(request):
    events = Event.objects.all().values('id', 'name', 'description', 'location', 'date', 'capacity')
    return JsonResponse(list(events), safe=False)

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event})

# API: Single Event
def api_event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    data = {
        'id': event.id,
        'name': event.name,
        'description': event.description,
        'location': event.location,
        'date': event.date,
        'capacity': event.capacity,
    }
    return JsonResponse(data)


from django.core.mail import send_mail
from django.conf import settings

def book_ticket(request, event_id):
    if request.method == 'POST':
        try:
            user = request.user
            event = Event.objects.get(pk=event_id)
            ticket_id = str(uuid.uuid4())[:8]

            booking = Booking.objects.create(
                user=user,
                event=event,
                status='PENDING',
                ticket_id=ticket_id
            )

            # ✅ Generate QR code
            qr_filename = f'{booking.ticket_id}.png'
            booking.qr_code_path = generate_qr_code(data=booking.ticket_id, filename=qr_filename)
            booking.save()

            # ✅ Email sending
            if user.email:
                print("User email:", user.email)
                print("Preparing to send confirmation email...")

                qr_url = request.build_absolute_uri('/media/' + booking.qr_code_path)

                send_mail(
                    subject=f"🎫 Your Ticket for {event.title}",
                    message=f"""Hi {user.username},

Your ticket booking was successful!

Event: {event.title}
Ticket ID: {ticket_id}
Status: {booking.status}

QR Code: {qr_url}

Thank you for using QrEntry!""",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                print("✅ Email sent successfully to", user.email)

            return redirect('booking_success', booking_id=booking.id)

        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Event not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})



# ✅ Success page
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, 'booking_success.html', {'booking': booking})


# ✅ Signup View with Password Confirmation + Role
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        role = request.POST.get('role')

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
            messages.success(request, "Signup successful!")
            return redirect('login')
        else:
            messages.error(request, "Signup failed. Please check the form.")
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})





# ✅ Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Allow login using either username or email
        from django.contrib.auth.models import User
        user = None
        if '@' in username:  # if email
            try:
                user_obj = User.objects.get(email=username)
                user = auth.authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username/email or password.")  # THIS triggers the alert

    return render(request, 'login.html')

# ✅ Logout View
def logout_view(request):
    logout(request)
    return redirect('login')


# ✅ Create Event (organiser only)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EventForm

@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)  # <-- Add request.FILES
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user  # Set organizer automatically
            event.save()
            messages.success(request, "Event created successfully!")
            return redirect('event_list')  # Redirect to event list
        else:
            print(form.errors)  # For debugging
            messages.error(request, "Please correct the errors below.")
    else:
        form = EventForm()

    return render(request, "create_event.html", {"form": form})



# ✅ Download QR Code
def download_qr_code(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.qr_code_path:
        file_path = os.path.join(settings.MEDIA_ROOT, booking.qr_code_path)
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), content_type='image/png')
        else:
            return JsonResponse({'success': False, 'error': 'QR file not found'})
    return JsonResponse({'success': False, 'error': 'QR not assigned'})


# ✅ Mark Attendance (API)
def mark_attendance(request):
    if request.method == "POST":
        ticket_id = request.POST.get("ticket_id")

        if not ticket_id:
            return render(request, "attendance.html", {
                "error": True,
                "message": "Please enter a Ticket ID."
            })

        try:
            booking = Booking.objects.get(ticket_id=ticket_id)
            booking.status = "ATTENDED"
            booking.save()

            return render(request, "attendance.html", {
                "success": True,
                "message": "Attendance marked successfully!"
            })
        except Booking.DoesNotExist:
            return render(request, "attendance.html", {
                "error": True,
                "message": "Ticket not found!"
            })

    return render(request, "attendance.html")


# ✅ Scan Attendance (HTML page)
@csrf_exempt
def scan_attendance(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        try:
            booking = Booking.objects.get(ticket_id=ticket_id)
            if booking.status != 'ATTENDED':
                booking.status = 'ATTENDED'
                booking.save()
                return render(request, 'scan_attendance.html', {'status': 'success', 'ticket_id': ticket_id})
            else:
                return render(request, 'scan_attendance.html', {'status': 'fail', 'ticket_id': ticket_id})
        except Booking.DoesNotExist:
            return render(request, 'scan_attendance.html', {'status': 'fail', 'ticket_id': ticket_id})
    
    return render(request, 'scan_attendance.html')


# ✅ Scan QR Camera Page
def scan_qr_camera(request):
    return render(request, 'scan_qr.html')


# ✅ Fake Payment for Dev Testing
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Event, Booking
from .utils import generate_qr_code  # Update this import if needed
import uuid
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

@csrf_exempt
@login_required
def fake_payment(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        user = request.user
        ticket_id = str(uuid.uuid4())[:8]

        # ✅ Create booking
        booking = Booking.objects.create(
            user=user,
            event=event,
            ticket_id=ticket_id,
            status='PENDING'
        )

        # ✅ Generate QR code image
        qr_filename = f'{ticket_id}.png'
        booking.qr_code_path = generate_qr_code(data=ticket_id, filename=qr_filename)
        booking.save()

        # ✅ Send email with PDF ticket
        if user.email:
            print("Preparing to send email with PDF...")

            # Step 1: Generate the PDF
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)

            # Ticket text
            p.setFont("Helvetica-Bold", 14)
            p.drawString(100, 750, "🎟️ QrEntry Ticket Confirmation")
            p.setFont("Helvetica", 12)
            p.drawString(100, 720, f"Name: {user.username}")
            p.drawString(100, 700, f"Event: {event.name}")
            p.drawString(100, 680, f"Ticket ID: {ticket_id}")
            p.drawString(100, 660, f"Status: {booking.status}")
            p.drawString(100, 640, "Please show this ticket at entry.")

            # Step 2: Add QR code image to PDF
            qr_path = os.path.join(settings.MEDIA_ROOT, booking.qr_code_path)
            if os.path.exists(qr_path):
                p.drawImage(ImageReader(qr_path), 100, 500, width=150, height=150)

            p.showPage()
            p.save()
            buffer.seek(0)

            # Step 3: Create email
            email = EmailMessage(
                subject=f"🎫 Your Ticket for {event.name}",
                body=f"""Hi {user.username},

Your ticket booking was successful!

Please find your ticket attached as a PDF.

Event: {event.name}
Ticket ID: {ticket_id}
Status: {booking.status}

Show the QR code at the event entry.

Thank you for using QrEntry!""",
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
            )

            # Step 4: Attach the PDF
            email.attach(f"{ticket_id}_ticket.pdf", buffer.read(), "application/pdf")
            email.send()

            print("✅ Email with PDF sent to:", user.email)

        # ✅ Redirect to booking success page
        return redirect('booking_success', booking_id=booking.id)

    return render(request, 'payment_page.html', {'event': event})



# ✅ Payment Webhook Handler (Simulated)
@csrf_exempt
def payment_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_id = data.get('ticket_id')
            payment_status = data.get('status')

            booking = Booking.objects.get(ticket_id=ticket_id)
            if payment_status == 'SUCCESS':
                booking.status = 'CONFIRMED'
                booking.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


# ✅ Attendance HTML form view
@csrf_exempt
def attendance_form(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        try:
            booking = Booking.objects.get(ticket_id=ticket_id)
            booking.status = 'ATTENDED'
            booking.save()
            return render(request, 'attendance.html', {'success': True, 'message': f"Attendance marked for {ticket_id}"})
        except Booking.DoesNotExist:
            return render(request, 'attendance.html', {'error': True, 'message': "Ticket not found"})
    return render(request, 'attendance.html')


@login_required
def organizer_bookings(request):
    bookings = Booking.objects.filter(event__organizer=request.user)
    return render(request, 'organizer_bookings.html', {'bookings': bookings})

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
from django.conf import settings
from .models import Booking

def download_ticket_pdf(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    pdf_path = os.path.join(settings.MEDIA_ROOT, f"{booking.ticket_id}_ticket.pdf")

    # Generate PDF if not already saved
    if not os.path.exists(pdf_path):
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, 750, "🎟️ QrEntry Ticket Confirmation")
        p.setFont("Helvetica", 12)
        p.drawString(100, 720, f"Name: {booking.user.username}")
        p.drawString(100, 700, f"Event: {booking.event.name}")
        p.drawString(100, 680, f"Ticket ID: {booking.ticket_id}")
        p.drawString(100, 660, f"Status: {booking.status}")
        p.showPage()
        p.save()

        with open(pdf_path, 'wb') as f:
            f.write(buffer.getvalue())

    return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=f"{booking.ticket_id}_ticket.pdf")


# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def choose_role(request):
    user = request.user
    profile = getattr(user, 'profile', None)

    # Make sure profile exists
    if not profile:
        from .models import Profile
        profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['organiser', 'participant']:
            profile.role = role
            profile.save()

            # Remove session flag if any
            if 'ask_role' in request.session:
                del request.session['ask_role']

            return redirect('/')  # Redirect after selecting role
        else:
            return render(request, 'choose_role.html', {
                'error': 'Please select a valid role.'
            })

    return render(request, 'choose_role.html')
