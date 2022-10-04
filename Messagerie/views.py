from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import *
def index(request):
    latest_message_list = Message.objects.order_by('-Date')
    template = loader.get_template('Messagerie/Index.html')
    context = {'latest_message_list': latest_message_list, }
    text = request.GET.get('text')
    toAdd = Message(Text=text)
    return HttpResponse(template.render(context, request))

def log(request):
    template = loader.get_template('Messagerie/Log.html')
    latest_message_list = Message.objects.order_by('-Date')
    context = {'latest_message_list': latest_message_list, }

    return HttpResponse(template.render(context, request))

