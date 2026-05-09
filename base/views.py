from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db.models import Q
from friendship.models import Friend, FriendshipRequest
from django.contrib.auth import get_user_model, login
from django.views import View
from django.contrib import messages
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializer import TeamSerializer, TaskSerializer
from .models import CustomUser, Task, Team, Difficulty, Item, UserItem
import random

User = get_user_model()

CLASS_CHOICES = [
    ('', 'Выбери роль'),
    ('Backend Developer', 'Backend Developer'),
    ('Frontend Developer', 'Frontend Developer'),
    ('Team Lead', 'Team Lead'),
    ('QA Engineer', 'QA Engineer'),
    ('DevOps Engineer', 'DevOps Engineer'),
    ('Data Analyst', 'Data Analyst'),
    ('Product Manager', 'Product Manager'),
    ('UI/UX Designer', 'UI/UX Designer'),
]


class EditProfileForm(forms.ModelForm):
    podclass = forms.ChoiceField(choices=CLASS_CHOICES, label='Класс героя', required=False)

    class Meta:
        model = CustomUser
        fields = ['podclass', 'avatar']


class CustomLoginView(LoginView):
    template_name = 'base/task_login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy('hub')
    

class CustomUserCreationForm(UserCreationForm):
    podclass = forms.ChoiceField(choices=CLASS_CHOICES, label='Класс героя', required=False)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'podclass']


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
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('hub')
        return super(RegisterPage, self).get(*args, **kwargs)

class TeamList(LoginRequiredMixin,TemplateView):
    template_name = "base/task_list.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['teams'] = Team.objects.filter(members=self.request.user)
        team_id = self.kwargs.get('team_id')
        if team_id:
            context['team'] = get_object_or_404(Team, id=team_id, members=self.request.user)
            context['tasks'] = Task.objects.filter(team_id=team_id, team__members=self.request.user) 
        else:
            context['tasks'] = Task.objects.filter(team__members=self.request.user)
        return context

class EditProfile(LoginRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'base/edit_profile.html'
    form_class = EditProfileForm
    success_url = reverse_lazy('hub')

    def get_object(self, queryset=None):
        return self.request.user


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
    fields = ['name']
    success_url = reverse_lazy('hub')
    def form_valid(self, form):
        form.instance.creator = self.request.user
        member_usernames = self.request.POST.getlist('members')
        response = super().form_valid(form)
        form.instance.members.add(self.request.user)
        for username in member_usernames:
            user = User.objects.filter(username=username).first()
            if user and Friend.objects.are_friends(self.request.user, user):
                form.instance.members.add(user)
            else:
                messages.error(self.request, f'Пользователь {username} не является вашим другом.')
        messages.success(self.request, 'Команда создана!')
        return response
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['friends'] = Friend.objects.friends(user=self.request.user)
        return context
    
class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "taskd"
    success_url = reverse_lazy("hub")
    template_name = "base/delete_task.html"

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(team__creator=user) | Q(user=user))

class TeamMemberDelete(LoginRequiredMixin, View):
    template_name = "base/delete_from_team.html"
    def post(self, request, team_id, user_id):
        team = get_object_or_404(Team, pk=team_id)
        user = get_object_or_404(User, pk=user_id)

        if request.user == team.creator or request.user.is_superuser:
            team.members.remove(user)
            return redirect('team', team_id=team.id)
        messages.error(request, 'У вас нет прав для этого действия.')
        return redirect('hub')


class TaskCreate(LoginRequiredMixin,View):
    def get(self, request, pk):
        team = get_object_or_404(Team, id=pk, members=request.user)
        members = team.members.all()
        diff = Difficulty.objects.all()
        is_creator = team.creator == request.user
        items = Item.objects.all() if is_creator else None
        return render(request, 'base/create_task.html', {
            'team': team,
            'members': members,
            'diff': diff,
            'items': items,
            'is_creator': is_creator,
        })

    def post(self, request, pk):
        team = get_object_or_404(Team, id=pk, members=request.user)
        title = request.POST.get('title')
        user_id = request.POST.get('user')
        difficulty_id = request.POST.get('difficulty')
        difficulty = get_object_or_404(Difficulty, id=difficulty_id)
        user = get_object_or_404(User, id=user_id)
        xp = request.POST.get('xp')

        try:
            xp = int(xp)
        except ValueError:
            messages.error(request, "XP должно быть числом.")
            return redirect(request.path)
        if xp > difficulty.max_xp:
            messages.error(request, f"XP не может превышать лимит сложности ({difficulty.max_xp}).")
            return redirect(request.path)
        if xp < 0:
            messages.error(request, f"XP не может быть меньше нуля")
            return redirect(request.path)

        reward_item = None
        if team.creator == request.user:
            item_id = request.POST.get('reward_item')
            if item_id:
                reward_item = Item.objects.filter(id=item_id).first()

        Task.objects.create(title=title, user=user, team=team, xp=xp, difficulty=difficulty, reward_item=reward_item)

        return redirect('hub')



