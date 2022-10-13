from django.http import HttpResponse
from django.http import HttpRequest
from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import *
from .Source import *
from django.conf import settings
def index(request):
    latest_message_list = Message.objects.order_by('-Date')
    template = loader.get_template('Messagerie/Index.html')
    context = {'latest_message_list': latest_message_list, }
    text = request.POST.get('text')
    print(text)
    return HttpResponse(template.render(context, request))

def log(request):
    context = {}
    connected = False

    template = loader.get_template('Messagerie/Log.html')
    user = auto_login(request.COOKIES.get('sessionid'), request.session.get('userid'))
    if user == -1:
        print("No cookie found")
        toConnect = login(request.POST.get('username'), request.POST.get('password'), request.COOKIES.get('sessionid'))
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
        user.set_sessionid(request.COOKIES.get('sessionid'))
        print(user.sessionid)
        template = loader.get_template('Messagerie/index.html')

        Conv = createConv(request, user)
    return HttpResponse(template.render(context, request))

