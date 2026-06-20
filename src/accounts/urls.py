from django.urls import path
from .views import (
    register, verify_account, resent_code, reset_password, forgot_password,
    changePassword, login, logout, allusers, me, all_moderators, all_teachers, 
    update_profile, update_moderator, update_teacher
)

urlpatterns = [
    path('auth/register/', register),
    path('auth/login/', login),
    path('auth/verify-account/', verify_account),
    path('auth/resent-verification-code/', resent_code),
    path('auth/reset-password/', forgot_password),
    path('auth/new-password/', reset_password),
    path('auth/change-password/', changePassword),
    path('auth/logout/', logout),
    path('users/me/', me),
    
    # Teachers endpoints
    path('teachers/', all_teachers, name='all-teachers'),
    path('teachers/<uuid:id>/', update_teacher, name='update-teacher'),
    
    # Moderators endpoints
    path('moderators/', all_moderators, name='all-moderators'),
    path('moderators/<uuid:id>/', update_moderator, name='update-moderator'),
    
    path('users/profil-update/', update_profile)
]