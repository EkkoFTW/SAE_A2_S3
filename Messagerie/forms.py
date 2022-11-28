from django import forms
from .models import File
from django.forms import ClearableFileInput
class FileForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = File
        fields = ['file']
        widgets = {'file': ClearableFileInput(attrs={'multiple': True}), }