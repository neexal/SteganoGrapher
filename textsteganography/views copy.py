from django.shortcuts import render, redirect
from .models import TextMessage
from django.contrib.auth.decorators import login_required
import os
from django.http import HttpResponse
from django.conf import settings

# Create your views here.
def index(request):

    #if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    return render(request, 'textsteganography/index.html')


# def Text_steganography(file, n):
#     # def EncodeTheText(text, file):
        



#     def BinaryToDecimal(binary):
#         string = int(binary, 2)
#         return string

#     def Decode():
#         print("[INFO] Text Steganography DECODING")
#         ZWC_reverse = {u"\u200C": "00", u'\u202C': "01", u'\u202D': "11", u'\u200E': "10"}
#         file4 = open(file, 'r', encoding="utf-8")
#         temp = ''
#         for line in file4:
#             for word in line.split():
#                 T1 = word
#                 binary_extract = ""
#                 for letters in T1:
#                     if letters in ZWC_reverse:
#                         binary_extract = binary_extract + ZWC_reverse[letters]
#                     if letters == "111111111111":
#                         break
#                     else:
#                         if len(binary_extract) == 12:
#                             temp = temp + binary_extract
#         print("[INFO] Encrypted message present in code bits: {}".format(temp))
#         print("[INFO] Length of encoded bits:- {}".format(len(temp)))
#         i = 0
#         a = 0
#         b = 4
#         c = 4
#         d = 12
#         final = ''
#         while i < len(temp):
#             t3 = temp[a:b]
#             a = a + 12
#             b = b + 12
#             i = i + 12
#             t4 = temp[c:d]
#             c = c + 12
#             d = d + 12
#             if t3 == "0110":
#                 for i in range(0, len(t4), 8):
#                     temp_data = t4[i:i + 8]
#                     decimal_data = BinaryToDecimal(temp_data)
#                     final = final + chr((decimal_data ^ 170) + 48)
#             elif t3 == "0011":
#                 for i in range(0, len(t4), 8):
#                     temp_data = t4[i:i + 8]
#                     decimal_data = BinaryToDecimal(temp_data)
#                     final = final + chr((decimal_data ^ 170) - 48)
#         print("[*] The Encoded data was:- {}".format(final))
#         print("=" * 100)

#     # if n == 0:
#     #     EncodeTheText(file)
#     # else:
#     #     Decode()


import tempfile

class Text_steganography:
    @staticmethod
    def char_to_bin(c):
        return '{0:08b}'.format(ord(c))

    @staticmethod
    def bin_to_char(b):
        return chr(int(b, 2))

    @staticmethod
    def encode(text, message):
        # Convert the message to binary
        message_bin = ''.join(Text_steganography.char_to_bin(c) for c in message)

        # Get the length of the message in binary
        message_len_bin = '{0:032b}'.format(len(message_bin))

        # Check if the message can fit in the text
        text_len = len(text)
        required_len = len(message_len_bin) + len(message_bin)
        if text_len < required_len:
            raise ValueError('Text is too short to fit message.')

        # Embed the message length in the text
        text = text[:required_len] + message_len_bin + text[required_len+len(message_len_bin):]

        # Embed the message in the text
        for i, bit in enumerate(message_bin):
            char_index = required_len + i*8
            char = text[char_index:char_index+8]
            new_char = char[:-1] + bit
            text = text[:char_index] + new_char + text[char_index+8:]

        return text

    @staticmethod
    def decode(text):
        # Extract the message length from the text
        message_len_bin = text[:32]
        message_len = int(message_len_bin, 2)

        # Extract the message from the text
        message_bin = ''
        for i in range(message_len):
            char_index = 32 + i*8
            char = text[char_index:char_index+8]
            message_bin += char[-1]
        message = ''.join(Text_steganography.bin_to_char(message_bin[i:i+8]) for i in range(0, len(message_bin), 8))

        return message
