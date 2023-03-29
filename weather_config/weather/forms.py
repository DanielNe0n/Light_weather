from django import forms
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from captcha.fields import CaptchaField, CaptchaTextInput


class UserRegistationForm(UserCreationForm):
    email = forms.EmailField(required=True, )
    captcha = CaptchaField(widget=CaptchaTextInput(),)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'captcha')
        
        

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, required=True,)
    password = forms.CharField(max_length=30, required=True,
                               widget=forms.PasswordInput())
                               
    captcha = CaptchaField(widget=CaptchaTextInput())


class EmailForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(widget=CaptchaTextInput())