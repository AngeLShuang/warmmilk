from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializer import CreateUserSerializer
from .models import User


class UserView(CreateAPIView):
    """用户注册"""
    serializer_class = CreateUserSerializer


class UsernameCountView(APIView):
    """用户户名数量"""

    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


class MobileCountView(APIView):
    """手机号数量"""

    def get(self, request, mobile):
        """获取指定手机号数量"""
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)
