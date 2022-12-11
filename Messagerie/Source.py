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

class formsToInt(Enum):
    deleteMessage = 0
    editMessage = 1
    replyMessage = 2
    selectConv = 3
    deleteConv = 4
    sendMessage = 5


def handle_uploaded_file(f, name):
    perf = PerformanceProfiler("handle_uploaded_file")
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
        elif 'addDir' in request.POST:
            return createDir(request, user, conv)

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
def get_files_in_conv_with_path(conv, start):
    QSFilesList = get_all_QS_files(conv)
    all_files = []
    QSFilesPath = None
    print("All files in conv : ", end='')
    print(conv)
    for QSFiles in QSFilesList:
        print(QSFiles)
        if QSFiles is not None:
            QSFilesPath = []
            for lone_file in QSFiles:
                if lone_file.file.path.startswith(start):
                    QSFilesPath.append(lone_file)
        if QSFilesPath is not None:
            for file in QSFilesPath:
                all_files.append(file)
    return all_files

def get_all_files(conv, directory):
    start = settings.MEDIA_ROOT + "\\files\\" + str(conv.id)
    if directory is not None:
        start = directory.path
    all_files = get_files_in_conv_with_path(conv, start)
    dirs = 0
    start_path = start.split("/")
    subdirs = []
    for i in reversed(range(len(all_files))):
        fpart = ""
        path = all_files[i]
        path = str(path.file).split(start)
        fpart = fpart.split("/")
        if(len(fpart) > 1):
            all_files.remove(all_files[i])
    return all_files, subdirs

def createConv(user, convName):
    perf = PerformanceProfiler("createConv")
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
    perf = PerformanceProfiler("addUserToConv")
    try:
        user_to_add = Users.objects.get(email=user)
        Conv.Users.add(user_to_add)
        user_to_add.Conv_User.add(Conv)
    except:
        return

def addUserObjToConv(Conv, user):
    perf = PerformanceProfiler("addUserObjToConv")
    try:
        Conv.Users.add(user)
        user.Conv_User.add(Conv)
    except:
        return

def sendMsg(user, request):
    perf = PerformanceProfiler("sendMsg")
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
            i = 0
            files = []
            for f in Files:
                toAdd = File()
                toAdd.file = f
                name = toAdd.file.name.split("/")
                name = name[len(name)-1]
                toAdd.file.name = str(conv.id) + "/" + str(user.pk) + "/" + name
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
    perf = PerformanceProfiler("whisper")
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
    perf = PerformanceProfiler("deleteConvID")
    try:
        conv = Conv_User.objects.get(pk=IDconv)
        if conv is None:
            return -1
        else:
            for msg in conv.Messages.all():
                deleteMsg(msg)
            conv.delete()
    except:
        print("Conv does not exist")


def deleteConv(conv):
    perf = PerformanceProfiler("deleteConv")
    try:
        if conv is None:
            return -1
        else:
            for msg in conv.Messages.all():
                deleteMsg(msg)
            conv.delete()
    except:
        print("Conv does not exist")

def msgCleaner():
    perf = PerformanceProfiler("msgCleaner")
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
    perf = PerformanceProfiler("deleteMsgID")
    try:
        obj = Message.objects.get(pk=msgID)
        obj.files.all().delete()
        obj.delete()
    except:
        print(perf.space() + "msg does not exist")

def deleteMsg(msg):
    perf = PerformanceProfiler("deleteMsg")
    try:
        msg.files.all().delete()
        msg.delete()
    except:
        print(perf.space() + "msg does not exist")

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

def fetchAskedMsg(conv, begin=0,nb=20):
    allMsg = conv.Messages.all()
    nbMsg = allMsg.count()-1
    nbMsg = nbMsg - begin

    if nbMsg < 0:
        return []
    if nb > nbMsg:
        nb = nbMsg
    latest = allMsg[nbMsg]
    first = allMsg[nbMsg-nb]
    msgList = allMsg.filter(pk__lte=latest.id, pk__gte=first.id)
    return msgList

def getLatestConv(user):
    try:
        conv = user.Conv_User.all()[:1]
    except:
        conv = -1
    return conv
    
def deleteFile(id):
    try:
        file = File.objects.get(pk=id)
        if file is None:
            return -1
        else:
            file.Message.files.remove(file)
            print("Message contains :")
            print(not file.Message.files.all().exists())
            print(file.Message.Text)
            if(not file.Message.files.all().exists() and file.Message.Text == ""):
                file.Message.delete()
            file.delete()
    except:
        print("File does not exist or isn't reached")


def move_File(file, path):
    os.rename(file.file.path, path)
    file.file.path = path
    file.save()

def createDir(request, user, conv):
    given_name = ""
    dirName = settings.MEDIA_ROOT + "\\files\\" + str(conv.id) + "\\"
    if 'File_Path' in request.session:
        dirName += request.session['File_Path']
    if 'directoryName' in request.POST:
        given_name = request.POST['directoryName']
        given_name.replace("/", "\\")
        given_name = get_valid_filename(given_name)
        dirName += given_name
    else:
        given_name = 'New file'
        number = Directory.objects.all().count()
        if (number > 0):
            given_name += "(" + number + ")"
        dirName += given_name
    if(not os.path.exists(dirName)):
        dir = Directory()
        dir.path = dirName
        dir.title = given_name
        dir.Conv_User = conv
        os.mkdir(dirName)
        dir.save()

