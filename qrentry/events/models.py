# events/models.py

from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class TicketCategory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)  # e.g., Regular, VIP
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.category} - {self.event.title}"
