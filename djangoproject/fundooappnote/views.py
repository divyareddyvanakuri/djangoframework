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
from .serializers import (RegisterSerializer, LoginSerializer, SetPasswordSerializer,
                          UserSerializer, ForgotPasswordSerializer,)
from django.contrib.auth import authenticate,logout
from django.contrib.auth.models import User, auth, UserManager
from .models import Note
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


# Create your views here.
@csrf_protect   
def user_register(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmpassword = request.POST['confirmpassword']
        if password == confirmpassword:
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
                return HttpResponse("After Successful registeration,please active your accout througth mailed link")
        else:
            context['error']="password and confirmpassword fields are not equal...!!"
            return render(request,'register.html',context)    
    else:
        return render(request,'register.html')

