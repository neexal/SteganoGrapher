from django.db import models

# Create your models here.
class TextMessage(models.Model):
    message = models.TextField(max_length=10000)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.message