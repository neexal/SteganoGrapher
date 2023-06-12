from django.urls import path, include
from . import views

app_name = 'videosteganography'

urlpatterns = [
    path('', views.index, name='index'),
    path('encode/', views.encode, name='encode'),
    path('decode/', views.decode, name='decode'),
    path('download/<video_message_id>', views.download, name='download'),
]
