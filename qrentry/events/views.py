# events/views.py
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import Event,TicketCategory    
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage



def home(request):
   events = Event.objects.filter(is_active=True).order_by('date')
   return render(request, 'home.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event})

def book_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    tickets = TicketCategory.objects.filter(event=event)
    return render(request, 'book_ticket.html', {'event': event, 'tickets': tickets})


def confirm_booking(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        tickets = TicketCategory.objects.filter(event=event)
        selected_tickets = []

        for ticket in tickets:
            qty = int(request.POST.get(f"ticket_{ticket.id}", 0))
            if qty > 0:
                selected_tickets.append({
                    'category': ticket.category,
                    'price': ticket.price,
                    'quantity': qty,
                    'subtotal': ticket.price * qty
                })

        total_price = sum(item['subtotal'] for item in selected_tickets)

        return render(request, 'confirm_booking.html', {
            'event': event,
            'selected_tickets': selected_tickets,
            'total': total_price,
        })

    # If GET request, redirect back to booking page or show empty
    return render(request, 'book_ticket.html', {
        'event': event,
        'tickets': TicketCategory.objects.filter(event=event),
    })


import base64
import qrcode
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Event

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

@login_required
def payment(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        # Simulate booking ID
        booking_id = f"EVT{event.id}BK001"  # Replace with real booking ID logic

        # Generate QR code
        qr_img_bytes = generate_qr_code(booking_id)

        # Convert to base64 for success page
        qr_code_base64 = base64.b64encode(qr_img_bytes).decode('utf-8')

        # Compose email
        subject = f"🎟️ Your Ticket for {event.title}"
        message = f"""
Hi {request.user.first_name or request.user.username},

🎟️ Thank you for booking your ticket for "{event.title}"!

📅 Date: {event.date}
⏰ Time: {event.time}
📍 Venue: {event.venue}

🆔 Booking ID: {booking_id}

Attached is your QR code ticket. Please show it at the venue for entry.

Regards,
Eventora Team
        """

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[request.user.email],
        )

        email.attach(f"{booking_id}.png", qr_img_bytes, 'image/png')
        email.send()

        return render(request, 'payment_success.html', {
            'event': event,
            'booking_id': booking_id,
            'qr_code_base64': qr_code_base64,
        })

    return render(request, 'payment.html', {'event': event})


from django.contrib.auth import login
from .forms import CustomUserRegistrationForm
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "🎉 Account created successfully. You're now logged in!")
            return redirect('home')
        else:
            messages.error(request, "There was an error with your registration form.")
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'register.html', {'form': form})

from django.contrib.auth.views import LoginView
from django.contrib import messages

class CustomLoginView(LoginView):
    def form_invalid(self, form):
        messages.error(self.request, "❌ Invalid username or password.")
        return super().form_invalid(form)
