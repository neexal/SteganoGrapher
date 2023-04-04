from django.urls import path, include
from . import views

app_name = 'textsteganography'

urlpatterns = [
    path('', views.index, name='index'),
    path('encode/', views.encode, name='encode'),
    path('download/', views.download, name='download'),
]
