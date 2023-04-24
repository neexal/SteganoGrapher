import os
import cv2
import numpy as np
from PIL import Image
from django.shortcuts import render
from django.conf import settings


def Image_steganography(file, n):
    # Function for Image Steganography

    def data2binary(data):
        # Converts data to binary format
        p = ''
        if type(data) == str:
            p = p.join([format(ord(i), '08b') for i in data])
        elif type(data) == bytes or type(data) == np.ndarray:
            p = [format(i, '08b') for i in data]
        return p

    def hide_data(img, data):
        # Hides data in the given image
        data += "$$"  # '$$'--> secret key
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

    def find_data(img):
        # Finds the hidden data in the image
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

    def Encode(file_path, message):
        # Encodes the given message into the image file
        image = cv2.imread(file_path)
        img = Image.open(file_path, 'r')
        w, h = img.size
        if len(message) == 0:
            raise ValueError("Empty message")
        enc_img = os.path.join(settings.MEDIA_ROOT, 'encoded.png')
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

    def Decode(file_path):
        # Decodes the message from the given image file
        image = cv2.imread(file_path)
        img = Image.open(file_path, 'r')
        msg = find_data(image)
        img.close()
        return msg

    if n == 0:
        return Encode
    else:
        return Decode


def steganography(request):
    if request.method == 'POST':
        # If form is submitted
        file = request.FILES['image']
        message = request.POST.get('message', '')
            # Save the uploaded file to the server
        file_path = 'media/' + file.name
        with open(file_path, 'wb') as f:
            f.write(file.read())
        
        # Encode or decode based on the value of 'submit' button
        if request.POST.get('submit') == 'Encode':
            # Encode the message in the image and save the image
            Image_steganography(file_path, 0, message)
            message = "Image encoded successfully!"
        else:
            # Decode the message from the image
            message = Image_steganography(file_path, 1)
        
        # Return the response with the encoded/decoded message
        context = {'message': message}
        return render(request, 'steganography.html', context)
    else:
        # If form is not submitted
        return render(request, 'steganography.html')
