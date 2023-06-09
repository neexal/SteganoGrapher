from django.urls import path, include
from . import views

app_name = 'imagesteganography'

urlpatterns = [
    path('', views.index, name='index'),
    path('encode/', views.encode, name='encode'),
    path('decode/', views.decode, name='decode'),
    path('download/', views.download, name='download'),
]
