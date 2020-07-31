from . import models
from django import forms


class VideoForm(forms.ModelForm):
    class Meta:
        model = models.Video
        fields = ['title', 'url', 'youtube_id']
