from django.contrib import admin
from .models import Event, TicketCategory

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'venue', 'is_active')

@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('category', 'price', 'event')
