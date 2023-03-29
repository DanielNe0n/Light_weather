from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField("City", max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Cities'
        verbose_name = 'City'
