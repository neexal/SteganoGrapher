"""Steganography URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


admin.site.site_header = 'SteganoGrapher Dashboard'                   
admin.site.index_title = 'Welcome to SteganoGrapher'  
admin.site.site_title = 'SteganoGrapher Dashboard' 




urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('landing_page.urls', namespace='landing_page')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    # path('accounts/', include('accounts.urls', namespace='accounts')),
    path('', include('accounts.urls', namespace='accounts')),
    path('audiosteganography/', include('audiosteganography.urls', namespace='audiosteganography')),
    path('textsteganography/', include('textsteganography.urls', namespace='textsteganography')),
    path('imagesteganography/', include('imagesteganography.urls', namespace='imagesteganography')),
    path('videosteganography/', include('videosteganography.urls', namespace='videosteganography')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
