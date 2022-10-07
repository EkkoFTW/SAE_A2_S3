from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import *
from .Source import *

def index(request):
    latest_message_list = Message.objects.order_by('-Date')
    template = loader.get_template('Messagerie/Index.html')
    context = {'latest_message_list': latest_message_list, }
    text = request.POST.get('text')
    print(text)
    return HttpResponse(template.render(context, request))

def log(request):
    template = loader.get_template('Messagerie/Log.html')
    context = {}
    toConnect = login(request.session.get('Username'), request.session.get('Password'))
    if (type(toConnect) == type(Users)):
        print("Cookie found")
        print(toConnect)
    else:
        print("No cookie found")
        request.session.get('Mail')
        toConnect = login(request.POST.get('username'), request.POST.get('password'))
        if (toConnect == -1):
            print("type again u monke")
        else:
            print(toConnect)
            template = loader.get_template('Messagerie/index.html')
            request.session['Username'] = toConnect.username_value
            request.session['Mail'] = toConnect.email
    return HttpResponse(template.render(context, request))

