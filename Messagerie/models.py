import base64
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager

class Users(AbstractBaseUser, PermissionsMixin):
    username_value = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    PP = models.CharField(max_length=1000, default="Empty", blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username_value']

    def get_username_value(self):
        return self.username_value

    def __str__(self):
        return "Username: " + str(self.username_value) + "    Mail: " + str(self.email)

    objects = CustomUserManager()

class Message(models.Model):
    ID_Sender = models.ForeignKey("Users", on_delete=models.DO_NOTHING, related_name="User_Sender")
    ID_Reply = models.ForeignKey("self", on_delete=models.DO_NOTHING, null=True, blank=True)
    Text = models.CharField(max_length=5000)
    ID_Conv = models.IntegerField()
    Date = models.DateTimeField()

    def __str__(self):
        return "S: " + str(self.ID_Sender) + "  R:  " + "   Texte: " + str(self.Text) + "   Time: " + str(self.Date)

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
