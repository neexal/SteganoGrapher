
from django.contrib.auth.decorators import login_required
from .models import AudioMessage
import os
import wave
from django.shortcuts import render, redirect, HttpResponse, reverse
from django.http import FileResponse
from django.core.files.storage import FileSystemStorage



# Create your views here.
def index(request):
    #if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    return render(request, 'audiosteganography/index.html')



@login_required

def encode(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        audio_file = request.FILES.get('audio_file')
        audio_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'input.wav')

        # Save the uploaded audio file
        with open(audio_path, 'wb') as file:
            for chunk in audio_file.chunks():
                file.write(chunk)

        def encode_audio(input_audio, output_audio, message):
            # Open the input audio file
            audio = wave.open(input_audio, mode='rb')
            frames = audio.readframes(audio.getnframes())
            frame_list = list(frames)
            frame_byte = bytearray(frame_list)

            # Encode the message in the audio frames
            message += '*^*^*'  # Add secret key
            results = []
            for char in message:
                bits = bin(ord(char))[2:].zfill(8)
                results.extend([int(bit) for bit in bits])

            index = 0
            for i in range(len(results)):
                byte = bin(frame_byte[index])[2:].zfill(8)
                if byte[-2] == '0':
                    frame_byte[index] = (frame_byte[index] & 253)
                else:
                    frame_byte[index] = (frame_byte[index] & 253) | 2
                frame_byte[index] = (frame_byte[index] & 254) | results[i]
                index += 1

            # Save the encoded audio file
            with wave.open(output_audio, 'wb') as encoded_audio:
                encoded_audio.setparams(audio.getparams())
                encoded_audio.writeframes(frame_byte)

            audio.close()

        encoded_audio_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'output.wav')
        encode_audio(audio_path, encoded_audio_path, message)
        
        # encoded_file_path = os.path.relpath(encoded_audio_path, settings.MEDIA_ROOT)
        # download_link = reverse('audiosteganography:download', kwargs={'encoded_file_path': encoded_file_path})
        # return redirect('audiosteganography:download', encoded_file_path='audio/output.wav')
        return redirect('audiosteganography:download', encoded_file_path=encoded_audio_path)


        # # Redirect to the download page
        # context={
        #     "message": download_link
        # }
        # return redirect('audiosteganography:download', context)
    else:
        return render(request, 'audiosteganography/index.html')
    
from django.http import HttpResponse, Http404
import mimetypes
import os 
@login_required
def download(request, encoded_file_path):
    # Get the absolute file path
    file_path = os.path.join(settings.MEDIA_ROOT, encoded_file_path)

    # Check if the file exists
    if os.path.exists(file_path):
        # Set the appropriate content type
        content_type, _ = mimetypes.guess_type(file_path)
        response = HttpResponse(content_type=content_type)

        # Set the file attachment headers
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)

        # Open the file in binary mode and read the content
        with open(file_path, 'rb') as file:
            response.write(file.read())

        return response
    else:
        raise Http404("The requested file does not exist.")


@login_required
def decode(request):
    if request.method == 'POST':
        # Get the audio file from the form
        audio_file = request.FILES.get('audio_file')

        try:
            # Open the audio file using the wave module
            song = wave.open(audio_file, mode='rb')
            nframes = song.getnframes()
            frames = song.readframes(nframes)
            frame_list = list(frames)
            frame_byte = bytearray(frame_list)

            # Get the binary message from the audio file by reading the least significant bit of each audio frame
            message = ''
            for i in range(0, len(frame_byte), 1):
                res = bin(frame_byte[i])[2:].zfill(8)
                message += res[len(res) - 1]

            # Split the binary message using the delimiter
            message = message.split('*^*^*')[0]

            # Convert the binary message to ASCII characters
            message = ''.join(chr(int(message[i:i+8], 2)) for i in range(0, len(message), 8))

            # Render the success page with the decoded message
            context = {'message': message}
            return render(request, 'audiosteganography/result.html', context)

        except Exception as e:
            # Handle any exceptions that occur during decoding
            print(f"Error: {e}")
            context = {'message': 'An error occurred during decoding. Please try again.'}
            return render(request, 'audiosteganography/result.html', context)

    else:
        # Render the index page with the form
        return render(request, 'audiosteganography/decode.html')
    
    
import os
from django.http import HttpResponse
from django.conf import settings


# def download(request):
#     file_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'output.wav')
    
#     # Check if the file exists
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as file:
#             response = HttpResponse(file.read(), content_type='audio/wav')
#             response['Content-Disposition'] = 'inline; filename="output.wav"'
#             return response
#     else:
#         return HttpResponse('File not found')

