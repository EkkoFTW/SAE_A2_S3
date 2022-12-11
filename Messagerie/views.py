from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import FileResponse
from django.http import HttpRequest
from django.template import loader
from django.shortcuts import get_object_or_404, render
import mimetypes
from .forms import FileForm
from .models import *
from .Source import *
from django.shortcuts import redirect

#latest_message_list, conv_list, conv, list_user

def index(request):
    perf = PerformanceProfiler("index")
    if not request.user.is_authenticated:
        return redirect('log')
    template = loader.get_template('Messagerie/Index.html')
    if "logout" in request.POST:
        logout(request)
        return redirect('log')
    fileform = FileForm()
    context = {"fileform": fileform}
    """
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

    template = loader.get_template('Messagerie/Index.html')
    if conv is not None:
        latest_message_list = showMessageList(conv)
        list_user = conv.Users.all()
        conv_list = user.Conv_User.all()
    else:
        latest_message_list = list_user = None
    context = {"user": user, 'latest_message_list': latest_message_list, 'conv_list': conv_list, 'conv_shown': conv, 'fileform': fileform, 'list_user': list_user}

    if conv_list is not None:
        for i in conv_list:
            if(str(i.Name).__len__() > 12):
                i.Name = i.Name[:10]+"..."

    #Users.objects.create_user(username_value="test2", email="test2@test2.fr", password="test2", PP="")
    """
    return HttpResponse(template.render(context, request))

def log(request):
    perf = PerformanceProfiler("log")
    context = {}
    template = loader.get_template('Messagerie/Log.html')
    if "connect" in request.POST:
        username = request.POST['usernameconnect']
        password = request.POST['passwordconnect']
        user = authenticate(request, username=username, password=password)
        if user is not None :
            login(request, user)
            return redirect('index')
    elif "create" in request.POST:
        username = request.POST['username']
        email = request.POST['email']
        user = Users.objects.create_user(username, email, request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('index')
    return HttpResponse(template.render(context, request))

def handler(request):
    perf = PerformanceProfiler("handler")
    if request.method == 'POST':
        type = request.POST['type']
        if "sendMessage" == type:
            user = getUser(request.user.id)
            msg = sendMsg(user, request)
            fileList = []
            for fl in msg.files.all():
                fileList.append(fl.file.url)
            Dict = {"type": "sendMessage", "userid": msg.Sender.id, "username": msg.Sender.username_value, "convid": request.session['actualConv'], "text": msg.Text, "files": fileList, "date": msg.Date, "msgid": msg.id}
            return JsonResponse(data=Dict)
        elif "fetchMsg" == type:
            user = getUser(request.user.id)
            try:
                conv = getConv(request.session['actualConv'])
            except:
                conv = getLatestConv(user)[0]
                request.session['actualConv'] = conv.id
            if conv == -1:
                return JsonResponse(data={'type': "non"})
            msgList = fetchAskedMsg(conv)
            Dict = {}
            records = []
            for msg in msgList:
                fileList = []
                for fl in msg.files.all():
                    fileList.append(fl.file.url)
                records.append({"userid": msg.Sender.id, "username": msg.Sender.username_value, "convid": request.session['actualConv'], "text": msg.Text, "files": fileList, "date": msg.Date, "msgid": msg.id})
            Dict["msgList"] = records
            return JsonResponse(data=Dict)
        elif "fetchConv" == type:
            user = getUser(request.user.id)
            convList = user.Conv_User.all()
            Dict = {}
            records = []
            for conv in convList:
                records.append({"convid": conv.id, "convname": conv.Name})
            Dict["convList"] = records
            return JsonResponse(data=Dict)
        elif "selectConv" == type:
            convid = request.POST['convid']
            user = getUser(request.user.id)
            try:
                actualConv = request.session['actualConv']
            except:
                request.session['actualConv'] = user.Conv_User.all()[:1][0].id
                actualConv = request.session['actualConv']
            conv = None
            usercan = True
            begin = False
            if (convid == "Begin"):
                try:
                    conv = user.Conv_User.get(pk=actualConv)
                    convid = conv.id
                except:
                    try:
                        conv = user.Conv_User.all()[:1][0]
                        convid = conv.id
                    except:
                        usercan = False
                begin = True
            else:
                try:
                    conv = user.Conv_User.get(pk=convid)
                except:
                    usercan = False
            if (usercan or (begin and usercan)):
                request.session['old_convid'] = actualConv
                old_convid = request.session['old_convid']
                request.session['actualConv'] = convid
                return JsonResponse(data={"type": "selectConv", "convid": convid, "old_convid": old_convid, "convname": conv.Name, "response": True})
            return JsonResponse(data={"type": "selectConv", "response": False})

        elif "deleteConv" == type:
            old_convid = -1
            try:
                old_convid = request.session['old_convid']
            except:
                pass
            convid = request.POST['convid']
            if request.session['actualConv'] == convid:
                request.session['actualConv'] = ""
            if old_convid == convid:
                request.session['old_convid'] = ""
            user = getUser(request.user.id)
            kick(getConv(convid), user)
            return JsonResponse(data={"type": "deleteConv", "convid": convid})
        elif "createConv" == type:
            user = getUser(request.user.id)
            conv = createConv(request, user, request.POST['convname'])
            return JsonResponse(data={"type": "createConv", "convid": conv.id, "convname": conv.Name})
        elif "addUserToConv" == type:
            convid = request.session['actualConv']
            userEmail = request.POST['email']
            try:
                user = Users.objects.get(email=userEmail)
                addUserObjToConv(getConv(convid), user)
                return JsonResponse(data={"type": "addUserToConv", "convid": convid, "userid": user.id})
            except:
                return JsonResponse(data={"type": "userNotAdded"})
        elif "askUser" == type:
            convid = request.POST['convid']
            conv = getConv(convid)
            userList = conv.Users.all()
            Dict = {}
            records = []
            for user in userList:
                records.append({"username": user.username_value, "email": user.email, "userid": user.id, "PP": user.PP})
            Dict['userList'] = records
            return JsonResponse(data=Dict)
        elif "askUserById" == type:
            user = getUser(request.POST['userid'])
            return JsonResponse(data={"username": user.username_value, "email": user.email, "PP": user.PP})
        elif "askConvById" == type:
            conv = getConv(request.POST['convid'])
            return JsonResponse(data={"convid": conv.id, "convname": conv.Name})
    return JsonResponse(data="EMPTY", safe=False)

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
    print(request.session)
    if 'current_dir' in request.session:
        print(request.session['current_dir'])
        current_dir = request.session['current_dir']
        print(current_dir)
    all_files = []
    list_subdirs = []
    try:
        all_files, list_subdirs = get_all_files(conv, current_dir)
        previous_dir = None
        if list_subdirs is not None and len(list_subdirs) == 0 and current_dir is not None:
            previous_dir = getDir(current_dir, conv)
    except:
        print("Conv deleted and not updated or unknown on get_all_files execution views.file()")

    context = {'latest_message_list': latest_message_list, 'conv_list': conv_list, 'conv_shown': conv,
               'fileform': fileform, 'list_user': list_user, 'list_files': all_files, 'list_subdir': list_subdirs,
               'current_dir': current_dir}

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
