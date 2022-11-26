import Messagerie.models
from django.contrib.auth import *
from .models import *
from .forms import *
from enum import Enum
from .PerformanceProfiler import *

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

def login(Username, Passwd):
    perf = PerformanceProfiler("login")
    #print('DEBUG: function "login(' + str(Username) + ', ' + str(Passwd) + ') ---> ', end="")
    user = authenticate(username=Username, password=Passwd)
    if user is not None:
        print('connection: succeed ---> ', end="")
        return user
    else:
        print("connection: failed")
        return -1

def auto_login(Sessionid, Userid):
    perf = PerformanceProfiler("auto_login")
    #print('DEBUG: function "auto_login(' + str(Sessionid) + ', ' + str(Userid) + ') ---> ', end="")
    if Sessionid is None or Userid is None:
        #print("Nop")
        return -1
    user = Users.objects.get(email=Userid)
    if user is None:
        #print("userid dosn't exist")
        #print("")
        return -1
    sessionid = user.sessionid
    if sessionid == Sessionid:
        #print("Connected to " + str(user))
        return user
    else:
        #print("Wrong SessionID for " + str(user))
        return -1

def createConv(request, user, convName):
    perf = PerformanceProfiler("createConv")
    if convName == "":
        newConv = Conv_User(privateKey=1, publicKey=1, Name=user.get_username_value() + "'s Conv")
    elif convName.__len__() < 25:
        newConv = Conv_User(privateKey=1, publicKey=1, Name=convName)
    else:
        newConv = Conv_User(privateKey=1, publicKey=1, Name=convName[:24])
    newConv.save()
    user.Conv_User.add(newConv)
    user.save()
    newConv.Users.add(user)
    newConv.save()
    request.session['actualConv'] = newConv.id
    return newConv

def kick(conv, user_id):
    perf = PerformanceProfiler("kick")
    try:
        if(user_id):
            rm = conv.Users.get(id=user_id)
            conv.Users.remove(rm)
            rm.Conv_User.remove(conv)
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
    #print("Actual session to send message : ", end="")
    #print(request.session["actualConv"])
    text = request.POST.get('text')

    try:
        if False and text.__len__() > 5000:
            text = text[:5000]
        fileform = FileForm(request.FILES)
        conv = request.session["actualConv"]
        if conv is not None and fileform.is_valid():
            file = File()
            file.file = request.FILES['file']
            file.save()
            conv = Conv_User.objects.get(id=conv)
            if text is None:
                toAdd = Message(Sender=user, Text="", Date=timezone.now())
                toAdd.save()
                toAdd.files.add(file)
                conv.Messages.add(toAdd)
            else:
                toAdd = Message(Sender=user, Text=text, Date=timezone.now())
                toAdd.save()
                toAdd.files.add(file)
                conv.Messages.add(toAdd)
    except:
        if text is not None and conv is not None:
            conv = Conv_User.objects.get(id=conv)
            toAdd = Message(Sender=user, Text=text, Date=timezone.now())
            toAdd.save()
            conv.Messages.add(toAdd)

def showMessageList(user, request):
    perf = PerformanceProfiler("showMessageList")
    conv_list = user.Conv_User.all()
    try:
        firstConv = conv_list[0]
    except:
        return None, None, None, None

    conv = firstConv
    try:
        OldConv = conv_list.get(id=request.session['actualConv'])
        conv = OldConv
    except:
        pass

    try:
        request.session['actualConv']
    except:
        request.session['actualConv'] = conv.id

    if request.method == 'POST':
        if "selectConv" in request.POST:
            updatedConvID = request.POST.get('selectConv')
            if updatedConvID != conv.id:
                try:
                    request.session['actualConv'] = updatedConvID
                    conv = user.Conv_User.get(id=updatedConvID)
                except:
                    conv = firstConv
        elif "sendMessage" in request.POST:
            try:
                sendMsg(user, request)
            except:
                pass
        elif "deleteConv" in request.POST:
            deleteConvID(request.POST.get('deleteConv'))
            if request.session['actualConv'] == request.POST.get('deleteConv'):
                conv_list = user.Conv_User.all()
                try:
                    request.session['actualConv'] = conv_list[0].id
                    conv = conv_list[0]
                except:
                    return None, None, None, None
        elif "addToConv" in request.POST:
            addUserToConv(conv, request.POST.get("userToAdd"))

        elif "deleteMessage" in request.POST:
            deleteMsg(request.POST.get('deleteMessage'))
        elif "kickUser" in request.POST:
            kick(conv,request.POST.get('kickUser'))
        elif "whisper" in request.POST:
            whisper(request.POST.get('whisper'), user, request, conv)
    latest_message_list = conv.Messages.all().order_by('Date')

    return latest_message_list, conv_list, conv, conv.Users.all()


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
            conv.Messages.all().delete()
            conv.delete()
    except:
        print("Conv does not exist")


def deleteConv(conv):
    perf = PerformanceProfiler("deleteConv")
    try:
        if conv is None:
            return -1
        else:
            conv.Messages.all().delete()
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
            msg.delete()

def deleteMsg(msgID):
    perf = PerformanceProfiler("deleteMsg")
    print(msgID)
    try:
        Message.objects.get(pk=msgID).delete()
    except:
        print("msg does not exist")
