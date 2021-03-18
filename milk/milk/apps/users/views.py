from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializer import CreateUserSerializer, UserDetailSerializer, EmailSerializer
from .models import User
from milk.utils import error_code as ec

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


class UserDetailView(RetrieveAPIView):
    """提供用户详细信息"""
    serializer_class = UserDetailSerializer
    # 用户身份验证：是否是登录用户
    permission_classes = [IsAuthenticated]

    # 重写get_object(self)，返回用户详情模型对象
    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """更新邮箱"""
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    """验证邮箱"""

    def get(self, request):
        # 获取token参数
        token = request.query_params.get('token')
        if not token:
            return Response(ec.EMAIL_TOKEN_LOSE, status=status.HTTP_400_BAD_REQUEST)
        # 验证token参数：提取user
        user = User.check_verify_email_token(token)
        if not user:
            return Response(ec.EMAIL_TOKEN_INVALID, status=status.HTTP_400_BAD_REQUEST)
        # 修改用户的email_active的值为True，完成验证
        user.email_active = True
        user.save()
        return Response(ec.SUCCESS)
