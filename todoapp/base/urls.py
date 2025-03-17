from django.urls import path
from .views import TaskList,CustomLoginView,RegisterPage
from django.contrib.auth.views import LogoutView

urlpatterns = [
  path('login/',CustomLoginView.as_view(), name = "login"),
  path('logout/',LogoutView.as_view(next_page = 'login'), name = "logout"),
  path('register/',RegisterPage.as_view(), name = "register"),
  path('',TaskList.as_view(), name= 'tasks'),
]