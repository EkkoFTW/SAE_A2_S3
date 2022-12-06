from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('Log', views.log, name="log"),
    path('file', views.file, name="file")
]
