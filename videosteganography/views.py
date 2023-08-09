from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from moviepy.editor import VideoFileClip
from moviepy.audio.AudioClip import AudioArrayClip  
from .models import VideoMessage
import io
import os
import struct
import numpy as np
from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.conf import settings
from accounts.email_utils import send_email_with_attachment
from pathlib import Path  # Import the Path class
import mimetypes


def index(request):

    #if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    return render(request, 'videosteganography/index.html')

import math
import os
import shutil
from subprocess import call, STDOUT
import cv2
from stegano import lsb
from django.shortcuts import render, redirect
from .models import VideoMessage

def encode(request):
    def split_string(split_str, count=10):
        per_c = math.ceil(len(split_str) / count)
        c_cout = 0
        out_str = ''
        split_list = []
        for s in split_str:
            out_str += s
            c_cout += 1
            if c_cout == per_c:
                split_list.append(out_str)
                out_str = ''
                c_cout = 0
        if c_cout != 0:
            split_list.append(out_str)
        return split_list

    def frame_extraction(video):
        if not os.path.exists("./temp"):
            os.makedirs("temp")
        temp_folder = "./temp"
        print("[INFO] temp directory is created")
        vidcap = cv2.VideoCapture(video)
        count = 0
        while True:
            success, image = vidcap.read()
            if not success:
                break
            cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
            count += 1

    def encode_string(input_string, root="./temp/"):
        split_string_list = split_string(input_string)
        for i in range(0, len(split_string_list)):
            f_name = "{}{}.png".format(root, i)
            secret_enc = lsb.hide(f_name, split_string_list[i])
            secret_enc.save(f_name)
            print("[INFO] frame {} holds {}".format(f_name, lsb.reveal(f_name)))
        print("[INFO] The message is stored in the Embedded_Video.mp4 file")

    def clean_temp(path="./temp"):
        if os.path.exists(path):
            shutil.rmtree(path)
            print("[INFO] temp files are cleaned up")

    if request.method == 'POST':
        video_file = request.FILES['video_file']
        message = request.POST.get('message')
        video_path = os.path.join(settings.MEDIA_ROOT, 'video', video_file.name)
        with open(video_path, 'wb+') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)
        
        frame_extraction(video_path)
        call(["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", "temp/audio.mp3", "-y"], stdout=open(os.devnull, "w"),
             stderr=STDOUT)
        encode_string(message)
        call(["ffmpeg", "-i", "temp/%d.png", "-vcodec", "png", "temp/Embedded_Video.mp4", "-y"],
             stdout=open(os.devnull, "w"), stderr=STDOUT)
        call(["ffmpeg", "-i", "temp/Embedded_Video.mp4", "-i", "temp/audio.mp3", "-codec", "copy", "Embedded_Video.mp4",
              "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)
        
        os.remove(video_path)
        os.rename("Embedded_Video.mp4", video_path)
        clean_temp()
        print("[INFO] FILE LOCATION: {}".format(video_path))
        print("=" * 100)

        # Save the encoded video file in the database
        video_message = VideoMessage.objects.create(user=request.user, message=message, video_file=video_path)
        video_message.save()
        if request.method == 'POST' and 'send_email' in request.POST:
            subject = 'Encoded Message'
            em_message = 'Please find the attached file.'
            from_email = 'testdjango890@gmail.com'  # Replace with your email address
            to_email = request.POST.get('to_email')
            recipient_list = [to_email]  # Replace with the recipient's email address

            # Generate the FileResponse for the encoded image
            encoded_video_response = FileResponse(open(video_path, 'rb'), content_type=mimetypes.guess_type(video_path)[0])
            encoded_video_response['Content-Disposition'] = 'attachment; filename="encoded_output.mp4"'

            # Save the FileResponse to a temporary file
            temp_file_path = Path(settings.MEDIA_ROOT) / 'temp_encoded_output.mp4'
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in encoded_video_response.streaming_content:
                    temp_file.write(chunk)

            # Send the email with the temporary file as an attachment
            send_email_with_attachment(subject, em_message, from_email, recipient_list, temp_file_path)

            # Clean up: Remove the temporary file
            temp_file_path.unlink()

            return HttpResponse('Email sent with encoded audio attachment.')
        
        else:
            return redirect('videosteganography:download', video_message_id=video_message.id)
    return render(request, 'videosteganography/index.html')

import os
import shutil
import cv2
from subprocess import call, STDOUT
from django.shortcuts import render
from stegano import lsb

def split_string(split_str, count=10):
    per_c = math.ceil(len(split_str) / count)
    c_cout = 0
    out_str = ''
    split_list = []
    for s in split_str:
        out_str += s
        c_cout += 1
        if c_cout == per_c:
            split_list.append(out_str)
            out_str = ''
            c_cout = 0
    if c_cout != 0:
        split_list.append(out_str)
    return split_list

def frame_extraction(video):
    if not os.path.exists("./temp"):
        os.makedirs("temp")
    temp_folder = "./temp"
    print("[INFO] temp directory is created")
    vidcap = cv2.VideoCapture(video)
    count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1
import math
import os
import shutil
from subprocess import call, STDOUT
import cv2
from stegano import lsb

from django.shortcuts import render

def split_string(split_str, count=10):
    per_c = math.ceil(len(split_str) / count)
    c_cout = 0
    out_str = ''
    split_list = []
    for s in split_str:
        out_str += s
        c_cout += 1
        if c_cout == per_c:
            split_list.append(out_str)
            out_str = ''
            c_cout = 0
    if c_cout != 0:
        split_list.append(out_str)
    return split_list

def frame_extraction(video):
    if not os.path.exists("./temp"):
        os.makedirs("temp")
    temp_folder = "./temp"
    print("[INFO] temp directory is created")
    vidcap = cv2.VideoCapture(video)
    count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1

def encode_string(input_string, root="./temp/"):
    split_string_list = split_string(input_string)
    for i in range(0, len(split_string_list)):
        f_name = "{}{}.png".format(root, i)
        secret_enc = lsb.hide(f_name, split_string_list[i])
        secret_enc.save(f_name)
        print("[INFO] frame {} holds {}".format(f_name, lsb.reveal(f_name)))
    print("[INFO] The message is stored in the Embedded_Video.mp4 file")

def clean_temp(path="./temp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] temp files are cleaned up")

def decode(request):
    if request.method == 'POST':
        video_file = request.FILES['video_file']

        # Save the uploaded video file to a temporary location
        temp_folder = os.path.join(settings.MEDIA_ROOT, "temp")
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)
        video_path = os.path.join(temp_folder, video_file.name)
        with open(video_path, 'wb') as destination:
            for chunk in video_file.chunks():
                destination.write(chunk)

        frame_extraction(video_path)
        secret = []
        root = "./temp/"
        a = ''
        try:
            for i in range(0, len(os.listdir(root)) - 1):
                f_name = "{}{}.png".format(str(root), str(i))
                secret_dec = lsb.reveal(f_name)
                if secret_dec is None:
                    break
                secret.append(secret_dec)
        except IndexError as e:
            print('')
        a = a.join([i for i in secret])
        print("[*] The Encoded data was:{}".format(a))
        print("")
        clean_temp()
        print("="*100)

        return render(request, 'accounts/result.html', {'message': a})

    return render(request, 'videosteganography/decode.html')
 
@login_required
def download(request, video_message_id):
    video_message = VideoMessage.objects.get(id=video_message_id)
    video_file_path = os.path.join(settings.MEDIA_ROOT, f'{video_message.video_file}')
    response = FileResponse(open(video_file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{video_message.video_file}"'
    return response