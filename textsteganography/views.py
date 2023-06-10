from django.shortcuts import render, redirect
from .models import TextMessage
from django.contrib.auth.decorators import login_required
import os

# Create your views here.
def index(request):
    return render(request,'textsteganography/index.html')


def encode(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        # password = request.POST.get('password')
        text_file = request.FILES.get('text_file')
        text_message = TextMessage.objects.create(user=request.user,message=message, text_file = text_file)
        text_message.save()
        cover_content = text_file.read().decode('utf-8')
        encoded_text = ''

        # Convert each character in message to binary and replace LSB of each corresponding character in cover_content
        for i, char in enumerate(message):
            if i < len(cover_content):
                binary_char = format(ord(char), '08b')
                cover_char = cover_content[i]
                binary_cover_char = format(ord(cover_char), '08b')
                encoded_char = binary_cover_char[:-1] + binary_char[-1]  # Replace LSB of cover_char with LSB of binary_char
                encoded_text += chr(int(encoded_char, 2))
            else:
                encoded_text += char

            # Append remaining characters in the cover_content to the encoded text
            encoded_text += cover_content[len(message):]

            # Save encoded text to database
            encoded_text_object = TextMessage(text_file=encoded_text, user=request.user)
            encoded_text_object.save()

            # Save updated cover file
            text_file.seek(0)
            text_file.write(encoded_text.encode('utf-8'))

            return redirect('textsteganography:download')
        else:
            return render(request, 'textsteganography/index.html')

@login_required
def decode(request):
    if request.method == 'POST':
        encoded_text = request.POST['encoded_text']
        decoded_text = ''

        # Extract LSB of each character in encoded_text and convert to binary
        for char in encoded_text:
            binary_char = format(ord(char), '08b')
            decoded_text += binary_char[-1]  # Extract LSB

        # Convert binary string to ASCII string
        decoded_text = ''.join(chr(int(decoded_text[i:i+8], 2)) for i in range(0, len(decoded_text), 8))

        encoded_text_object = TextMessage(text=encoded_text, user=request.user)
        encoded_text_object.save()

        return render(request, 'textsteganography/result.html', {'message': decoded_text})
    else:
        return render(request, 'textsteganography/decode.html')

@login_required
def download(request):
    latest_text = TextMessage.objects.filter(user=request.user).latest('uploaded_at')
    context = {'text': latest_text}
    return render(request, 'textsteganography/download.html', context)