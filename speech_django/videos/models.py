from django.db import models

# Create your models here.


class Videos(models.Model):
    URL = models.CharField(max_length=200)
    URI = models.CharField(max_length=200)
