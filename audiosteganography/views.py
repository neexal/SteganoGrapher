from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import AudioMessage
import os
import wave

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
        audio = AudioMessage(message=message, audio_file=audio_file, user=request.user) # attach current user to audio
        audio.save()
        try:
            song = wave.open(audio_file, mode='rb')
            nframes = song.getnframes()
            frames = song.readframes(nframes)
            frame_list = list(frames)
            frame_byte = bytearray(frame_list)

            data = request.POST.get('message')

            res = ''.join(format(i, '08b') for i in bytearray(data, encoding='utf-8'))
            print("[INFO] The String after binary conversion:-{}".format(res))
            length = len(res)
            print("[INFO] Length of binary after conversion:-{}".format(length))

            data = data + '*^*^*'

            results = []
            for j in data:
                bits = bin(ord(j))[2:].zfill(8)
                results.extend([int(b) for b in bits])

            k = 0
            for i in range(0, len(results), 1):
                res = bin(frame_byte[k])[2:].zfill(8)
                if res[len(res) - 4] == results[i]:
                    frame_byte[k] = (frame_byte[k] & 253)
                else:
                    frame_byte[k] = (frame_byte[k] & 253) | 2
                    frame_byte[k] = (frame_byte[k] & 254) | results[i]
                k = k + 1
            frame_modified = bytes(frame_byte)
            os.remove(audio_file.name)
            with wave.open(audio_file.name, 'wb') as fd:
                fd.setparams(song.getparams())
                fd.writeframes(frame_modified)
            print("[INFO] ENCODING DATA Successful")
            print("[INFO] LOCATION:{}".format(audio_file.name))
            song.close()
       
        
            context = {'audio_file': audio_file}
            return redirect('audiosteganography:download', context)
    
        except Exception as e:
            # Handle any exceptions that occur during encoding
            print(f"Error: {e}")
            context = {'error_message': 'An error occurred during encoding. Please try again.'}
            return render(request, 'audiosteganography/index.html', context)
    else:
        return render(request, 'audiosteganography/index.html')

@login_required
def download(request):
    return render(request, 'audiosteganography/download.html')

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