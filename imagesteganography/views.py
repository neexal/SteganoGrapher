from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ImageMessage


# Create your views here.
def index(request):

    #if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    return render(request, 'imagesteganography/index.html')


def encode(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        image_file = request.FILES.get('image_file')
        image = ImageMessage(message=message, image_file=image_file, user=request.user) # attach current user to image
        image.save()
        return redirect('imagesteganography:download')
    else:
        return render(request, 'imagesteganography/index.html')

@login_required
def download(request):
    return render(request, 'imagesteganography/download.html')
