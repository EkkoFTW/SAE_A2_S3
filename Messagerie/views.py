from django.http import HttpResponse
from django.http import HttpRequest
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .forms import ImageForm, FileForm
from .models import *
from .Source import *
from django.conf import settings
from django.shortcuts import redirect

def handle_uploaded_file(f):
    with open('E:\Code\A2\SAE_A2_S3\media.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def index(request):
    try:
        user = auto_login(request.session.session_key, request.session.get('userid'))
        if user == -1:
            print("no sessionid")
            return redirect('log')
    except:
        return redirect('log')

    #createConv(request, user)
    #deleteConv(42)
    msgCleaner()
    latest_message_list, conv_list, conv = showMessageList(user, request)
    template = loader.get_template('Messagerie/Index.html')
    context = {'latest_message_list': latest_message_list, 'conv_list': conv_list, 'conv_shown': conv, }

    #Users.objects.create_user(username_value="test2", email="test2@test2.fr", password="test2", PP="")

    return HttpResponse(template.render(context, request))

def log(request):
    context = {}
    connected = False
    template = loader.get_template('Messagerie/Log.html')
    user = -1
    try:
        user = auto_login(request.session.session_key, request.session.get('userid'))
    except:
        print("error cookies sessionid")
    if user != -1:
        connected = True
    else:
        print("not auto-logged in")
        user = login(request.POST.get('username'), request.POST.get('password'))
        if user != -1:
            print("connected", end="")
            connected = True
            request.session['userid'] = user.email
            try:
                user.sessionid = request.COOKIES.get('sessionid')
                user.save()
            except:
                print('no sessionid set')
                request.session.create()
                user.sessionid = request.session.session_key
                user.save()
        else:
            print('no matching account')
    if connected:
        print("Connected")
        return redirect('index')
    return HttpResponse(template.render(context, request))


def image_upload_view(request):
    """Process images uploaded by users"""
    print("image_upload_view")
    imageform = ImageForm()
    fileform = FileForm()
    if request.method == 'POST':
        if "image" in request.POST:
            print("image")
            imageform = ImageForm(request.POST, request.FILES)
            fileform = FileForm()
            if imageform.is_valid():
                imageform.save()
                # Get the current instance object to display in the template
                img_obj = imageform.instance
                return render(request, 'Messagerie/Upload.html', {'imageform': imageform, 'fileform' : fileform , 'img_obj': img_obj})
        elif "file" in request.POST:
            print("file")
            imageform = ImageForm()
            fileform = FileForm(request.POST, request.FILES)
            if fileform.is_valid():
                handle_uploaded_file(request.FILES['file'])
        else:
            print("No type")
    else:
        imageform = ImageForm()
        fileform = FileForm()
        response = HttpResponse()
        response.status_code = 200
        response.content = loader.get_template("Messagerie/Upload.html")
        response.headers = {'imageform': imageform, 'fileform': fileform}

    return HttpResponse(render(request, 'Messagerie/Upload.html', {'imageform': imageform, 'fileform' : fileform}))