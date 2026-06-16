from django.urls import path
from .views import register, verify_account, resent_code, reset_password, newPassword,changePassword, login, logout, allusers, me

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('verify-account/', verify_account),
    path('resent-verification-code/', resent_code),
    path('reset-password/', reset_password),
    path('new-password/', newPassword),
    path('change-password/', changePassword),
    path('logout/', logout),
    path('all/', allusers),
    path('me/', me)
]