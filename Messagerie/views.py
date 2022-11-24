from django.http import HttpResponse
from django.http import HttpRequest
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .forms import ImageForm, FileForm
from .models import *
from .Source import *
from django.conf import settings
from django.shortcuts import redirect

def index(request):
    try:
        user = auto_login(request.session.session_key, request.session.get('userid'))
        if user == -1:
            print("no sessionid")
            return redirect('log')
    except:
        return redirect('log')
    if request.method:
        if "createConv" in request.POST:
            createConv(request, user, request.POST.get('convName'))
    latest_message_list, conv_list, conv, list_user = showMessageList(user, request)
    fileform = FileForm()
    template = loader.get_template('Messagerie/Index.html')
    context = {'latest_message_list': latest_message_list, 'conv_list': conv_list, 'conv_shown': conv, 'fileform': fileform, 'list_user': list_user}


    #Users.objects.create_user(username_value="test2", email="test2@test2.fr", password="test2", PP="")
    return HttpResponse(template.render(context, request))

def log(request):
    context = {}
    connected = False
    template = loader.get_template('Messagerie/Log.html')
    user = -1
    if request.session.session_key is None:
        request.session.create()
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
            imageform = ImageForm(request.POST, request.FILES)
            fileform = FileForm()
            if imageform.is_valid():
                imageform.save()
                img_obj = imageform.instance
                return render(request, 'Messagerie/Upload.html', {'imageform': imageform, 'fileform' : fileform , 'img_obj': img_obj})
        elif "file" in request.POST:
            print(request.POST)
            print(request.FILES)
            imageform = ImageForm()
            fileform = FileForm(request.POST, request.FILES)
            if fileform.is_valid():
                print(request.POST)
                print(request.FILES)
                handle_uploaded_file(request.FILES['file'], request.POST['title'])
        else:
            print("No type")
    else:
        imageform = ImageForm()
        fileform = FileForm()

    return HttpResponse(render(request, 'Messagerie/Upload.html', {'imageform': imageform, 'fileform' : fileform}))