import Messagerie.models
from django.contrib.auth import *
from .models import *
def login(Username, Passwd, sessionid):
    print('DEBUG: function "login('+ str(Username) + ', ' + str(Passwd) +') ---> ', end="")
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
    user = Users.objects.get(username_value=Userid)
    if type(user) == type(Users):
        print("userid dosn't exist")
        return -1
    sessionid = user.get_sessionid()
    print(user)
    print(sessionid)
    if sessionid == Sessionid:
        return user
    else:
        return -1

def createConv(request, user):
    newConv = Conv_User(privateKey=1, publicKey=1)
    newConv.save()
    user.Conv_User.add(newConv)
    user.save()
    newConv.Users.add(user)
    newConv.save()
    return newConv


def addUserToConv(Conv, user):
    for usr in user:
        updateConv = Conv.Users.add(usr)
        updateUsr = usr.Conv_User.add(user)
        updateUsr.save()
    updateConv.save()



