from django.shortcuts import render, redirect
from .models import TextMessage

# Create your views here.
def index(request):
    return render(request,'textsteganography/index.html')


def encode(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        password = request.POST.get('password')
        print(f"message: {message}")
        print(f"password: {password}")
        text_message = TextMessage.objects.create(message=message, password=password)
        print(f"text_message: {text_message}")
        text_message.save()
        return redirect('textsteganography:download')
    else:
        return render(request, 'textsteganography/index.html')
    
def download(request):
    return render(request,'textsteganography/download.html')