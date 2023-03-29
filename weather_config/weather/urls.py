from django.urls import path
from weather import views


urlpatterns = [
    path('', views.index, name='main_page'),

    path('register/', views.user_register, name='register_page'), 
    path('login/', views.user_login, name='login_page'), 
    path('logout/', views.user_logout, name='logout_page'), 
    path('activation/<uidb>/<token>/', views.email_activation, name='activation_page'), 
    path('forgot-password/', views.forgot_password, name='forgot_password_page'), 
    path('reset-password/<uidb>/<token>/', views.reset_password, name='reset_password_page'),  
]