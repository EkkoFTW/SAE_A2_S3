import Messagerie.models
from django.contrib.auth import *
from .models import Users
def login(Username, Passwd):
    print('DEBUG: function "login('+ str(Username) + ', ' + str(Passwd) +') ---> ', end="")
    user = authenticate(username=Username, password=Passwd)
    if user is not None:
        print('connection: succeed ---> ', end="")
        return user
    else:
        print("connection: failed")
        return -1