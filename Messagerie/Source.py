import os.path

import Messagerie.models
from django.contrib.auth import *
from .models import *
from .forms import *
from enum import Enum
from .PerformanceProfiler import *
from django.shortcuts import redirect

from django.utils.text import get_valid_filename
from django.template import loader
from django.conf import settings
import shutil

class formsToInt(Enum):
    deleteMessage = 0
    editMessage = 1
    replyMessage = 2
    selectConv = 3
    deleteConv = 4
    sendMessage = 5


def handle_uploaded_file(f, name):
    #perf = PerformanceProfiler("handle_uploaded_file")
    with open("media\\files\\"+name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def handle_form_response(request, user, conv, firstConv):
    all_param = []
    if request.method == 'POST':
        if "createConv" in request.POST:
            all_param.append(createConv(request, user, request.POST.get('convName')))
            return all_param
        elif "selectConv" in request.POST:
            updatedConvID = request.POST.get('selectConv')
            if updatedConvID != conv.id:
                try:
                    request.session['actualConv'] = updatedConvID
                    conv = user.Conv_User.get(id=updatedConvID)
                    all_param.append(conv)
                    return all_param
                except:
                    conv = firstConv
                    all_param.append(conv)
                    return all_param
        elif "deleteConv" in request.POST:
            deleteConvID(request.POST.get('deleteConv'))
            if request.session['actualConv'] == request.POST.get('deleteConv'):
                conv_list = user.Conv_User.all()
                try:
                    request.session['actualConv'] = conv_list[0].id
                    conv = conv_list[0]
                    all_param.append(conv)
                    return all_param
                except:
                    latest_message_list = None
                    conv_list = None
                    conv = None
                    list_user = None
                    all_param.append(conv)
                    all_param.append(conv_list)
                    all_param.append(latest_message_list)
                    all_param.append(list_user)
                    return all_param
        elif "addToConv" in request.POST:
            addUserToConv(conv, request.POST.get("userToAdd"))

        elif "deleteMessage" in request.POST:
            deleteMsgID(request.POST.get('deleteMessage'))
        elif "kickUser" in request.POST:
            kick(conv, request.POST.get('kickUser'))
        elif "whisper" in request.POST:
            whisper(request.POST.get('whisper'), user, request, conv)
        elif "logout" in request.POST:
            logout(request)
            return redirect('log')

        elif "toFiles" in request.POST:
            # toFiles(request, user, conv)
            return redirect('file')
        elif 'deleteFile' in request.POST:
            return deleteFile(request.POST['deleteFile'])
        elif 'deleteDir' in request.POST:
            return deleteDir(request.POST['deleteDir'], conv)
        elif 'enterDir' in request.POST:
            return enterDir(request, request.POST['enterDir'], conv)
        elif 'current_dir' in request.POST:
            return previousDir(request, request.POST['current_dir'], conv)

def previousDir(request, previous_dir, conv):
    request.session['current_dir'] = previous_dir

def disconnect(user):
    print(user.sessionid)
    user.sessionid = "Empty"
    user.save()

def get_all_QS_files(conv):
    allMessages = conv.Messages.all()
    QSfiles = []
    for message in allMessages:
        if message.files.all() is not None:
            QSfiles.append(message.files.all())
    return QSfiles

def get_all_files(conv, directory, ws = False):
    if conv is not None:
        subdirs = []
        if directory is None or directory == "":
            if(ws):
                conv = Conv_User.objects.get(id=conv)
            directory = Directory.objects.get(path=(settings.MEDIA_ROOT + "\\files\\" + str(conv.id)+"\\"))
        else:
            directory = getDir(directory, conv)
        dirs = Directory.objects.filter(parent=directory)
        for dir in dirs:
            subdirs.append(dir)
        all_qs_files = File.objects.filter(directory=directory)
        all_files = []
        for file in all_qs_files:
            all_files.append(file)
        return all_files, subdirs
    else:
        return None, None

def createConv(request, user, convName):
    #perf = PerformanceProfiler("createConv")
    if convName == "":
        newConv = Conv_User(Name=user.get_username_value() + "'s Conv")
    elif convName.__len__() < 30:
        newConv = Conv_User(Name=convName)
    else:
        newConv = Conv_User(Name=convName[:24])
    newConv.save()
    user.Conv_User.add(newConv)
    user.save()
    newConv.Users.add(user)
    newConv.save()
    newDir = createDir(settings.MEDIA_ROOT + "\\files\\", newConv.id, newConv, None, True)
    newConv.dir = newDir
    newConv.save()
    request.session['actualConv'] = newConv.id

    createDir(settings.MEDIA_ROOT + "\\files\\" + str(newConv.id) + "\\", user.id, newConv, newDir, True)
    #os.mkdir(settings.MEDIA_ROOT + "\\files\\" + str(newConv.id) + "\\")
    #os.mkdir(settings.MEDIA_ROOT + "\\files\\" + str(newConv.id) + "\\" + str(user.id) + "\\")
    return newConv

def kick(conv, user):
    perf = PerformanceProfiler("kick")
    try:
        conv.Users.remove(user)
        user.Conv_User.remove(conv)
        if not conv.Users.all().exists():
            deleteConv(conv)
        conv.Name = ""
    except:
        return

def convCleaner():
    perf = PerformanceProfiler("convCleaner")
    for conv in Conv_User.objects.all():
        if not conv.Users.all().exists():
            deleteConv(conv)

def addUserToConv(Conv, user):
    #perf = PerformanceProfiler("addUserToConv")
    try:
        user_to_add = Users.objects.get(email=user)
        Conv.Users.add(user_to_add)
        user_to_add.Conv_User.add(Conv)
        os.mkdir(settings.MEDIA_ROOT + "\\files\\" + str(Conv.id) + "\\" + str(user.id) + "\\")
    except:
        return

def addUserObjToConv(Conv, user):
    #perf = PerformanceProfiler("addUserObjToConv")
    try:
        Conv.Users.get(id=user.id)
        return False
    except:
        Conv.Users.add(user)
        user.Conv_User.add(Conv)
        return True


def sendMsg(user, request):
    #perf = PerformanceProfiler("sendMsg")
    #print("Actual session to send message : ", end="")
    #print(request.session["actualConv"])
    text = request.POST.get('text')
    toAdd = None
    print("Message sent")
    files = []
    Files = []
    try:
        fileform = FileForm(request.FILES)
        conv = request.session["actualConv"]
        if conv is not None and fileform.is_valid():
            Files = request.FILES.getlist('files')
            conv = Conv_User.objects.get(id=conv)
            dir_path = settings.MEDIA_ROOT + "\\files\\" + str(conv.id) + "\\" + str(user.id) + "\\"
            dir = Directory.objects.filter(path=dir_path)
            if dir.exists():
                dir = dir[0]
            else:
                try:
                    dir = createDir(settings.MEDIA_ROOT + "\\files\\" + str(conv.id) + "\\", user.id, conv, Directory.objects.filter(path=(settings.MEDIA_ROOT + "\\files\\" + str(conv.id) + "\\"))[0], True)
                except:
                    print("Dir conv does not exist")
            i = 0
            files = []
            for f in Files:
                toAdd = File()
                toAdd.file = f
                name = toAdd.file.name.split("/")
                name = name[len(name)-1]
                toAdd.Title = name
                toAdd.file.name = str(conv.id) + "/" + str(user.pk) + "/" + name
                toAdd.directory = dir
                files.append(toAdd)
                files[i].save()
                i += 1
            if text is None:
                toAdd = Message(Sender=user, Text="", Date=timezone.now())
                toAdd.save()
                for file in files:
                    toAdd.files.add(file)
                conv.Messages.add(toAdd)
            else:
                toAdd = Message(Sender=user, Text=text, Date=timezone.now())
                toAdd.save()
                for file in files:
                    toAdd.files.add(file)
                conv.Messages.add(toAdd)
    except:
        if text is not None and conv is not None:
            conv = request.session['actualConv']
            conv = Conv_User.objects.get(id=conv)
            toAdd = Message(Sender=user, Text=text, Date=timezone.now())
            toAdd.save()
            conv.Messages.add(toAdd)
    try:
        for i in range(len(files)):
            files[i].Message = toAdd
            files[i].Author = toAdd.Sender
            files[i].save()
        return toAdd
    except:
        return -1
 

def showMessageList(conv):
   return conv.Messages.all().order_by('Date')


def whisper(Receiver, Sender, request, baseConv):
    #perf = PerformanceProfiler("whisper")
    list = Sender.Conv_User.all()
    print(list)
    Receiver = Users.objects.get(pk=Receiver)
    found = False
    for conv in list:
        if conv.Users.all().count() == 2:
            request.session['actualConv'] = conv.id
            baseConv = conv
            found = True
    if not found:
        addUserObjToConv(createConv(request, Sender, Sender.username_value + " " + Receiver.username_value), Receiver)



def deleteConvID(IDconv):
    #perf = PerformanceProfiler("deleteConvID")
    try:
        conv = Conv_User.objects.get(pk=IDconv)
        if conv is None:
            return -1
        else:
            for msg in conv.Messages.all():
                deleteMsg(msg)
            if os.path.isdir(settings.MEDIA_ROOT + "\\files\\" + str(conv.id) + "\\"):
                shutil.rmtree(settings.MEDIA_ROOT + "\\files\\" + str(conv.id) + "\\")
            conv.delete()
    except:
        print("Conv does not exist")


def deleteConv(conv):
    #perf = PerformanceProfiler("deleteConv")
    try:
        if conv is None:
            return -1
        else:
            for msg in conv.Messages.all():
                deleteMsg(msg)
            shutil.rmtree(settings.MEDIA_ROOT + "\\files\\" + str(conv.id) + "\\")
            conv.delete()
    except:
        print("Conv does not exist")

def msgCleaner():
    #perf = PerformanceProfiler("msgCleaner")
    msgList = Message.objects.all()
    convList = Conv_User.objects.all()
    tabMsg = [False]*(((Message.objects.order_by('-id')[:1])[0].id)+1)
    tabMsg2 = tabMsg
    for conv in convList:
        for msg in conv.Messages.all():
            tabMsg[msg.id]=True
    for msg in msgList:
        if tabMsg2[msg.id] == False:
            deleteMsg(msg)

def deleteMsgID(msgID):
    #perf = PerformanceProfiler("deleteMsgID")
    try:
        obj = Message.objects.get(pk=msgID)
        obj.files.all().delete()
        obj.delete()
    except:
        #print(perf.space() + )
        print("msg does not exist")

def deleteMsg(msg):
    #perf = PerformanceProfiler("deleteMsg")
    try:
        msg.files.all().delete()
        msg.delete()
    except:
        #print(perf.space() + "msg does not exist")
        print("msg does not exist")

def getUser(user_id):
    perf = PerformanceProfiler("getUser")
    try:
        return Users.objects.get(pk=user_id)
    except:
        return -1

def getConv(conv_id):
    perf = PerformanceProfiler("getConv")
    try:
        return Conv_User.objects.get(pk=conv_id)
    except:
        return -1

def fetchAskedMsg(conv, begin=0,nb=10):
    perf = PerformanceProfiler("fetchAskedMsg")
    allMsg = conv.Messages.all().order_by('-id')
    nbMsgToShow = nb+begin
    nbMsg = allMsg.count()
    if nbMsg < nbMsgToShow:
        nbMsgToShow = nbMsg
    msgList = []
    try:
        msgList = allMsg.filter(id__gte=allMsg[nbMsgToShow-1].id, id__lte=allMsg[begin].id)
    except:
        pass
    return msgList

def getLatestConv(user):
    try:
        conv = user.Conv_User.all()[:1]
    except:
        conv = -1
    return conv
    
def deleteFile(id):
    try:
        file = File.objects.get(id=id)
        if file is None:
            return -1
        else:
            file.Message.files.remove(file)
            if(not file.Message.files.all().exists() and file.Message.Text == ""):
                file.Message.delete()
            file.delete()
    except:
        print("File does not exist or isn't reached")

def getFile(file, conv):
    file = File.objects.get(id=file)
    print("Test conv")
    print(file.directory.Conv_User.id)
    print(conv)
    if(file.directory.Conv_User.id == conv):
        print("return true")
        return file
    else:
        print("Return false")
        return None

def move_File(file, parent):
    print("Enter move_file ------------------------------")
    print(file.file.path)
    print(parent.path + file.Title)
    os.rename(file.file.path, parent.path + file.Title)
    file.directory = parent
    file.file.name = parent.path + file.Title
    file.save()
    return True

def move_Dir(dir, parent):
    path = parent.path + str(dir.id) + "\\"
    if os.path.exists(path):
        return False
    else:
        dir.parent = parent
        os.rename(dir.path, path)
        dir.path = path
        dir.save()
        return True

def is_path_creatable(pathname: str) -> bool:
    dirname = os.path.dirname(pathname) or os.getcwd()
    return os.access(dirname, os.W_OK)


def is_name_safe(pathname: str):
    if(str(pathname).find("\\") or str(pathname).find("/")):
        return False
    else:
        return True


def createDir(path, title, conv, parent, useTitleInPath = False):
    print("--------------------------------------------")
    print(path)
    if (useTitleInPath):
        path = path + str(title) + "\\"
        print("Path creatable")
    if not os.path.isdir(path):
        dir = Directory()
        dir.path = path
        dir.title = title
        dir.Conv_User = conv
        dir.parent = parent
        os.makedirs(path)
        dir.save()
        return dir
    else:
        dirs = Directory.objects.filter(path=path)
        if dirs.exists():
            return dirs[0]
        else:
            dir = Directory()
            dir.path = path
            dir.title = title
            dir.Conv_User = conv
            dir.save()
            return dir


def deleteDir(id, conv):
    if conv is not None:
        dirs = Directory.objects.filter(Conv_User=conv)
        for dir in dirs:
            if str(dir.id) == id:
                dir.delete()


def enterDir(request, id, conv):
    dir = getDir(id, conv)
    request.session['current_dir'] = dir.id

def getDir(id, conv):
    if id is not None and conv is not None:
        dirs = Directory.objects.filter(Conv_User=conv)
        for dir in dirs:
            if str(dir.id) == str(id):
                return dir
        return Directory.objects.filter(Conv_User=conv).order_by("id")[0]
    return None
