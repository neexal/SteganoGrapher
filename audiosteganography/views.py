import os
import wave
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.conf import settings
from accounts.email_utils import send_email_with_attachment
from pathlib import Path  # Import the Path class
import mimetypes

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
            message += '000010110000101100001011'  # Add delimiter
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

        encoded_audio_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'encoded_output.wav')
        encode_audio(audio_path, encoded_audio_path, message)

        if request.method == 'POST' and 'send_email' in request.POST:
            subject = 'Encoded Message'
            em_message = 'Please find the attached file.'
            from_email = 'testdjango890@gmail.com'  # Replace with your email address
            to_email = request.POST.get('to_email')
            recipient_list = [to_email]  # Replace with the recipient's email address

            # Generate the FileResponse for the encoded image
            encoded_image_response = FileResponse(open(audio_path, 'rb'), content_type=mimetypes.guess_type(audio_path)[0])
            encoded_image_response['Content-Disposition'] = 'attachment; filename="encoded_output.wav"'

            # Save the FileResponse to a temporary file
            temp_file_path = Path(settings.MEDIA_ROOT) / 'temp_encoded_output.wav'
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in encoded_image_response.streaming_content:
                    temp_file.write(chunk)

            # Send the email with the temporary file as an attachment
            send_email_with_attachment(subject, em_message, from_email, recipient_list, temp_file_path)

            # Clean up: Remove the temporary file
            temp_file_path.unlink()

            return HttpResponse('Email sent with encoded audio attachment.')
        
        else:
            response = FileResponse(open(encoded_audio_path, 'rb'), content_type='audio/wav')
            response['Content-Disposition'] = 'attachment; filename="encoded_output.wav"'
            return response

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

            message = ''
            delimiter = '000010110000101100001011'
            delimiter_length = len(delimiter)

            for i in range(len(frame_byte) - delimiter_length + 1):
                chunk = frame_byte[i:i+delimiter_length]
                if all(bit & 1 == int(delimiter[j]) for j, bit in enumerate(chunk)):
                    break  # Stop if delimiter is found
                message += bin(frame_byte[i])[-1]

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
