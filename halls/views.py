from halls.forms import SearchForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import Http404, JsonResponse
from django.forms.utils import ErrorList

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

from . import models
from . import forms

import urllib
import requests

YOUTUBE_API_KEY = 'AIzaSyB97ldAKPu8tRKgQBHU-BO2MkT5-Nw3ylE'


def get_youtube_api_url(video_id, api_key):
    return f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id }&key={ api_key }'


def home(request):
    return render(request, 'halls/home.html')


def dashboard(request):
    return render(request, 'halls/dashboard.html')


def add_video(request, pk):
    form = forms.VideoForm()
    search_form = forms.SearchForm()
    hall = models.Hall.objects.get(pk=pk)

    if not hall.user == request.user:
        raise Http404

    if request.method == 'POST':
        form = forms.VideoForm(request.POST)
        if form.is_valid():
            video = models.Video()
            video.url = form.cleaned_data['url']
            video.hall = hall

            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id = video_id[0]
                response = requests.get(get_youtube_api_url(video_id[0], YOUTUBE_API_KEY))
                json = response.json()
                title = json['items'][0]['snippet']['title']
                video.title = title
                video.save()
                return redirect('detail_hall', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Needs to be a YouTube URL')

    return render(request, 'halls/add_video.html', {'form': form, 'search_form': search_form, 'hall': hall})


def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        return JsonResponse({'hello': search_form.cleaned_data['search_term']})
    return JsonResponse({'hello': 'Not working'})


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view


class CreateHall(generic.CreateView):
    model = models.Hall
    fields = ['title']
    template_name = 'halls/create_hall.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHall, self).form_valid(form)
        return redirect('home')


class DetailHall(generic.DetailView):
    model = models.Hall
    template_name = 'halls/detail_hall.html'


class UpdateHall(generic.UpdateView):
    model = models.Hall
    template_name = 'halls/update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')


class DeleteHall(generic.DeleteView):
    model = models.Hall
    template_name = 'halls/delete_hall.html'
    success_url = reverse_lazy('dashboard')
