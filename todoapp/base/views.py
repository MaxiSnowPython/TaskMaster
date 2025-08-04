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
from django.contrib.auth import get_user_model
from django.views import View
from django.contrib import messages
from django.contrib.auth import login
from rest_framework import viewsets
from .serializer import TeamSerializer,TaskSerializer,ProfileSerializer
from .models import Task,Team,Profile



User = get_user_model()
class CustomLoginView(LoginView):
    template_name = 'base/task_login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy('hub')
    

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class RegisterPage(FormView):
    template_name = 'base/task_register.html'
    form_class = CustomUserCreationForm
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
        else:
            context['tasks'] = Task.objects.filter(team__members=self.request.user)
        return context


class HubView(LoginRequiredMixin, TemplateView):
    template_name = "base/hub.html"  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['user'] = user
        context['teams'] = Team.objects.filter(members=user)
        context['tasks'] = Task.objects.filter(user=user)

        return context
    def post(self, request, *args, **kwargs):
        user = request.user

        if "upgrade" in request.POST:
          while user.xp >= 1000:
            user.level += 1
            user.xp -= 1000
        user.save()
        return redirect('hub')

class CreateTeam(LoginRequiredMixin, CreateView):

    model = Team
    template_name = "base/create_team.html"
    fields = '__all__'
    success_url = reverse_lazy('hub')
    def form_valid(self, form):
        form.instance.user = self.request.user 
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

        if request.user == team.creator or request.user.is_superuser:
            team.members.remove(user)
            return redirect('team', team_id=team.id)
        

class TaskCreate(LoginRequiredMixin,View):
    def get(self, request, pk):
        team = get_object_or_404(Team, id=pk)
        members = team.members.all()
        return render(request, 'base/create_task.html', {
            'team': team,
            'members': members
        })
    def post(self, request, pk):
        team = get_object_or_404(Team, id=pk)
        title = request.POST.get('title')
        user_id = request.POST.get('user')
        user = get_object_or_404(User, id=user_id)
        xp = request.POST.get('xp')
        Task.objects.create(title=title, user=user, team=team,xp=xp)
        return redirect('hub')



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
        teams = Team.objects.filter(members=user)
        return render(request, 'base/status.html', {
            'friendships': friends,
            'teams': teams
        })

class TeamApi(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('name')
    serializer_class = TeamSerializer

class TaskApi(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('title')
    serializer_class = TaskSerializer

class ProfileApi(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by('user')
    serializer_class = ProfileSerializer

class TaskComplete(LoginRequiredMixin, View):
    template_name = "base/confirm_task.html"

    def get(self, request, pk, *args, **kwargs):
        """Показываем страницу подтверждения"""
        task = get_object_or_404(Task, id=pk, team__members=request.user)
        return render(request, self.template_name, {"task": task})

    def post(self, request, pk, *args, **kwargs):
        current_user = request.user
  
        task = get_object_or_404(Task, id=pk, team__members=current_user)
        if task.complete:
            messages.warning(request, "Эта задача уже выполнена.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        task.complete = True
        task.save()
        
        user = task.user
        if user:
            user.xp += task.xp or 0
            user.save()
        return redirect('hub')
