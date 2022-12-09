from django.http import HttpResponse
from django.http import FileResponse
from django.http import HttpRequest
from django.template import loader
from django.shortcuts import get_object_or_404, render
import mimetypes
from .forms import FileForm
from .models import *
from .Source import *
from django.conf import settings
from django.shortcuts import redirect

#latest_message_list, conv_list, conv, list_user

def index(request):
    perf = PerformanceProfiler("index")
    try:
        user = auto_login(request.session.session_key, request.session.get('userid'))
        if user == -1:
            print("no sessionid")
            return redirect('log')
    except:
        return redirect('log')

    conv_list = user.Conv_User.all()
    firstConv = None
    try:
        firstConv = conv_list[0]
        conv = firstConv
    except:
        latest_message_list = None
        conv_list = None
        conv = None
        list_user = None
    try:
        OldConv = conv_list.get(id=request.session['actualConv'])
        conv = OldConv
    except:
        pass

    try:
        request.session['actualConv']
    except:
        if conv is not None:
            request.session['actualConv'] = conv.id
    all_param = []
    all_param = handle_form_response(request, user, conv, firstConv)
    try:
        for i in range(len(all_param)):
            if i == 0:
                if(type(all_param[i]) == type(redirect)):
                    return all_param[i]
                else:
                    conv = all_param[i]
            elif i == 1:
                conv_list = all_param[i]
            elif i == 2:
                latest_message_list = all_param[i]
            elif i == 3:
                list_user = all_param[i]
    except:
        pass

    fileform = FileForm()
    template = loader.get_template('Messagerie/Index.html')
    if conv is not None:
        latest_message_list = showMessageList(conv)
        list_user = conv.Users.all()
        conv_list = user.Conv_User.all()
    else:
        latest_message_list = list_user = None
    context = {'latest_message_list': latest_message_list, 'conv_list': conv_list, 'conv_shown': conv, 'fileform': fileform, 'list_user': list_user}

    if conv_list is not None:
        for i in conv_list:
            if(str(i.Name).__len__() > 12):
                i.Name = i.Name[:10]+"..."

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
        if "connect" in request.POST:
            user = login(request.POST.get('usernameconnect'), request.POST.get('passwordconnect'))
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
        elif "create" in request.POST:
            Users.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
            return HttpResponse(template.render(context, request))
        if connected:
            print("Connected")
            return redirect('index')
        return HttpResponse(template.render(context, request))

def file(request):
    context = {}
    template = loader.get_template('Messagerie/file.html')
    try:
        user = auto_login(request.session.session_key, request.session.get('userid'))
        if user == -1:
            print("no sessionid")
            return redirect('log')
    except:
        return redirect('log')

    conv_list = user.Conv_User.all()
    firstConv = None
    latest_message_list = None
    list_user = None
    try:
        firstConv = conv_list[0]
        conv = firstConv
    except:
        latest_message_list = None
        conv_list = None
        conv = None
        list_user = None
    try:
        OldConv = conv_list.get(id=request.session['actualConv'])
        conv = OldConv
    except:
        pass
    try:
        request.session['actualConv']
    except:
        if conv is not None:
            request.session['actualConv'] = conv.id

    all_param = handle_form_response(request, user, conv, firstConv)
    try:
        for i in range(len(all_param)):
            if i == 0:
                if (type(all_param[i]) == type(redirect)):
                    return all_param[i]
                else:
                    conv = all_param[i]
            elif i == 1:
                conv_list = all_param[i]
            elif i == 2:
                latest_message_list = all_param[i]
            elif i == 3:
                list_user = all_param[i]
    except:
        pass
    fileform = FileForm()
    if conv_list is not None:
        for i in conv_list:
            if (len(str(i.Name)) > 12):
                i.Name = i.Name[:10] + "..."
    current_dir = None
    if 'current_dir' in request.session:
        current_dir = request.session['current_dir']
    all_files, list_subdirs = get_all_files(conv, current_dir)

    context = {'latest_message_list': latest_message_list, 'conv_list': conv_list, 'conv_shown': conv,
               'fileform': fileform, 'list_user': list_user, 'list_files': all_files, 'list_subdir': list_subdirs}

    return HttpResponse(template.render(context, request))

def download_file(request, filepath):
    if "downloadFile" in request.POST:
        file = request.POST['downloadFile']
        filename = file.Title
        fl_path = file.file.path
        fl = open(fl_path, 'rb')
        mime_type, _ = mimetypes.guess_type(fl_path)
        response = FileResponse(fl)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    else:
        return index(request)
