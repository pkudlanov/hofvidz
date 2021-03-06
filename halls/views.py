from halls.forms import SearchForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import Http404, JsonResponse
from django.forms.utils import ErrorList

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from . import models
from . import forms

import urllib
import requests

YOUTUBE_API_KEY = 'AIzaSyB97ldAKPu8tRKgQBHU-BO2MkT5-Nw3ylE'


def youtube_api_video_data_url(video_id, api_key):
    return f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id }&key={ api_key }'


def youtube_api_search_results_url(search, api_key):
    return f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q={ search }&key={ api_key }'


def home(request):
    recent_halls = models.Hall.objects.all().order_by('-id')[:3]
    print(models.Hall.objects.all())
    if len(models.Hall.objects.all()) == 0:
        popular_halls = []
    else:
        popular_halls = [models.Hall.objects.get(pk=1), models.Hall.objects.get(pk=2), models.Hall.objects.get(pk=3)]
    return render(request, 'halls/home.html', {'recent_halls': recent_halls, 'popular_halls': popular_halls})


@login_required
def dashboard(request):
    halls = models.Hall.objects.filter(user=request.user)
    return render(request, 'halls/dashboard.html', {'halls': halls})


@login_required
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
                response = requests.get(youtube_api_video_data_url(video_id[0], YOUTUBE_API_KEY))
                try:
                    response.json()['items']
                except KeyError:
                    errors = form._errors.setdefault('url', ErrorList())
                    errors.append('Hit YouTube queries limit')
                else:
                    json = response.json()
                    title = json['items'][0]['snippet']['title']
                    video.title = title
                    video.save()
                    return redirect('detail_hall', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Needs to be a YouTube URL')

    return render(request, 'halls/add_video.html', {'form': form, 'search_form': search_form, 'hall': hall})


@login_required
def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        encoded_search_term = urllib.parse.quote(search_form.cleaned_data['search_term'])
        response = requests.get(youtube_api_search_results_url(encoded_search_term, YOUTUBE_API_KEY))
        return JsonResponse(response.json())
    return JsonResponse({'error': 'Not able to validate form'})


class DeleteVideo(LoginRequiredMixin, generic.DeleteView):
    model = models.Video
    template_name = 'halls/delete_video.html'
    success_url = reverse_lazy('dashboard')

    # Make sure the loged in user owns the video
    def get_object(self):
        video = super(DeleteVideo, self).get_object()
        if not video.hall.user == self.request.user:
            raise Http404
        return video


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')
    template_name = 'registration/signup.html'

    # This method is called when valid form data has been POSTed.
    # To log a user in when the form is validated.
    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view


class CreateHall(LoginRequiredMixin, generic.CreateView):
    model = models.Hall
    fields = ['title']
    template_name = 'halls/create_hall.html'
    success_url = reverse_lazy('dashboard')

    # This method is called when valid form data has been POSTed.
    def form_valid(self, form):
        # Adding the current user into the form
        # Required for the Hall model
        form.instance.user = self.request.user

        # Performing validation ourselves
        return super(CreateHall, self).form_valid(form)


class DetailHall(generic.DetailView):
    model = models.Hall
    template_name = 'halls/detail_hall.html'


class UpdateHall(LoginRequiredMixin, generic.UpdateView):
    model = models.Hall
    template_name = 'halls/update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        hall = super(UpdateHall, self).get_object()
        if not hall.user == self.request.user:
            raise Http404
        return hall


class DeleteHall(LoginRequiredMixin, generic.DeleteView):
    model = models.Hall
    template_name = 'halls/delete_hall.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        hall = super(DeleteHall, self).get_object()
        if not hall.user == self.request.user:
            raise Http404
        return hall
