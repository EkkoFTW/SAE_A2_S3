import base64
from django.db import models

class Message(models.Model):
    ID_Message = models.IntegerField()
    ID_Sender = models.IntegerField()
    ID_Reply = models.IntegerField(default=0)
    Text = models.CharField(max_length=5000)
    ID_Conv = models.IntegerField()
    Date = models.DateTimeField('date_published')

class Users(models.Model):
    ID_User = models.IntegerField()
    Username = models.CharField(max_length=30)
    Password = models.CharField(max_length=30)
    PP = models.CharField(max_length=1000)

class UserToConv(models.Model):
    ID_User = models.IntegerField()
    ID_Conv = models.TextField(db_column='data',blank=True)

    def set_data(self, data):
        self._data = base64.encodestring(data)

    def get_data(self):
         return base64.decodestring(self._data)

    data = property(get_data, set_data)

class ConvToUser(models.Model):
    ID_Conv = models.IntegerField();
    ID_User = models.TextField(db_column='data',blank=True)

    def set_data(self, data):
        self._data = base64.encodestring(data)

    def get_data(self):
         return base64.decodestring(self._data)

    data = property(get_data, set_data)

class Conv_User(models.Model):
    ID_Conv = models.IntegerField();
    ID_User = models.TextField(db_column='data',blank=True)
    PrivateKey = models.IntegerField()
    Publickey = models.IntegerField()
    def set_data(self, data):
        self._data = base64.encodestring(data)

    def get_data(self):
         return base64.decodestring(self._data)

    data = property(get_data, set_data)

class Conv_Admin(models.Model):
    ID_Conv = models.IntegerField()
    ID_Message = models.TextField(db_column='data', blank=True)
    PrivateKey = models.IntegerField()
    Publickey = models.IntegerField()
    def set_data(self, data):
        self._data = base64.encodestring(data)

    def get_data(self):
         return base64.decodestring(self._data)

    data = property(get_data, set_data)
