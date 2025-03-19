from django.urls import path
from .views import TeamList,CustomLoginView,RegisterPage,HubView
from django.contrib.auth.views import LogoutView

urlpatterns = [
  path('login/',CustomLoginView.as_view(), name = "login"),
  path('logout/',LogoutView.as_view(next_page = 'login'), name = 'logout'),
  path('register/',RegisterPage.as_view(), name = 'register'),
  path('team/<int:team_id>/',TeamList.as_view(), name= 'team'),
  path('hub/',HubView.as_view(),name='hub')
]