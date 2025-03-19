from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login

from .models import Task,Team,Reward,UserProfile


# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'base/task_login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy('hub')
    

class RegisterPage(FormView):
    template_name = 'base/task_register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("tasks")
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request,user)
        return super().form_valid(form)
    
    def get(self,*args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage,self).get(*args, **kwargs)

class TeamList(LoginRequiredMixin,TemplateView):
    template_name = "base/task_list.html"
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['teams'] = Team.objects.filter(members=self.request.user)
        team_id = self.kwargs.get('team_id')
        if team_id:
            context['team'] = Team.objects.get(id=team_id, members=self.request.user)
            context['tasks'] = Task.objects.filter(team_id=team_id, team__members=self.request.user)
            context['rewards'] = Reward.objects.filter(task__team_id=team_id, user=self.request.user)    
        else:
            # Если team_id не передан, показываем все задачи и награды пользователя
            context['tasks'] = Task.objects.filter(team__members=self.request.user)
            context['rewards'] = Reward.objects.filter(task__user=self.request.user, user=self.request.user)
            
        return context


class HubView(LoginRequiredMixin, TemplateView):
    template_name = "base/hub.html"  # Шаблон, который будет использоваться

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user  # Получаем текущего пользователя
        
        context['user'] = user
        context['teams'] = Team.objects.filter(members=user)
        context['tasks'] = Task.objects.filter(user=user)
        context['rewards'] = Reward.objects.filter(user=user)
        context['leaderboard'] = UserProfile.objects.order_by('-xp')[:10]  # Топ-10 игроков

        return context