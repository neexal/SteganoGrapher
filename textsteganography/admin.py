from django.contrib import admin
from .models import TextMessage

# Register your models here.
# admin.site.register(TextMessage)

class TextMessageAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'message', 'text_file', 'password')
    list_display_links = ('id','user', 'message', 'text_file')

admin.site.register(TextMessage, TextMessageAdmin)