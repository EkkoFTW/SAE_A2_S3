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
    user = auto_login(request.COOKIES.get('sessionid'), request.session.get('userid'))
    conv_list = Conv_User.objects.filter(Users=user)
    firstConv = conv_list[0]
    latest_message_list = firstConv.Messages.all().order_by('-Date')[:4]
    conv=firstConv
    updatedConv = request.POST.get('conv')

    if updatedConv is not None:
        conv = updatedConv
    sendMsg(user, request)
    template = loader.get_template('Messagerie/Index.html')
    context = {'latest_message_list': latest_message_list, 'conv_list': conv_list, }
    return HttpResponse(template.render(context, request))

def log(request):
    context = {}
    connected = False
    template = loader.get_template('Messagerie/Log.html')
    user = auto_login(request.COOKIES.get('sessionid'), request.session.get('userid'))
    if user == -1:
        print("No cookie found")
        toConnect = login(request.POST.get('username'), request.POST.get('password'))
        if toConnect == -1:
            print("Password = false")
        else:
            print(toConnect)
            request.session['userid'] = toConnect.username_value
            user = toConnect
            connected = True
    else:
        connected = True
    if connected:
        user.sessionid = request.COOKIES.get('sessionid')
        user.save()
        return redirect('index')

        #Conv = createConv(request, user)
        #conv_list = Conv_User.objects.filter(Users=user)
        #context = {'conv_list': conv_list, }
        #testConv = Conv_User.objects.get(id=36)
        #sendMsg(testConv, user, request)
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