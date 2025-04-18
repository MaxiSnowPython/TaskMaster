from django.urls import path
from .views import TeamList,CustomLoginView,RegisterPage,HubView,CreateTeam,TaskDelete,TaskCreate,TeamMemberDelete,AddFriendToTeamView
from django.contrib.auth.views import LogoutView

urlpatterns = [
  path('login/',CustomLoginView.as_view(), name = "login"),
  path('logout/',LogoutView.as_view(next_page = 'login'), name = 'logout'),
  path('register/',RegisterPage.as_view(), name = 'register'),
  path('team/<int:team_id>/',TeamList.as_view(), name= 'team'),
  path('hub/',HubView.as_view(),name='hub'),
  path('create_team',CreateTeam.as_view(), name = 'create_team'),
  path('delete/<int:pk>/', TaskDelete.as_view(), name='delete_task'),
  path('team/<int:pk>/create_task/',TaskCreate.as_view(),name = "task_create"),
  path('team/<int:team_id>/remove_member/<int:user_id>/',TeamMemberDelete.as_view(),name="deletemember"),
  path('add_friend_to_team/', AddFriendToTeamView.as_view(), name='add_friend_to_team'),

]