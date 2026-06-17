from django.urls import path
from .views import register, verify_account, resent_code, reset_password, newPassword,changePassword, login, logout, allusers, me, all_moderators, all_teachers, update_profile

urlpatterns = [
    path('auth/register/', register),
    path('auth/login/', login),
    path('auth/verify-account/', verify_account),
    path('auth/resent-verification-code/', resent_code),
    path('auth/reset-password/', reset_password),
    path('auth/new-password/', newPassword),
    path('auth/change-password/', changePassword),
    path('auth/logout/', logout),
    path('users/all/', allusers),
    path('users/me/', me),
    path('users/teachers/', all_teachers, name='all-teachers'),
    path('users/moderators/', all_moderators, name='all-moderators'),
    path('users/profil-update/', update_profile)
]