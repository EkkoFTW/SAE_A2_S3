import pathlib

from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import FileResponse
import mimetypes
from .Source import *
from django.shortcuts import redirect
from wsgiref.util import FileWrapper

#latest_message_list, conv_list, conv, list_user
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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

    if "toFiles" in request.POST:
        return redirect('file')
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
        channel_layer = get_channel_layer()
        type = request.POST['type']
        validatedConv = None
        try:
            validatedConv = request.user.Conv_User.get(pk=request.session['actualConv'])
        except:
            pass
        if "sendMessage" == type:
            if validatedConv is None:
                return JsonResponse(data={"sendMessage": "false"})
            user = request.user
            Edited = request.POST['Edited']
            if Edited != "null":
                newText = request.POST['text']
                msg = getMsgFromConv(Edited, validatedConv)
                editMessage(msg, newText)
                async_to_sync(channel_layer.group_send)("convId"+str(validatedConv.id), {"type": "editMsg", "msgid": msg.id})
                return JsonResponse(data={"editMsg": True})
            RequestFiles = request.FILES.getlist('files')
            msg = createMsg(user, request.POST['text'])
            try:
                msg.Reply = getMsg(request.POST['Reply'])
            except:
                msg.Reply = None
            for fl in RequestFiles:
                msg.files.add(createFile(fl, user, settings.MEDIA_ROOT+"\\files\\"+str(validatedConv.id)+"\\"+str(user.id)+"\\", msg))
            msg.save()
            NewSendMsg(getConv_s(user, validatedConv.id), msg)
            async_to_sync(channel_layer.group_send)("convId"+str(validatedConv.id), {"type": "sendMessage", "msgid": msg.id})
        elif "fetchMsg" == type:
            user = request.user
            first = int(request.POST['first'])
            try:
                conv = getConv(request.session['actualConv'])
            except:
                conv = getLatestConv(user)[0]
                request.session['actualConv'] = conv.id
            if conv == -1:
                return JsonResponse(data={'type': "non"})
            msgList = fetchAskedMsg(conv, first)
            Dict = {}
            records = []
            replyid = None
            for msg in msgList:
                fileList = []
                try:
                    replyid = msg.Reply.id
                except:
                    replyid = None
                for fl in msg.files.all():
                    fileList.append(fl.file.url)
                records.append({"userid": msg.Sender.id, "username": msg.Sender.username_value, "convid": request.session['actualConv'], "reply": replyid, "text": msg.Text, "Edited": msg.Edited, "files": fileList, "date": msg.Date, "msgid": msg.id})
            Dict["msgList"] = records
            return JsonResponse(data=Dict)
        elif "fetchConv" == type:
            user = request.user
            convList = user.Conv_User.all()
            Dict = {}
            records = []
            for conv in convList:
                records.append({"convid": conv.id, "convname": conv.Name})
            Dict["convList"] = records
            return JsonResponse(data=Dict)
        elif "selectConv" == type:
            convid = request.POST['convid']
            user = request.user
            if user.Conv_User.all().count() == 0:
                request.session['actualConv'] = ""
                async_to_sync(channel_layer.group_send)("userId"+str(user.id), {"type": "selectConv", "convname": "You have no conversation"})
                return JsonResponse(data={"type": "selectConvResponse", "text": "notInConv"})
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
                try:
                    async_to_sync(channel_layer.group_send)("userId"+str(user.id), {"type": "discardConvGroup", "old_convid": old_convid})
                except:
                    pass
                try:
                    async_to_sync(channel_layer.group_send)("userId"+str(user.id), {"type": "addConvGroup", "convid": convid})
                except:
                    pass
                async_to_sync(channel_layer.group_send)("userId"+str(user.id), {"type": "selectConv", "convid": convid, "convname":conv.Name })
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
            if request.POST['userid'] == "-1":
                user = request.user
            else:
                user = getUser(request.POST['userid'])
            if convid == "-1":
                convid = request.session['actualConv']
            kick(getConv(convid), user)
            async_to_sync(channel_layer.group_send)("userId"+str(user.id), {"type": "kickFromConv", "convid": convid})
            async_to_sync(channel_layer.group_send)("convId"+str(convid), {"type": "userToKick", "userid": user.id})
        elif "createConv" == type:
            user = request.user
            conv = createConv(request, user, request.POST['convname'])
            async_to_sync(channel_layer.group_send)("userId"+str(user.id), {"type": "createConv", "convname": conv.Name, "convid": conv.id})
        elif "addUserToConv" == type:
            if validatedConv is None:
                return JsonResponse(data={"addUserToConv": "false"})
            userEmail = request.POST['email']
            try:
                user = Users.objects.get(email=userEmail)
                if addUserObjToConv(getConv(validatedConv.id), user):
                    async_to_sync(channel_layer.group_send)("convId"+str(validatedConv.id), {"type": "add_usertoconv", "userid": user.id})
                    async_to_sync(channel_layer.group_send)("userId"+str(user.id), {"type": "got_addedtoconv", "convid": validatedConv.id})
            except:
                pass
        elif "askUser" == type:
            convid = request.POST['convid']
            conv = getConv(convid)
            userList = []
            try:
                userList = conv.Users.all()
            except:
                pass
            Dict = {}
            records = []
            for user in userList:
                records.append({"username": user.username_value, "email": user.email, "userid": user.id, "PP": user.PP})
            Dict['userList'] = records
            return JsonResponse(data=Dict)
        elif "askUserById" == type:
            user = getUser(request.POST['userid'])
            return JsonResponse(data={"userid": user.id, "username": user.username_value, "email": user.email, "PP": user.PP})
        elif "askConvById" == type:
            conv = getConv(request.POST['convid'])
            return JsonResponse(data={"convid": conv.id, "convname": conv.Name})
        elif "fetchFiles" == type:
            found = False
            try:
                current_dir = request.session["current_dir"]
                found = True
            except:
                current_dir = Directory.objects.filter(Conv_User=request.session["actualConv"])

                for dir in current_dir:
                    if dir.parent is None:
                        current_dir = dir
                        found = True
                        break
            Dict = {}
            dictFiles = []
            dictDirs = []
            if found:
                all_files, all_subdirs = get_all_files(request.session["actualConv"], current_dir, True)
                print(all_files)
                print(all_subdirs)
                for i in range(len(all_files)):
                    print(all_files[i])
                    print(all_files[i].Title)
                    dictFiles.append({"path":all_files[i].file.url, "id":all_files[i].id, "title":all_files[i].Title, "author_id":all_files[i].Author.id, "date":all_files[i].dateAdded, "directory_id":all_files[i].directory.id, "message_id":all_files[i].Message.id})
                for i in range(len(all_subdirs)):
                    print(all_subdirs[i])
                    dictDirs.append({"path":all_subdirs[i].path, "id":all_subdirs[i].id, "title":all_subdirs[i].title, "parent_id": all_subdirs[i].parent.id, "date":all_subdirs[i].Conv_User.id})
                actualDir = getDir(current_dir, request.session["actualConv"])
                if actualDir.parent is None:
                    Dict["parent"] = 0
                else:
                    Dict["parent"] = actualDir.parent.id
            Dict["all_files"] = dictFiles
            Dict["all_subdirs"] = dictDirs
            return JsonResponse(data=Dict)
        elif "enterDir" == type:
            enterDir(request, request.POST["dirId"], request.session["actualConv"])
            return JsonResponse(data={})
        elif "backDir" == type:
            print("Backdir")
            print("Current dir :")
            print(request.session["current_dir"])
            parent = getDir(request.session["current_dir"], request.session["actualConv"]).parent
            if (parent is not None):
                request.session["current_dir"] = parent.id
                print("Current dir set successfully !")
                print("New current dir = ")
                print(request.session["current_dir"])
                if parent.parent is None:
                    return JsonResponse(data={})
                else:
                    return JsonResponse(data={})
            else:
                print("Security beach avoided. Pay attention to potential attacks through the file system via the website function backDir().")
                print(request.session["current_dir"])
                return JsonResponse(data="Either a back() function error or someone tried to access a parent file through unauthorised commands. Error raised to website administration.", safe=False)
        elif type == "dropInDir":
            print("--------------")
            print(request.POST["itemType"])
            print(request.POST["receiverDir"])
            print(request.POST["mvItemId"])
            if request.POST["itemType"] == "Dir":
                mvDir = request.POST["mvItemId"]
                receiverDir = request.POST["receiverDir"]
                conv = request.session["actualConv"]
                mvDir = getDir(mvDir, conv)
                receiverDir = getDir(receiverDir, conv)
                success = move_Dir(mvDir, receiverDir)
                return JsonResponse(data={"success": success})
            elif request.POST["itemType"] == "File":
                conv = request.session["actualConv"]
                receiverDir = getDir(request.POST["receiverDir"], conv)
                file = getFile(request.POST["mvItemId"], conv)
                return JsonResponse(data={"success": move_File(file, receiverDir)})
            else:
                return JsonResponse(data={"success": False})
        elif type == "addDir":
            dirName = request.POST["name"]
            conv = request.session["actualConv"]
            parent = getDir(request.session["current_dir"], conv)
            print(conv)
            conv = getConv(conv)
            createDir(parent.path, dirName, conv, parent, True)
        elif type == "deleteDir":
            dirId = request.POST["id"]
            deleteDir(dirId, request.session["actualConv"])
        elif type == "deleteFile":
            fileId = request.POST["id"]
            print("Delete file id = " + str(fileId))
            deleteFile(fileId, request.session["actualConv"])
        elif type == "getFileName":
            fileId = request.POST["id"]
            try:
                return JsonResponse(data={"title" : File.objects.get(id=fileId).Title})
            except:
                pass
        elif "deleteMsg" == type:
            msgid = request.POST['msgid']
            msg = getMsgFromConv(msgid, validatedConv)
            async_to_sync(channel_layer.group_send)("convId"+str(validatedConv.id), {'type': 'msgToDelete', "msgid": msgid})
            deleteMsg(msg)
        elif "askMsgById" == type:
            if validatedConv is None:
                return JsonResponse(data={"askMsgById": "false"})
            msg = getMsgFromConv(request.POST['msgid'], validatedConv)
            fileList = []
            replyid = None
            try:
                replyid = msg.Reply.id
            except:
                pass
            for fl in msg.files.all():
                fileList.append(fl.file.url)
            return JsonResponse({"userid": msg.Sender.id, "username": msg.Sender.username_value,
                        "convid": validatedConv.id, "edited": msg.Edited, "reply": replyid, "text": msg.Text, "files": fileList,
                        "date": msg.Date, "msgid": msg.id})
        elif "getUser" == type:
            user = request.user
            return JsonResponse({"userid": user.id, "username": user.username_value, "PP": user.PP, "email": user.email})
        elif "setPP" == type:
            user = request.user
            user.PP = request.FILES['files']
        elif "setUsername" == type:
            user = request.user
            user.username_value = request.POST['Username']
            user.save()
        elif "setPassword" == type:
            user = request.user
            user.set_password(request.POST['Password'])
            user.save()
            login(request, user)
    return JsonResponse(data="EMPTY", safe=False)

