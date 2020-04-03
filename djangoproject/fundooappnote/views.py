from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django_short_url.views import get_surl
from django_short_url.models import ShortURL
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from djangoproject.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import (RegisterSerializer, LoginSerializer, SetPasswordSerializer,ForgotPasswordSerializer,)
from django.contrib.auth import authenticate,logout
from django.contrib.auth.models import User, auth, UserManager
from django.urls import reverse
from .token_activation import tokenActivation,tokendecode
from django.views.decorators.csrf import csrf_exempt,csrf_protect
import jwt
from rest_framework import status
from django.utils.datastructures import MultiValueDictKeyError
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core import serializers
CACHE_TTL = getattr(settings,"CACHE_TTL",DEFAULT_TIMEOUT)
from django.views.decorators.cache import cache_page
from djangoproject.redis import Redis
obj_redis = Redis()
# Create your views here.
@csrf_protect   
def user_register(request):
    context = {}
    try:
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            confirmpassword = request.POST['confirmpassword']
    
        if User.objects.filter(username=username).exists():
                print("username taken")
                context['error']="username was already in use...!!"
                return render(request,'register.html',context) 
        elif User.objects.filter(email=email).exists():
            print("email id taken")
            context['error']="email was already in use...!!"
            return render(request,'register.html',context)
        else:
            user = User.objects.create_user(username=username, email=email, password=password) 
            user.is_active = False
            user.save()
            token = tokenActivation(username)
            current_site = get_current_site(request)
            domain_name = current_site.domain
            mail_subject = "Activate your account"
            msg1 = render_to_string('email_validation.html', {
                'username': username, 'domain': domain_name, 'surl':token})
            send_mail(mail_subject, msg1, EMAIL_HOST_USER,[email], fail_silently=False,)
            print(msg1)
            return HttpResponse("After Successful registeration,please active your accout througth mailed link")
    except:
        return render(request,'register.html')
    else:
        return render(request,'register.html')

@csrf_protect
def activate(request, surl):
    print("surl:",surl)
    username = tokendecode(surl)
    try:    
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    if user is not None:
        user.is_active = True
        user.save()
        return HttpResponseRedirect(reverse('s_reg', ))
    return HttpResponse("user not existed")

def successful_register(request):
    context = {}
    context['user']=request.user
    return render(request,"success.html", context) 


@csrf_protect
def user_login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                # auth.login(request,user)
                surl = tokenActivation(username)
                print("token",surl)
                obj_redis.set(username,surl)
                print(obj_redis.get(username))
                msg2 = render_to_string('logout.html',{'username': username,'surl':surl})
                return HttpResponse(msg2)
        else:
            context['error']="provide valide credentials...!!"
            return render(request,'login.html',context)    

    return render(request,'login.html')

def logout(request,surl):
    auth.logout(request)
    return HttpResponseRedirect(reverse('login'))

def forgot_password(request):
    context = {}
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            context['error']="provide valide credentials...!!"
            return render(request,'email.html',context)
        if user.is_active: 
            username = user.username
            token = tokenActivation(username)
            current_site = get_current_site(request)
            domain_name = current_site.domain
            surl = get_surl(str(token))
            z = surl.split("/")
            mail_subject = "Activate your account"
            msg1 = render_to_string('password_activation.html', {
                'username': username, 'domain': domain_name, 'surl': z[2]})
            send_mail(mail_subject, msg1, EMAIL_HOST_USER,[email], fail_silently=False,)
            print(msg1)
            return HttpResponse("setpassword through mailed link")
        else:
            context['error']="please activate before reset password...!!"
            return render(request,'email.html',context)
    else:
        return render(request,'email.html')

#password activation through jwt
@csrf_protect
def passwordactivation(request,surl):
    print("surl :", surl)
    username = tokendecode(surl)
    if request.method == 'POST':
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        user.set_password(password)
        user.save()
        return HttpResponseRedirect(reverse('s_reg', ))
    return render(request,'forgotpassword.html')


