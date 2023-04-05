from django.contrib import admin
from .models import ImageMessage

# Register your models here.
# admin.site.register(ImageMessage)

class ImageMessageAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'message', 'image_file', 'password')
    list_display_links = ('id','user', 'message', 'image_file')

admin.site.register(ImageMessage, ImageMessageAdmin)