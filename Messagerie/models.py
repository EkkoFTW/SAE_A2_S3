import base64
from django.db import models
from django.utils import timezone

class Users(models.Model):
    Username = models.CharField(max_length=30)
    Password = models.CharField(max_length=30)
    PP = models.CharField(max_length=1000)

    def __str__(self):
        return self.Username

class Message(models.Model):
    ID_Sender = models.ForeignKey("Users", on_delete=models.DO_NOTHING, related_name="User_Sender")
    ID_Receiver = models.ForeignKey("Users", on_delete=models.DO_NOTHING, related_name="User_Receiver")
    ID_Reply = models.ForeignKey("self", on_delete=models.DO_NOTHING, null=True, blank=True)
    Text = models.CharField(max_length=5000)
    ID_Conv = models.IntegerField()
    Date = models.DateTimeField()

    def __str__(self):
        return "S: " + str(self.ID_Sender) + "  R:  " + str(self.ID_Receiver) + "   Texte: " + str(self.Text) + "   Time: " + str(self.Date)

class Conv_User(models.Model):
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
