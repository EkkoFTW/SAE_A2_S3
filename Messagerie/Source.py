import Messagerie.models
from django.contrib.auth import *

def login(Username, Passwd):
    print('DEBUG: function "login('+ str(Username) + ', ' + str(Passwd) +')" ---> ', end="")
    user = authenticate(username=Username, password=Passwd)
    if user is not None:
        print('connection: succeed')
        return user
    else:
        print("connection: failed")
        return -1
