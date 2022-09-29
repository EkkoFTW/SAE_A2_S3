import base64
from django.db import models
from django.utils import timezone

class Users(models.Model):
    ID_User = models.BigAutoField(primary_key=True)
    Username = models.CharField(max_length=30)
    Password = models.CharField(max_length=30)
    PP = models.CharField(max_length=1000)

class Message(models.Model):
    ID_Message = models.BigAutoField(primary_key=True)
    ID_Sender = models.ForeignKey("Users", on_delete=models.DO_NOTHING)
    ID_Reply = models.ForeignKey("self", on_delete=models.DO_NOTHING)
    Text = models.CharField(max_length=5000)
    ID_Conv = models.IntegerField()
    Date = models.DateTimeField()

class Conv_User(models.Model):
    ID_Conv = models.BigAutoField(primary_key=True)
    ID_Message = models.ManyToManyField(Message)
    PrivateKey = models.IntegerField()
    Publickey = models.IntegerField()

class Conv_Admin(Conv_User):
    FOR_NOW = models.IntegerField()

class UserToConv(models.Model):
    ID_User = models.ForeignKey("Users", on_delete = models.DO_NOTHING)
    ID_Conv = models.ManyToManyField(Conv_Admin)

class ConvToUser(models.Model):
    ID_Conv = models.ForeignKey("Conv_User", on_delete=models.DO_NOTHING)
    ID_User = models.ManyToManyField(Users)