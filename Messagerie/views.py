from django.http import HttpResponse
from django.http import HttpRequest
from django.template import loader
from django.shortcuts import get_object_or_404, render

from .forms import ImageForm
from .models import *
from .Source import *
from django.conf import settings
from django.shortcuts import redirect

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
    print("I'm in upload")
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            return render(request, 'index.html', {'form': form, 'img_obj': img_obj})
    else:
        print("request.method != 'Post'")
        form = ImageForm()
        response = HttpResponse()
        response.status_code = 200
        response.content = loader.get_template("Messagerie/Upload.html")
        response.headers = {'form': form}

    return HttpResponse(render(request, 'Messagerie/Upload.html', {'form': form}))