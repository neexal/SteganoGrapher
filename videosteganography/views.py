from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from moviepy.editor import VideoFileClip
from .models import VideoMessage


def index(request):
    # if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    return render(request, 'videosteganography/index.html')


@login_required
def encode(request):
    if request.method == 'POST' and request.FILES['video_file']:
        video_file = request.FILES['video_file']
        message = request.POST.get('message')
        video_message = VideoMessage.objects.create(user=request.user,message=message, video_file = video_file)
        video_message.save()
        fs = FileSystemStorage()
        filename = fs.save(video_file.name, video_file)
        video_path = fs.path(filename)
        clip = VideoFileClip(video_path)
        audio = clip.audio
        binary_message = ''.join(format(ord(i), '08b') for i in message)
        binary_message += "00000000"
        binary_message_index = 0
        audio_length = len(audio)
        for i in range(audio_length):
            if binary_message_index == len(binary_message):
                break
            binary_frame = format(audio[i], '016b')[:-2] + binary_message[binary_message_index:binary_message_index+2]
            audio[i] = int(binary_frame, 2)
            binary_message_index += 2
        new_clip = clip.set_audio(audio)
        new_clip.write_videofile(filename, codec='libx264')
        with open(filename, 'rb') as f:
            video_data = f.read()
        video_message = VideoMessage()
        video_message.filename = filename
        video_message.video_data = video_data
        video_message.save()
        return redirect('download', video_message_id=video_message.id)
    return render(request, 'videosteganography/index.html')

@login_required
def download(request, video_message_id):
    video_message = VideoMessage.objects.get(id=video_message_id)
    with open(video_message.filename, 'wb') as f:
        f.write(video_message.video_data)
    video_path = video_message.filename
    return render(request, 'videosteganography/download.html', {'video_path': video_path})

def decode(request, video_message_id):
    video_message = VideoMessage.objects.get(id=video_message_id)
    with open(video_message.filename, 'wb') as f:
        f.write(video_message.video_data)
    clip = VideoFileClip(video_message.filename)
    audio = clip.audio
    binary_message = ""
    audio_length = len(audio)
    for i in range(audio_length):
        binary_frame = format(audio[i], '016b')[-2:]
        binary_message += binary_frame
        if binary_message[-8:] == "00000000":
            break
    message = ""    
    for i in range(0, len(binary_message), 8):
        message += chr(int(binary_message[i:i+8], 2))
        if message[-1] == "\x00":
            break
    return render(request, 'videosteganography/result.html', {'message': message})



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
