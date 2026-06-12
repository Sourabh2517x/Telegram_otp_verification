from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path("",views.index,name="index"),
    path("register/",views.register,name="register"),  
    path("login/",views.login,name="login"), 
    path('logout/', LogoutView.as_view(template_name='users/index.html'), name="logout"),
    path('webhook/', views.telegram_webhook,name='telegram_webhook'),
    path('verify/<str:phone>/', views.verify_otp, name='verify_otp'),
    path('resend-otp/<str:phone>/', views.resend_otp, name='resend_otp'), 
]