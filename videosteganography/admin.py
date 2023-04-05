from django.contrib import admin
from .models import VideoMessage

# Register your models here.
# admin.site.register(VideoMessage)

class VideoMessageAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'message', 'video_file', 'password')
    list_display_links = ('id','user', 'message', 'video_file')

admin.site.register(VideoMessage, VideoMessageAdmin)