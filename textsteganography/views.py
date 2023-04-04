from django.shortcuts import render
from .models import TextMessage

# Create your views here.
def index(request):
    return render(request,'textsteganography/index.html')


def encode(request):
    if request.method == 'POST':
        message = request.POST('message')
        password = request.POST('password')

        text = TextMessage.objects.create(message=message, password=password)
        text.save()

    return render(request,'textsteganography/test.html')