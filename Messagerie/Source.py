import Messagerie.models
from django.contrib.auth import *
from .models import *
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
    if type(user) is None:
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
    try:
        if text is not None and conv is not None:
            conv = Conv_User.objects.get(id=conv)
            toAdd = Message(Sender=user, Text=text, Date=timezone.now())
            toAdd.save()

            conv.Messages.add(toAdd)
    except:
        print("Conv does not exist")

def showMessageList(user, request):

    conv_list = user.Conv_User.all()
    firstConv = conv_list[0]
    conv = firstConv
    updatedConvID = request.POST.get('conv')

    if updatedConvID != conv.id:
        try:
            conv = user.Conv_User.get(id=updatedConvID)
        except:
            conv = firstConv

    latest_message_list = conv.Messages.all().order_by('-Date')[:4]
    sendMsg(user, request)

    return latest_message_list, conv_list, conv

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


