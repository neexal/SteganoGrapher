from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from .models import TextMessage

from django.conf import settings
from accounts.email_utils import send_email_with_attachment
from pathlib import Path  # Import the Path class


def index(request):

    #if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    return render(request, 'textsteganography/index.html')


def str2bin(text):
    bin_list = []
    for char in text:
        bin_list.append(bin(ord(char))[2:])
    return ' '.join(bin_list)

def wrap(string):
    return "\uFEFF" + string + "\uFEFF"

def unwrap(string):
    tmp = string.split("\uFEFF")
    if len(tmp) == 1:
        return False
    return tmp[1]

def bin2str(bin_text):
    text_list = []
    bin_list = bin_text.split()
    for bin_char in bin_list:
        text_list.append(chr(int(bin_char, 2)))
    return ''.join(text_list)

def bin2hidden(string):
    string = string.replace(' ', '\u2060')
    string = string.replace('0', '\u200B')
    string = string.replace('1', '\u200C')
    return string

def hidden2bin(string):
    string = string.replace('\u2060', ' ')
    string = string.replace('\u200B', '0')
    string = string.replace('\u200C', '1')
    return string

def encode(request):
    if request.method == 'POST':
        public = request.FILES.get('text_file', None)
        private = request.POST.get('message', None)
 
        if public and private:
            fs = FileSystemStorage()
            filename = fs.save(public.name, public)
            public_file = fs.open(filename)
            public_text = public_file.read().decode('utf-8')
            public_file.close()

            half = round(len(public_text) / 2)
            private_bin = str2bin(private)
            private_hidden = bin2hidden(private_bin)
            private_wrapped = wrap(private_hidden)

            i = 0
            tmp = []
            if len(public_text) == 1:
                tmp.append(public_text[0])
                tmp.append(private_wrapped)
            else:
                for char in public_text:
                    if i == half:
                        tmp.append(private_wrapped)
                    tmp.append(char)
                    i += 1

            public_text = ''.join(tmp)
            
            text = TextMessage(message=private, text_file=public, user=request.user)
            text.save()
            
            if request.method =='POST' and 'send_email' in request.POST:
                subject = 'Encoded Message'
                em_message = 'Please find the attached file.'
                from_email = 'testdjango890@gmail.com'  # Replace with your email address
                to_email = request.POST.get('to_email')
                recipient_list = [to_email]  # Replace with the recipient's email address

                response = HttpResponse(content_type='text/plain')
                response['Content-Disposition'] = 'attachment; filename="encoded.txt"'
                encoded_text = public_text.encode('utf-8')
                response.write(encoded_text)
                
                temp_file_path = Path(settings.MEDIA_ROOT) / 'temp_encoded_text.txt'
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(encoded_text)

                send_email_with_attachment(subject, em_message, from_email, recipient_list, temp_file_path)

                # Clean up: Remove the temporary file
                temp_file_path.unlink()

                return HttpResponse('Email sent with encoded Text attachment.')
            
            else:  
                response = HttpResponse(content_type='text/plain')
                response['Content-Disposition'] = 'attachment; filename="encoded.txt"'
            
                encoded_text = public_text.encode('utf-8')
                response.write(encoded_text)
                return response
    return render(request, 'textsteganography/index.html')


def decode(request):
    if request.method == 'POST':
        encoded = request.FILES.get('text_file', None)

        if encoded:
            fs = FileSystemStorage()
            filename = fs.save(encoded.name, encoded)
            encoded_file = fs.open(filename)
            encoded_text = encoded_file.read().decode('utf-8')
            encoded_file.close()

            unwrapped = unwrap(encoded_text)
            if unwrapped:
                message = bin2str(hidden2bin(unwrapped))
            else:
                message = bin2str(hidden2bin(encoded_text))

            context = {
                'message': message,
            }
            return render(request, 'textsteganography/result.html', context)

    return render(request, 'textsteganography/decode.html')


