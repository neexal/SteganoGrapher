from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import VideoMessage


# Create your views here.
def index(request):

    # if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    return render(request, 'videosteganography/index.html')


@login_required
def encode(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        video_file = request.FILES.get('video_file')
        # attach current user to video
        video = VideoMessage(
            message=message, video_file=video_file, user=request.user)
        video.save()
        return redirect('videosteganography:download')
    else:
        return render(request, 'videosteganography/index.html')


@login_required
def download(request):
    return render(request, 'videosteganography/download.html')


def decode(request):
    pass

# def encode(request):
#     user = request.user
#     if request.method == 'POST':
#         message = request.POST.get['message']
#         video = request.FILES.get['video']
#         password = request.POST.get['password']
#         Cpassword = request.POST.get['Cpassword']

#         # if password & Cpassword != '':
#         #     new_data = videoMessage.objects.create(user=user, message=message, video_file=filename)


#         # save the video file
#         fs = FileSystemStorage()
#         filename = fs.save(video.name, video)

#         # create a new videoMessage object
#         new_data = videoMessage.objects.create(user="aalok", message=message, video_file=video, password=password)
#         new_data.save()
#     return render(request, 'videosteganography/index.html')
