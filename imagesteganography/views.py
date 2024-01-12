from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ImageMessage
import cv2
from PIL import Image
import os
import numpy as np
from django.http import FileResponse, HttpResponse
import mimetypes

from django.conf import settings
from accounts.email_utils import send_email_with_attachment
from pathlib import Path  # Import the Path class


# Create your views here.
def index(request):

    #if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    return render(request, 'imagesteganography/index.html')




def encode(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        image_file = request.FILES.get('image_file')
        image = ImageMessage(message=message, image_file=image_file, user=request.user)
        image.save()

        file_path = image.image_file.path

        def data2binary(data):
            p = ''
            if type(data) == str:
                p = p.join([format(ord(i), '08b') for i in data])
            elif type(data) == bytes or type(data) == np.ndarray:
                p = [format(i, '08b') for i in data]
            return p

        def hide_data(img, data):
            data += "$$"
            d_index = 0
            b_data = data2binary(data)
            len_data = len(b_data)

            for value in img:
                for pix in value:
                    r, g, b = data2binary(pix)
                    if d_index < len_data:
                        pix[0] = int(r[:-1] + b_data[d_index])
                        d_index += 1
                    if d_index < len_data:
                        pix[1] = int(g[:-1] + b_data[d_index])
                        d_index += 1
                    if d_index < len_data:
                        pix[2] = int(b[:-1] + b_data[d_index])
                        d_index += 1
                    if d_index >= len_data:
                        break
            return img

        # print("[INFO] Image Steganography ENCODING")
        # print("")
 
        image = cv2.imread(file_path)
        img = Image.open(file_path, 'r')
        w, h = img.size
        if len(message) == 0:
            raise ValueError("[INFO] Empty data")
        enc_img = 'temp.png'
        enc_data = hide_data(image, message)
        cv2.imwrite(enc_img, enc_data)
        img1 = Image.open(enc_img, 'r')
        img1 = img1.resize((w, h), Image.Resampling.LANCZOS)
        if w != h:
            img1.save(enc_img, optimize=True, quality=65)
        else:
            img1.save(enc_img)
        img.close()
        img1.close()

        os.remove(file_path)
        os.rename(enc_img, file_path)

        # print("[INFO] ENCODING DATA Successful")
        # print("[INFO] LOCATION: {}".format(file_path))
        # print("=" * 100)
        
        # image = ImageMessage(message=message, image_file=file_path, user=request.user)
        # image.save()
        if request.method =='POST' and 'send_email' in request.POST:
            subject = 'Encoded Message'
            em_message = 'Please find the attached file.'
            from_email = 'testdjango890@gmail.com'  # Replace with your email address
            to_email = request.POST.get('to_email')
            recipient_list = [to_email]  # Replace with the recipient's email address

            # Generate the FileResponse for the encoded image
            encoded_image_response = FileResponse(open(file_path, 'rb'), content_type=mimetypes.guess_type(file_path)[0])
            encoded_image_response['Content-Disposition'] = 'attachment; filename="encoded_image.png"'

            # Save the FileResponse to a temporary file
            temp_file_path = Path(settings.MEDIA_ROOT) / 'temp_encoded_image.png'
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in encoded_image_response.streaming_content:
                    temp_file.write(chunk)

            # Send the email with the temporary file as an attachment
            send_email_with_attachment(subject, em_message, from_email, recipient_list, temp_file_path)

            # Clean up: Remove the temporary file
            temp_file_path.unlink()

            return HttpResponse('Email sent with encoded image attachment.')
        
        else:
            response = FileResponse(open(file_path, 'rb'), content_type=mimetypes.guess_type(file_path)[0])
            response['Content-Disposition'] = 'attachment; filename="encoded_image.png"'
            return response
    else:
        return render(request, 'imagesteganography/index.html')


def decode(request):
    if request.method == 'POST':
        image_file = request.FILES.get('image_file')
        image = ImageMessage( image_file=image_file, user=request.user) # attach current user to image
        # image.save()
        temp_image = image
        img = Image.open(image_file)
        img_path = os.path.join('media', 'image', image_file.name)
        img.save(img_path)

        # decode hidden message from image
        def data2binary(data):
            p = ''
            if type(data) == str:
                p = p.join([format(ord(i), '08b') for i in data])
            elif type(data) == bytes or type(data) == np.ndarray:
                p = [format(i, '08b') for i in data]
            return p

        def find_data(img):
            bin_data = ""
            for value in img:
                for pix in value:
                    r, g, b = data2binary(pix)
                    bin_data += r[-1]
                    bin_data += g[-1]
                    bin_data += b[-1]

            all_bytes = [bin_data[i: i + 8] for i in range(0, len(bin_data), 8)]

            readable_data = ""
            for i in all_bytes:
                readable_data += chr(int(i, 2))
                if readable_data[-2:] == "$$":
                    break
            return readable_data[:-2]

        image = cv2.imread(img_path)
        message = find_data(image)
        os.remove(img_path)
        context = {'message': message, 'image': temp_image}
        return render(request, 'accounts/result.html', context)
    else:
        return render(request, 'imagesteganography/decode.html')

@login_required
def download(request):
    latest_image = ImageMessage.objects.filter(user=request.user).latest('uploaded_at')
    context = {'image': latest_image}
    return render(request, 'imagesteganography/download.html', context)



