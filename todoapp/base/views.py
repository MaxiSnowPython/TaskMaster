from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views import View
from django.contrib import messages
from django.contrib.auth import login

from .models import Task,Team,Reward,UserProfile,Profile


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
    success_url = reverse_lazy("hub")
    
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
            context['rewards'] = Reward.objects.all()  
        else:
            # Если team_id не передан, показываем все задачи и награды пользователя
            context['tasks'] = Task.objects.filter(team__members=self.request.user)
            context['rewards'] = Reward.objects.all()
            
        return context


class HubView(LoginRequiredMixin, TemplateView):
    template_name = "base/hub.html"  # Шаблон, который будет использоваться

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user  # Получаем текущего пользователя
        
        context['user'] = user
        context['teams'] = Team.objects.filter(members=user)
        context['tasks'] = Task.objects.filter(user=user)
        context['rewards'] = Reward.objects.filter()
        context['leaderboard'] = UserProfile.objects.order_by('-xp')[:10]  # Топ-10 игроков

        return context


class CreateTeam(LoginRequiredMixin, CreateView):

    model = Team
    template_name = "base/create_team.html"
    fields = '__all__'
    success_url = reverse_lazy('hub')
    def form_valid(self, form):
        form.instance.user = self.request.user  # Привязываем задачу к текущему пользователю
        return super().form_valid(form)
    
class TaskDelete(LoginRequiredMixin,DeleteView):
    model = Task
    context_object_name = "taskd"
    success_url = reverse_lazy("hub")
    template_name = "base/delete_task.html"

class TeamMemberDelete(LoginRequiredMixin, View):
    template_name = "base/delete_from_team.html"
    def post(self, request, team_id, user_id):
        team = get_object_or_404(Team, pk=team_id)
        user = get_object_or_404(User, pk=user_id)

        # Удаляем участника из команды
        if request.user == team.creator or request.user.is_superuser:
            team.members.remove(user)
            return redirect('team', team_id=team.id)
        

class TaskCreate(LoginRequiredMixin,CreateView):
    model = Task
    template_name = "base/create_task.html"
    fields = ['title','user','xp']
    success_url = reverse_lazy("hub")
    def form_valid(self, form):
        team = get_object_or_404(Team, pk=self.kwargs['pk'])
        form.instance.team = team  # привязываем команду из URL
        return super().form_valid(form)



class AddFriendToTeamView(LoginRequiredMixin, View):
    def post(self, request):
        username = request.POST.get('username')
        to_user = User.objects.filter(username=username).first()

        if to_user and request.user != to_user:
            from_profile = request.user.profile
            to_profile = to_user.profile

            if to_user not in from_profile.friends.all():
                from_profile.friends.add(to_user)
                to_profile.friends.add(request.user)
        return redirect('hub')

    def get(self, request):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)
            messages.error(request, "Profile does not exist, new profile created.")

        friends = profile.friends.all()
        teams = Team.objects.filter(creator=user)
        return render(request, 'base/status.html', {
            'friendships': friends,
            'teams': teams
        })