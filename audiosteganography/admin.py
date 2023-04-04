from django.contrib import admin
from .models import AudioMessage

# Register your models here.
# admin.site.register(AudioMessage)

class AudioMessageAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'message', 'audio_file', 'password')
    list_display_links = ('id','user', 'message', 'audio_file')

admin.site.register(AudioMessage, AudioMessageAdmin)