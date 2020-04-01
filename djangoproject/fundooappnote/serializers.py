from rest_framework import serializers
from .models import Person
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['username', 'password']




