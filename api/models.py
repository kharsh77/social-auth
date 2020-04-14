from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    phone_number = models.CharField(unique=True, max_length=20)
    meta = models.CharField(max_length=400, default="{}")
    password = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return '%s' % (self.name)
