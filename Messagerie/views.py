from django.http import HttpResponse, JsonResponse

from .Source import *
from django.shortcuts import redirect

#latest_message_list, conv_list, conv, list_user

def index(request):
    perf = PerformanceProfiler("index")
    try:
        user = auto_login(request.session.session_key, request.session.get('email'))
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
    context = {"user": user, 'latest_message_list': latest_message_list, 'conv_list': conv_list, 'conv_shown': conv, 'fileform': fileform, 'list_user': list_user}

    if conv_list is not None:
        for i in conv_list:
            if(str(i.Name).__len__() > 12):
                i.Name = i.Name[:10]+"..."

    #Users.objects.create_user(username_value="test2", email="test2@test2.fr", password="test2", PP="")
    return HttpResponse(template.render(context, request))

def log(request):
    perf = PerformanceProfiler("log")
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
                request.session['email'] = user.email
                request.session['userid'] = user.id
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

def handler(request):
    perf = PerformanceProfiler("handler")
    if request.method == 'POST':
        if "sendMessage" in request.POST.get("type"):
            user = getUser(request.session.get('userid'));
            msg = sendMsg(user, request)
            fileList = []
            for fl in msg.files.all():
                fileList.append(fl.file.url)
            return JsonResponse(data={"userid": msg.Sender.id, "username": msg.Sender.username_value, "convid": request.session['actualConv'], "text": msg.Text, "files": fileList, "date": msg.Date, "msgid": msg.id})
        elif "fetch" in request.POST.get("type"):
            user = getUser(request.session.get('userid'))
            conv = getConv(request.session['actualConv'])
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
    return JsonResponse(data="EMPTY", safe=False)