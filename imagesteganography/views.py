from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# from .models import imageMessage


# Create your views here.
def index(request):

    #if user is not logged in, redirect to home page
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    return render(request, 'imagesteganography/index.html')


def encode(request):
    # if request.method == 'POST':
    #     message = request.POST.get('message')
    #     image_file = request.FILES.get('image_file')
    #     image = imageMessage(message=message, image_file=image_file, user=request.user) # attach current user to image
    #     image.save()
    #     return redirect('imagesteganography:download')
    # else:
    return render(request, 'imagesteganography/index.html')

@login_required
def download(request):
    return render(request, 'imagesteganography/download.html')


# def encode(request):
#     user = request.user
#     if request.method == 'POST':
#         message = request.POST.get['message']
#         image = request.FILES.get['image']
#         password = request.POST.get['password']
#         Cpassword = request.POST.get['Cpassword']

#         # if password & Cpassword != '':
#         #     new_data = imageMessage.objects.create(user=user, message=message, image_file=filename)
            

#         # save the image file
#         fs = FileSystemStorage()
#         filename = fs.save(image.name, image)

#         # create a new imageMessage object
#         new_data = imageMessage.objects.create(user="aalok", message=message, image_file=image, password=password)
#         new_data.save()
#     return render(request, 'imagesteganography/index.html')