class FriendList(LoginRequiredMixin, View):
    template_name = 'base/status.html'
    login_url = '/login/'

    def post(self, request,):
        
        username = request.POST.get('username')
        to_user = User.objects.filter(username=username).first()

        if not to_user:
            messages.error(request, 'Пользователь не найден.')
            return redirect('friendslist')

        if to_user == request.user:
            messages.error(request, 'Нельзя добавить себя в друзья.')
            return redirect('friendslist')

        if Friend.objects.are_friends(request.user, to_user):
            messages.error(request, 'Вы уже друзья.')
            return redirect('friendslist')
        

        Friend.objects.add_friend(
            from_user=request.user,
            to_user=to_user,
            message="Привет! Хочу добавить тебя в друзья."
        )
        messages.success(request, 'Запрос на дружбу отправлен!')
        return redirect('hub')

    def get(self, request):
        friend_requests = Friend.objects.unrejected_requests(user=request.user)
        friends = Friend.objects.friends(user=request.user)
        teams = Team.objects.filter(members=request.user)
        all_users = User.objects.exclude(id=request.user.id)
        return render(request, self.template_name,{
            'friend_requests': friend_requests,
            'friends': friends,
            'teams': teams,
            'all_users': all_users
        })

class TeamApi(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('name')
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

class TaskApi(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('title')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]




class TaskComplete(LoginRequiredMixin, View):
    template_name = "base/confirm_task.html"

    def get(self, request, pk, *args, **kwargs):
       
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
            user.xp += task.xp
            user.save()

            if task.reward_item:
                UserItem.objects.create(user=user, item=task.reward_item)
                messages.success(request, f'Получен предмет: {task.reward_item.icon} {task.reward_item.name}!')
            else:
                items = list(Item.objects.all())
                if items and random.random() < 0.4:
                    dropped = random.choice(items)
                    UserItem.objects.create(user=user, item=dropped)
                    messages.success(request, f'Случайная находка: {dropped.icon} {dropped.name}!')

        return redirect('hub')


class SendFriendRequestView(LoginRequiredMixin, View):

    def post(self, request, user_id):
        to_user = get_object_or_404(User, id=user_id)
        if to_user == request.user:
            messages.error(request, 'Нельзя добавить себя в друзья.')
            return redirect('friendslist')
        if Friend.objects.are_friends(request.user, to_user):
            messages.error(request, 'Вы уже друзья.')
            return redirect('friendslist')
        Friend.objects.add_friend(
            from_user=request.user,
            to_user=to_user,
            message="Привет! Хочу добавить тебя в друзья."
        )
        messages.success(request, 'Запрос на дружбу отправлен!')
        return redirect('friendslist')

class HandleFriendRequestView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, request_id, action):
        try:
            friend_request = FriendshipRequest.objects.get(id=request_id)
        except FriendshipRequest.DoesNotExist:
            messages.error(request, 'Запрос на дружбу не найден.')
            return redirect('add_friend_to_team')
        
        if request.user != friend_request.to_user:
            messages.error(request, 'У вас нет прав для этого действия.')
            return redirect('add_friend_to_team')
        
        if action == 'accept':
            friend_request.accept()
            messages.success(request, 'Дружба подтверждена!')
        elif action == 'reject':
            friend_request.reject()
            messages.success(request, 'Запрос отклонён.')
        
        return redirect('hub')

class AddFriendToTeam(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'base/add_friend_to_team.html'

    def dispatch(self, request, *args, **kwargs):

        self.team_id = kwargs.get("team_id")
        return super().dispatch(request, *args, **kwargs)



    def get(self, request, team_id):
        team = get_object_or_404(Team, id=team_id)
        
        friends = Friend.objects.friends(request.user)
        
        friends_not_in_team = [f for f in friends if f not in team.members.all()]

        return render(request, self.template_name, {
            "friends": friends_not_in_team,
            "team": team
        })

    def post(self, request, *args, **kwargs):
        team = get_object_or_404(Team, id=self.team_id)
        if team.creator != request.user:
            messages.error(request, 'Только создатель команды может добавлять участников.')
            return redirect('hub')
        friend_ids = request.POST.getlist("friends")
        friends = Friend.objects.friends(request.user)
        friend_pks = {f.pk for f in friends}
        for fid in friend_ids:
            if int(fid) in friend_pks and not team.members.filter(id=fid).exists():
                friend = get_object_or_404(User, id=fid)
                team.members.add(friend)
        return redirect('hub')


class InventoryView(LoginRequiredMixin, View):
    template_name = 'base/inventory.html'

    def get(self, request):
        inventory = UserItem.objects.filter(user=request.user).select_related('item').order_by('-acquired_at')
        return render(request, self.template_name, {'inventory': inventory})

    def post(self, request):
        user_item_id = request.POST.get('user_item_id')
        user_item = get_object_or_404(UserItem, id=user_item_id, user=request.user)
        user_item.equipped = not user_item.equipped
        user_item.save()
        return redirect('inventory')