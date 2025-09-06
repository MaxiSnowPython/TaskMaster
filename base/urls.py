from django.urls import path, include
from .views import *
from django.contrib.auth.views import LogoutView
from rest_framework import routers
from django.conf.urls.static import static
router = routers.DefaultRouter()
router.register(r'teams',TeamApi)
router.register(r'tasks',TaskApi)
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
  path('friendslist/', FriendList.as_view(), name='friendslist'),
  path('confirm_task/<int:pk>/',TaskComplete.as_view(), name='confirm_task'),
  path('api-auth/',include('rest_framework.urls',namespace='rest_framework')),
  path('api', include(router.urls)),
  path('friend/handle/<int:request_id>/<str:action>/', HandleFriendRequestView.as_view(), name='handle_friend_request'),
  path("team/<int:team_id>/add_friends/", AddFriendToTeam.as_view(), name="add_friend_to_team"),
  path('edit_profile',EditProfile.as_view(),name= "edit_profile"),
  


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)