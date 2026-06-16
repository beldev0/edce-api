from django.urls import path
from .views import register, verify_account, resent_code

urlpatterns = [
    path('register/', register),
    path('verify-account/', verify_account),
    path('resent-verification-code/', resent_code)
]