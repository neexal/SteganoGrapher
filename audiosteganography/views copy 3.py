import os
import wave
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.conf import settings



def index(request):
    #if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    return render(request, 'audiosteganography/index.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
import os
import wave




# comment
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

        encoded_file_path = os.path.relpath(encoded_audio_path, settings.MEDIA_ROOT)
        download_link = reverse('audiosteganography:download', kwargs={'encoded_file_path': encoded_file_path})
        return redirect(download_link)
    else:
        return render(request, 'audiosteganography/index.html')


@login_required
def decode(request):
    if request.method == 'POST':
        # Get the audio file from the form
        audio_file = request.FILES.get('audio_file')

        try:
            # Save the uploaded audio file
            audio_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'input.wav')
            with open(audio_path, 'wb') as file:
                for chunk in audio_file.chunks():
                    file.write(chunk)

            # Open the audio file using the wave module
            audio = wave.open(audio_path, mode='rb')
            frames = audio.readframes(audio.getnframes())
            frame_byte = bytearray(frames)

            # Extract the encoded message from the audio frames
            message = ''
            for byte in frame_byte:
                message += bin(byte)[-1]

            # Split the binary message using the delimiter
            message = message.split('*^*^*')[0]

            # Convert the binary message to ASCII characters
            decoded_message = ''.join(chr(int(message[i:i+8], 2)) for i in range(0, len(message), 8))

            # Render the success page with the decoded message
            context = {'message': decoded_message}
            return render(request, 'audiosteganography/result.html', context)

        except Exception as e:
            # Handle any exceptions that occur during decoding
            print(f"Error: {e}")
            context = {'message': 'An error occurred during decoding. Please try again.'}
            return render(request, 'audiosteganography/result.html', context)

    else:
        # Render the index page with the form
        return render(request, 'audiosteganography/decode.html')


def download(request, encoded_file_path):
    file_path = os.path.join(settings.MEDIA_ROOT, encoded_file_path)

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = 'attachment; filename="encoded_audio.wav"'
        return response
    else:
        return HttpResponse("File not found.")