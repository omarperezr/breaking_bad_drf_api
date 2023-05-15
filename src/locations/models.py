from django.db import models

from characters.models import Character


class Location(models.Model):
    id = models.BigAutoField(primary_key=True)
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="locations"
    )
    timestamp = models.DateTimeField()
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
