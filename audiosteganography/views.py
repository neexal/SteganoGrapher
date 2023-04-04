from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import AudioMessage
from django.core.files.storage import FileSystemStorage


# Create your views here.
def index(request):

    #if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    return render(request, 'audiosteganography/index.html')

def encode(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        audio_file = request.FILES.get('audio_file')
        audio = AudioMessage(message=message, audio_file=audio_file, user=request.user) # attach current user to audio
        audio.save()
        return redirect('audiosteganography:home')
    else:
        return render(request, 'audiosteganography/index.html')

# def encode(request):
#     user = request.user
#     if request.method == 'POST':
#         message = request.POST.get['message']
#         audio = request.FILES.get['audio']
#         password = request.POST.get['password']
#         Cpassword = request.POST.get['Cpassword']

#         # if password & Cpassword != '':
#         #     new_data = AudioMessage.objects.create(user=user, message=message, audio_file=filename)
            

#         # save the audio file
#         fs = FileSystemStorage()
#         filename = fs.save(audio.name, audio)

#         # create a new AudioMessage object
#         new_data = AudioMessage.objects.create(user="aalok", message=message, audio_file=audio, password=password)
#         new_data.save()
#     return render(request, 'audiosteganography/index.html')