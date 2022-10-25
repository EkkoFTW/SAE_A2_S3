import base64
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile


class Users(AbstractBaseUser, PermissionsMixin):
    username_value = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    PP = models.CharField(max_length=1000, default="Empty", blank=True)
    sessionid = models.CharField(max_length=50, default="Empty", blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    Conv_User = models.ManyToManyField('Conv_User')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username_value']

    def get_username_value(self):
        return self.username_value

    def get_sessionid(self):
        return self.sessionid

    def set_sessionid(self, _sessionid):
        print("new sessionid: " + _sessionid)
        self.sessionid = _sessionid

    def __str__(self):
        return "Username: " + str(self.username_value) + "    Mail: " + str(self.email)

    objects = CustomUserManager()


class Conv_User(models.Model):
    Name = models.CharField(max_length=20, default="Unnamed", null=True, blank=True)
    privateKey = models.IntegerField()
    publicKey = models.IntegerField()
    Messages = models.ManyToManyField('Message')
    Users = models.ManyToManyField(Users)

    def __str__(self):
        return self.Name + " " + str(self.id)


class Conv_Admin(Conv_User):
    FOR_NOW = models.IntegerField()


class File(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='files')

class Image(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.title

class Message(models.Model):
    Sender = models.ForeignKey("Users", on_delete=models.DO_NOTHING, related_name="User_Sender")
    Reply = models.ForeignKey("self", on_delete=models.DO_NOTHING, null=True, blank=True, default=None)
    Text = models.CharField(max_length=5000)
    Date = models.DateTimeField()
    images = models.ManyToManyField(Image)

    def __str__(self):
        return "S: " + str(self.Sender) + "  R:  " + "   Texte: " + str(self.Text) + "   Time: " + str(self.Date)
