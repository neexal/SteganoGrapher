from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from moviepy.editor import VideoFileClip
from .models import VideoMessage
import io, os
from django.conf import settings


def index(request):
    # if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    return render(request, 'videosteganography/index.html')


import os
import struct
import io
import numpy as np
from moviepy.editor import VideoFileClip, concatenate
from moviepy.audio.AudioClip import AudioArrayClip
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.conf import settings
from .models import VideoMessage

@login_required
def encode(request):
    if request.method == 'POST' and request.FILES['video_file']:
        video_file = request.FILES['video_file']
        message = request.POST.get('message')
        video_path = os.path.join(settings.MEDIA_ROOT, 'video', video_file.name)
        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        video_message = VideoMessage.objects.create(user=request.user, message=message, video_file=video_file.name)
        video_message.save()

        clip = VideoFileClip(video_path)
        audio = clip.audio
        binary_message = ''.join(format(ord(i), '08b') for i in message)
        binary_message += "00000000"
        binary_message_index = 0
        audio_frames = []
        for frame in audio.iter_frames():
            if binary_message_index == len(binary_message):
                break
            binary_frame = []
            for value in frame:
                binary_value = format(struct.unpack('!I', struct.pack('!f', value))[0], '032b')
                binary_frame.append(binary_value)
            binary_frame[-1] = binary_frame[-1][:-2] + binary_message[binary_message_index:binary_message_index+2]
            modified_frame = [int(binary_frame_value, 2) for binary_frame_value in binary_frame]
            audio_frames.append(modified_frame)
            binary_message_index += 2
        new_audio = AudioArrayClip(np.array(audio_frames), fps=audio.fps)
        new_clip = clip.set_audio(new_audio)

        # Save the modified clip to a BytesIO object
        output = io.BytesIO()
        output_path = os.path.join(settings.MEDIA_ROOT, 'video', f'{video_file.name}.mp4')
        new_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

        # Save the BytesIO object to the video_file field of the VideoMessage model
        video_message.video_file.save(f'{video_file.name}.mp4', ContentFile(output.getvalue()))

        return redirect('videosteganography:download', video_message_id=video_message.id)
    return render(request, 'videosteganography/index.html')






import os
from django.shortcuts import render
from django.http import FileResponse
from django.conf import settings
from .models import VideoMessage

@login_required
def download(request, video_message_id):
    video_message = VideoMessage.objects.get(id=video_message_id)
    video_file_path = os.path.join(settings.MEDIA_ROOT, f'{video_message.video_file}')
    response = FileResponse(open(video_file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{video_message.video_file}"'
    return response



import os
from django.shortcuts import render, redirect
from django.conf import settings
from .models import VideoMessage
from moviepy.editor import VideoFileClip

@login_required
def decode(request):
    if request.method == 'POST' and request.FILES.get('video_file'):
        video_file = request.FILES['video_file']
        video_message = VideoMessage.objects.create(user=request.user, video_file=video_file)
        video_message.save()

        video_path = os.path.join(settings.MEDIA_ROOT, 'video', video_file.name)
        clip = VideoFileClip(video_path)
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
            message += chr(int(binary_message[i:i + 8], 2))
            if message[-1] == "\x00":
                break

        return render(request, 'videosteganography/result.html', {'message': message})

    return render(request, 'videosteganography/decode.html')


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
