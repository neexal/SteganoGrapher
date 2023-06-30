from django.urls import path, include
from . import views

app_name = 'audiosteganography'

urlpatterns = [
    path('', views.index, name='index'),
    path('encode/', views.encode, name='encode'),
    path('decode/', views.decode, name='decode'),
    path('download/<path:encoded_file_path>/', views.download, name='download'),

]