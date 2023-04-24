from django.db import models
from django.conf import settings

# Create your models here.
class ImageMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(max_length=10000)
    image_file = models.FileField(upload_to='image/')
    password = models.CharField(max_length=100, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.message



class DecodeImageMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image_file = models.FileField(upload_to='image/')
    password = models.CharField(max_length=100, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user
    