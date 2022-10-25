from django.http import HttpResponse
from django.http import HttpRequest
from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import *
from .Source import *
from django.conf import settings
from django.shortcuts import redirect

def index(request):
    try:
        user = auto_login(request.COOKIES.get('sessionid'), request.session.get('userid'))
        if user == -1:
            print("no sessionid")
            return redirect('log')
    except:
        return redirect('log')

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
        user = auto_login(request.COOKIES.get('sessionid'), request.session.get('userid'))
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
            request.session['userid'] = user.username_value
            try:
                user.sessionid = request.COOKIES.get('sessionid')
                user.save()
            except:
                print('no sessionid set')
        else:
            print('no matching account')
    if connected:
        print("Connected")
        return redirect('index')
    return HttpResponse(template.render(context, request))