def file(request):
    perf = PerformanceProfiler("file")
    context = {}
    template = loader.get_template('Messagerie/file.html')
    context = {}
    if "connect" in request.POST:
        username = request.POST['usernameconnect']
        password = request.POST['passwordconnect']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            return redirect('log')
    elif "create" in request.POST:
        username = request.POST['username']
        email = request.POST['email']
        user = Users.objects.create_user(username, email, request.POST['password'])
        if user is not None:
            login(request, user)
        else:
            return redirect('log')
    elif "downloadFile" in request.POST:
        return download_file(request, "")
    user = request.user
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
    all_files = []
    list_subdirs = []
    try:
        all_files, list_subdirs = get_all_files(conv,
                                                )
        previous_dir = None
        if list_subdirs is not None and len(list_subdirs) == 0 and current_dir is not None:
            previous_dir = getDir(current_dir, conv)
    except:
        print("Conv deleted and not updated or unknown on get_all_files execution views.file()")

    context = {'latest_message_list': latest_message_list, 'conv_list': conv_list, 'conv_shown': conv,
               'fileform': fileform, 'list_user': list_user, 'list_files': all_files, 'list_subdir': list_subdirs,
               'current_dir': current_dir}

    return HttpResponse(template.render(context, request))

def download(request, filepath):
    if "downloadFile" in request.POST:
        file = File.objects.get(id=request.POST['downloadFile'])
        print(file)
        filename = file.Title
        fl_path = file.file.path
        print(fl_path)
        extension = pathlib.Path(filename).suffix
        filename_with_extension = "{0}{1}".format(filename, extension)
        return FileResponse(file, as_attachment=True)
    else:
        return redirect('index')
