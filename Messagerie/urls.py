from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('Log', views.log, name="log"),
    path('handler', views.handler, name="handler"),
    path('file', views.file, name="file"),
    path("<str:filepath>/", views.download_file, name="download")
]
