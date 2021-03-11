from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializer import CreateUserSerializer


class UserView(CreateAPIView):
    """用户注册"""
    serializer_class = CreateUserSerializer
