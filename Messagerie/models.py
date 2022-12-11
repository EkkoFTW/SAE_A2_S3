import base64
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager
from django.dispatch import receiver
import os
import shutil
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from Messagerie.PerformanceProfiler import PerformanceProfiler

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
    Messages = models.ManyToManyField('Message')
    Users = models.ManyToManyField(Users)
    def __str__(self):
        return self.Name + " " + str(self.id)


class Conv_Admin(Conv_User):
    FOR_NOW = models.IntegerField()


class File(models.Model):
    Title = models.CharField(max_length=200, default="file")
    file = models.FileField(upload_to='files', blank=True)
    Message = models.ForeignKey('Message', on_delete=models.SET_NULL, blank=True, null=True)
    Author = models.ForeignKey('users', on_delete=models.SET_NULL, blank=True, null=True)
    dateAdded = models.DateTimeField(default=timezone.now)
@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            dirs = File.objects.filter(path__contains=instance.path)
            for dir in dirs:
                dir.delete()
            os.remove(instance.file.path)

class Message(models.Model):
    Sender = models.ForeignKey("Users", on_delete=models.DO_NOTHING, related_name="User_Sender")
    Reply = models.ForeignKey("self", on_delete=models.DO_NOTHING, null=True, blank=True, default=None)
    Text = models.CharField(max_length=5000)
    Date = models.DateTimeField()
    files = models.ManyToManyField(File)

    def __str__(self):
        return "id: " + str(self.id) + "S: " + str(self.Sender) + "  R:  " + "   Texte: " + str(self.Text) + "   Time: " + str(self.Date)

class Directory(models.Model):
    title = models.CharField(max_length=100)
    path = models.CharField(max_length=300, unique=True)
    Conv_User = models.ForeignKey("Conv_User", on_delete=models.CASCADE)
    parent = models.ForeignKey("Directory", on_delete=models.CASCADE, null=True, blank=True)
    child_files = models.ForeignKey("File", on_delete=models.DO_NOTHING, null=True, blank=True)

@receiver(models.signals.post_delete, sender=Directory)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if os.path.isdir(instance.path):
        shutil.rmtree(instance.path)