@login_required
def encode(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        cover_text = request.FILES.get('text_file')

        # Create a temporary file to write the encoded message
        file = tempfile.NamedTemporaryFile(delete=False).name

        # Save the cover text file to the temporary file
        with open(file, 'wb+') as destination:
            for chunk in cover_text.chunks():
                destination.write(chunk)

        # Encode the secret message using Text_steganography function
        with open(file, 'r+') as f:
            text = f.read()
            encoded_text = Text_steganography.encode(text, message)
            f.seek(0)
            f.write(encoded_text)
            f.truncate()

        # Create a response for file download
        with open(file, 'rb') as encoded_file:
            response = HttpResponse(encoded_file, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="encoded_text.txt"'

        # Delete the temporary file
        os.remove(file)

        return response

    return render(request, 'textsteganography/index.html')


from django.core.files.uploadedfile import TemporaryUploadedFile

from django.core.files.uploadedfile import TemporaryUploadedFile

@login_required
def decode(request):
    if request.method == 'POST':
        encoded_text = request.FILES.get('text_file')

        # Save the encoded text file to a temporary file
        with TemporaryUploadedFile(name=encoded_text.name, content_type=encoded_text.content_type, size=encoded_text.size, charset='utf-8') as temp_file:
            for chunk in encoded_text.chunks():
                temp_file.write(chunk)

            # Read the encoded text file
            with open(temp_file.temporary_file_path(), 'rb') as f:
                text = f.read().decode('utf-8')

        # Decode the message using Text_steganography function
        message = Text_steganography.decode(text)

        # Create a response with the decoded message
        response = HttpResponse(message, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="decoded_message.txt"'

        return response

    return render(request, 'textsteganography/decode.html')

@login_required
def download(request):
    latest_text = TextMessage.objects.filter(user=request.user).latest


# bin_list = [" ", "0", "1"]
# char_list = ["\u2060", "\u200B", "\u200C"]

# @login_required
# def encode(request):
#     if request.method == 'POST':
#         message = request.POST.get('message')
#         cover_text = request.FILES.get('text_file')

#         # Read the content of the cover text file
#         cover_content = cover_text.read().decode('utf-8')

#         # Encode the secret message using zero-width characters
#         bin_text = ' '.join(format(ord(x), 'b') for x in message)
#         encoded_text = cover_content
#         for b in bin_text:
#             encoded_text += char_list[bin_list.index(b)]

#         # Save the encoded text to the database
#         text_message = TextMessage.objects.create(user=request.user, message=message, text_file=encoded_text)
#         text_message.save()

#         # Create a response for file download
#         response = HttpResponse(encoded_text, content_type='text/plain')
#         response['Content-Disposition'] = 'attachment; filename="encoded_text.txt"'

#         return response
    
#     return render(request, 'textsteganography/index.html')



# @login_required
# def decode(request):
#     if request.method == 'POST':
#         encoded_text = request.POST.get('text_file')

#         if not encoded_text:
#             # Handle case where encoded_text is not provided
#             return render(request, 'textsteganography/decode.html', {'message': 'Encoded text is missing'})

#         # Extract the binary representation from the encoded text
#         bin_text = ""
#         for w in encoded_text:
#             if w in char_list:
#                 bin_text += bin_list[char_list.index(w)]

#         if not bin_text:
#             # Handle case where bin_text is empty
#             return render(request, 'textsteganography/decode.html', {'message': 'Invalid encoded text'})

#         # Split the binary text into chunks of 8 bits (1 byte)
#         bin_val = bin_text.split()

#         # Convert each byte to its corresponding ASCII character
#         secret_text = ""
#         for b in bin_val:
#             secret_text += chr(int(b, 2))

#         # Save the decoded text to the database
#         text_message = TextMessage.objects.create(user=request.user, message=secret_text)
#         text_message.save()

#         return render(request, 'textsteganography/result.html', {'message': secret_text})

#     return render(request, 'textsteganography/decode.html')
# @login_required
# def download(request):
#     latest_text = TextMessage.objects.filter(user=request.user).latest('uploaded_at')
#     context = {'text': latest_text}
#     return render(request, 'textsteganography/download.html', context)