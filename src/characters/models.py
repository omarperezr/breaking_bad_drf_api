from django.db import models


class Character(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    occupation = models.CharField(max_length=255)
    is_suspect = models.BooleanField(default=False)
