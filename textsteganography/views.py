from django.shortcuts import render, redirect
from .models import TextMessage

# Create your views here.
def index(request):
    return render(request,'textsteganography/index.html')


def encode(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        password = request.POST.get('password')
        text_file = request.FILES.get('text_file')
        text_message = TextMessage.objects.create(user=request.user,message=message, text_file = text_file)
        text_message.save()
        return redirect('textsteganography:download')
    else:
        return render(request, 'textsteganography/index.html')
    
def download(request):
    return render(request,'textsteganography/download.html')


def decode(request):
    pass