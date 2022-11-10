import Messagerie.models
from django.contrib.auth import *
from .models import *
from .forms import *

def handle_uploaded_file(f, name):
    with open("media\\files\\"+name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def login(Username, Passwd):
    print('DEBUG: function "login(' + str(Username) + ', ' + str(Passwd) + ') ---> ', end="")
    user = authenticate(username=Username, password=Passwd)
    if user is not None:
        print('connection: succeed ---> ', end="")
        return user
    else:
        print("connection: failed")
        return -1

def auto_login(Sessionid, Userid):
    print('DEBUG: function "auto_login(' + str(Sessionid) + ', ' + str(Userid) + ') ---> ', end="")
    if Sessionid is None or Userid is None:
        print("Nop")
        return -1
    user = Users.objects.get(email=Userid)
    if user is None:
        print("userid dosn't exist")
        print("")
        return -1
    sessionid = user.sessionid
    if sessionid == Sessionid:
        print("Connected to " + str(user))
        return user
    else:
        print("Wrong SessionID for " + str(user))
        return -1

def createConv(request, user):
    newConv = Conv_User(privateKey=1, publicKey=1, Name=user.get_username_value() + "'s Conv")
    newConv.save()
    user.Conv_User.add(newConv)
    user.save()
    newConv.Users.add(user)
    newConv.save()
    return newConv


def addUserToConv(Conv, user):
    for usr in user:
        updateConv = Conv.Users.add(usr)
        updateConv.save()
        updateUsr = usr.Conv_User.add(user)
        updateUsr.save()


def sendMsg(user, request):
    conv = request.POST.get('conv')
    text = request.POST.get('text')
    fileform = FileForm(request.POST, request.FILES)
    try:
        if conv is not None and fileform.is_valid():
            handle_uploaded_file(request.FILES['file'], request.POST['title'])
            file = File()
            file.file = request.FILES['file']
            file.title = request.POST['title']
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
    conv_list = user.Conv_User.all()
    print(conv_list)
    print(conv_list.filter(id=1))
    try:
        firstConv = conv_list[0]
    except:
        return None, None, None
    conv = firstConv
    updatedConvID = request.POST.get('conv')
    if request.method == 'POST':
        if "sendMessage" in request.POST:
            sendMsg(user, request)
    if updatedConvID != conv.id:
        try:
            conv = user.Conv_User.get(id=updatedConvID)
        except:
            conv = firstConv

    latest_message_list = conv.Messages.all().order_by('Date')

    return latest_message_list, conv_list, conv

def deleteConv(IDconv):
    try:
        conv = Conv_User.objects.get(pk=IDconv)
        if conv is None:
            return -1
        else:
            #conv.Messages.all().delete()
            conv.delete()
    except:
        print("Conv does not exist")

def msgCleaner():
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