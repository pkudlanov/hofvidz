from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

from . import models
from . import forms


def home(request):
    return render(request, 'halls/home.html')


def dashboard(request):
    return render(request, 'halls/dashboard.html')


def add_video(request, pk):
    form = forms.VideoForm()

    if request.method == 'POST':
        filled_form = forms.VideoForm(request.POST)
        if filled_form.is_valid():
            video = models.Video()
            video.url = filled_form.cleaned_data['url']
            video.title = filled_form.cleaned_data['title']
            video.youtube_id = filled_form.cleaned_data['youtube_id']
            video.hall = models.Hall.objects.get(pk=pk)
            video.save()

    return render(request, 'halls/add_video.html', {'form': form})


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
