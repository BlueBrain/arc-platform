from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views as user_view
from arcv2_platform.config.config import config

urlpatterns = [
    path('users/sso_login/', user_view.sso_login, name='sso-login'),
    path('users/logout/', user_view.logout_user, name='logout'),
    path('users/', user_view.UserListView.as_view(), name='users'),
    path('users/new', user_view.UserCreate.as_view(), name='users-create'),
    path('users/edit/<int:pk>', user_view.UserUpdate.as_view(), name="users-edit"),
    path('users/<int:pk>', user_view.user_info, name="users-info"),
    path('tos/', user_view.terms_of_service, name='terms-of-service'),
    path('users/password', user_view.change_password, name='change-password'),
    path('users/profile', user_view.user_profile, name='profile'),
    path('users/unsubscribe/<user_token>', user_view.unsubscribe_notification, name='unsubscribe'),
]

if config.allow_password_login:
    urlpatterns.append(path('users/login/', user_view.login_user, name='login'))

urlpatterns = format_suffix_patterns(urlpatterns)
