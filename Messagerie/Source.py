import Messagerie.models
from django.contrib.auth import *
from .models import *
from .forms import *
from enum import Enum
class formsToInt(Enum):
    deleteMessage = 0
    editMessage = 1
    replyMessage = 2
    selectConv = 3
    deleteConv = 4
    sendMessage = 5


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
    request.session['actualConv'] = newConv.id
    return newConv

def kick(request, user_id):
    try:
        if(user_id):
            conv = Conv_User.objects.get(id=request.session["actualConv"])
            conv.Users.get(id=user_id).delete()
    except:
        return -1



def addUserToConv(Conv, user):
    for usr in user:
        user_to_add = Users.objects.get(email=usr)
        updateConv = Conv.Users.add(user_to_add)
        updateConv.save()
        updateUsr = user_to_add.Conv_User.add(Conv)
        updateUsr.save()


def sendMsg(user, request):
    print("Actual session to send message : ", end="")
    print(request.session["actualConv"])
    text = request.POST.get('text')
    fileform = FileForm(request.POST, request.FILES)
    try:
        conv = request.session["actualConv"]
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
            sendMsg(user, request)
        elif "deleteConv" in request.POST:
            deleteConv(request.POST.get('deleteConv'))
            if request.session['actualConv'] == request.POST.get('deleteConv'):
                conv_list = user.Conv_User.all()
                try:
                    request.session['actualConv'] = conv_list[0].id
                    conv = conv_list[0]
                except:
                    return None, None, None
        elif "addToConv" in request.POST:
            addUserToConv(conv, request.POST.get("userToAdd"))

        elif "deleteMessage" in request.POST:
            deleteMsg(request.POST.get('deleteMessage'))

    latest_message_list = conv.Messages.all().order_by('Date')
    return latest_message_list, conv_list, conv, conv.Users.all()

def deleteConv(IDconv):
    try:
        conv = Conv_User.objects.get(pk=IDconv)
        if conv is None:
            return -1
        else:
            conv.Messages.all().delete()
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

def deleteMsg(msgID):
    print(msgID)
    try:
        Message.objects.get(pk=msgID).delete()
    except:
        print("msg does not exist")
