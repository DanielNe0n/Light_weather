from django.contrib.auth.tokens import default_token_generator as token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm 
from django.utils.encoding import force_bytes  

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.http import Http404

from .utils import is_ajax, CityRequestMaster
from .forms import UserRegistationForm, LoginForm, EmailForm
from .models import City




def index(request):
    #Main page 
    CityMultiTool = CityRequestMaster

    if request.user.is_authenticated:
        #returning cities for js 
        if request.method == 'GET' and is_ajax(request):
            return CityMultiTool.returning_cities(request)

        elif request.method == 'GET':
            cities = City.objects.filter(user=request.user)
            return render(request, 'weather/main_page.html', {'cities': cities})
        #Add city from js
        elif request.method == 'POST' and is_ajax(request):
            return CityMultiTool.addding_city(request)
    
    
    else:    
        #returning cities for js 
        if request.method == 'GET' and is_ajax(request):
            return CityMultiTool.returning_cities(request)

        elif request.method == 'GET':
            cities = request.session.get('cities', [])
            return render(request, 'weather/main_page.html', {'cities': cities})

        elif request.method == 'POST' and is_ajax(request):
            return CityMultiTool.addding_city(request)


def user_register(request):
    if request.method == 'POST':
        form = UserRegistationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user_email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            print(form.cleaned_data)

            if not User.objects.filter(email=user_email).exists():
                new_user = User.objects.create_user(username=username, password=password,
                                                    email=user_email, is_active=False)

                messages.success(request, 'Check ' + user_email + ' to finish registration')
                
                token = token_generator.make_token(new_user)
                uidb = urlsafe_base64_encode(force_bytes(new_user.pk))
                link = f"http://{request.get_host()}/LightWeather/activation/{uidb}/{token}"

                send_mail(
                    'Light Weather - verification',
                    f'Click on the link to complete the registration - {link}',
                    settings.EMAIL_HOST_USER,
                    [user_email],
                    fail_silently=True,
                )
                return redirect('main_page')
            else:
                form.add_error('email', 'This email is already get') 
        else:
            print(form.errors)
    else:
        form = UserRegistationForm()

    return render(request, 'weather/register_page.html', {'form': form})
        
    


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            print(username, password)
            if user is not None:
                login(request, user)
                return redirect('main_page')
            form.add_error('__all__', 'form not valid')

        else:
            form.add_error('__all__', 'form not valid')
    else:
        form = LoginForm()

    return render(request, 'weather/login_page.html', {'form': form})


def email_activation(request, uidb, token):
    user_pk = urlsafe_base64_decode(uidb)

    try:
        user = User.objects.get(pk=user_pk)
        
        if user and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect("main_page")
        else:
            raise Http404('invalid activation link')

    except:
        raise Http404('invalid activation link')
    
    
@login_required()
def user_logout(request):
    logout(request)
    request.session.clear()
    return redirect('main_page')




def forgot_password(request):
    if request.method == 'GET':
        form = EmailForm
        return render(request, 'weather/forgot_password_page.html', {'form':form})
    else:
        form = EmailForm(request.POST)
        if form.is_valid():
            user = User.objects.filter(email=form.cleaned_data['email']).first()
            if user:

                token = token_generator.make_token(user)
                uidb = urlsafe_base64_encode(force_bytes(user.pk))

                link = f'http://{request.get_host()}/LightWeather/reset-password/{uidb}/{token}'

                send_mail(
                    'Light Weather - Reset password',
                    f"""
                        Click on the link to reset password - {link}
                        if this is not you then ignore this letter
                    """,
                    settings.EMAIL_HOST_USER,
                    [form.cleaned_data['email']],
                    fail_silently=True,
                    )
                messages.success(request, 'We send a reset link to your email')

            else:
                form.add_error('email', 'Account with this email not found')
        return render(request, 'weather/forgot_password_page.html', {'form':form})
        


def reset_password(request, uidb, token):
    user_pk = urlsafe_base64_decode(uidb)

    try:
        user = User.objects.get(pk=user_pk)
        if token_generator.check_token(user, token):
            form = SetPasswordForm(user=user)
            if request.method == 'POST':
                form = SetPasswordForm(user=user, data=request.POST)
                if form.is_valid():
                    form.save()
                    user.save()
                    return redirect('login_page')
            return render(request, 'weather/reset_password_page.html',
                                        {'form':form, 'uidb':uidb, 'token':token,}
                                        )
                                #uidb and token for form action="{% url '' %}"
        else:
            raise Http404('Invalid reset token')

    except Exception:
        raise Http404('Invalid reset token')
