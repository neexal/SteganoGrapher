import wave
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, Http404
import mimetypes
from django.contrib.auth.decorators import login_required


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
            frame_byte = bytearray(frames)

            # Encode the message in the audio frames
            message += '*^*^*'  # Add secret key
            message_bytes = message.encode('utf-8')
            message_length = len(message_bytes)

            index = 0
            for i in range(message_length):
                byte = bin(frame_byte[index])[2:].zfill(8)
                bit = bin(message_bytes[i])[2:].zfill(8)
                modified_byte = byte[:-1] + bit[-1]
                frame_byte[index] = int(modified_byte, 2)
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

            # Convert the binary message to ASCII characters using the 'latin-1' encoding
            decoded_message = ''
            for i in range(0, len(message), 8):
                byte = message[i:i+8]
                try:
                    char = chr(int(byte, 2))
                except ValueError:
                    char = '?'  # Placeholder for invalid characters
                decoded_message += char

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
