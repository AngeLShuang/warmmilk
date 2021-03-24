from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from . import serializers
from . import constants
from .models import User
from milk.utils import error_code as ec


class UserView(CreateAPIView):
    """用户注册"""
    serializer_class = serializers.CreateUserSerializer


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
    serializer_class = serializers.UserDetailSerializer
    # 用户身份验证：是否是登录用户
    permission_classes = [IsAuthenticated]

    # 重写get_object(self)，返回用户详情模型对象
    def get_object(self):
        return self.request.user


class EmailView(UpdateAPIView):
    """更新邮箱"""
    serializer_class = serializers.EmailSerializer
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


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址增删改查
    """
    serializer_class = serializers.UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_delete=False)

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        # 判断⽤户地址数量是否超过上线
        count = request.user.addresses.count()
        # count = Address.objects.filter(user=request.user).count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response(ec.ADDRESS_LIMIT, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        # 用户地址列表数据
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            "user_id": user.id,
            "default_address_id": user.default_address,
            "limit": constants.USER_ADDRESS_COUNTS_LIMIT,
            "addresses": serializer.data
        })

    # DELETE /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        # 逻辑删除
        address = self.get_object()
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PUT /addresses/<pk>/status/
    def status(self, request, *args, **kwargs):
        # 设置默认地址
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PUT /addresses/<pk>/title/
    @action(detail=True, methods=['PUT'])
    def title(self, request, pk=None):
        # 修改标题
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
