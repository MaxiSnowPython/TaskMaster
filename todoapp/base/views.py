from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login

from .models import Task,Team


# Create your views here.
class CustomLoginView(LoginView):
    template_name = 'base/task_login.html'
    fields = '__all__'
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy('tasks')
    

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

class TeamList(LoginRequiredMixin,ListView):
    template_name = "base/task_list.html"
    model = Team
    context_object_name = "teams"
    def get_context_data(self, **kwargs):
        print("Залогиненный пользователь:", self.request.user)
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.model.objects.filter(creator=self.request.user)
        return context