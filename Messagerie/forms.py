from django import forms
from .models import Image
from .models import File


class ImageForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = Image
        fields = ('title', 'image')

class FileForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = File
        fields = ('title', 'file')