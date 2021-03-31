from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework_jwt.views import ObtainJSONWebToken
from django_redis import get_redis_connection
from . import serializers
from . import constants
from .models import User
from goods.models import SKU
from goods.serializers import SKUSerializer
from milk.utils import error_code as ec
from apps.carts.utils import merge_cart_cookie_to_redis

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
        # 判断用户地址数量是否超过上线
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


class UserBrowseHistoryView(CreateAPIView):
    """用户浏览记录"""
    # 验证是否登录
    permission_classes = [IsAuthenticated]
    # 指定序列化器
    serializer_class = serializers.UserBrowseHistorySerializer

    def get(self, request):
        """查询用户浏览记录"""
        # 获取user_id
        user_id = request.user.id
        # 获取连接到redis对象
        redis_conn = get_redis_connection('history')
        # 查询出redis中用户存储的浏览记录
        sku_ids = redis_conn.lrange('history_%s' % user_id, 0, -1)
        # 查询sku列表数据
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)
        # 调用序列化器实现输出：序列化器序列化操作
        serializer = SKUSerializer(sku_list, many=True)
        return Response(serializer.data)


class UserAuthorizeView(ObtainJSONWebToken):
    """
    用户认证
    """

    def post(self, request, *args, **kwargs):
        # 调用父类的⽅法，获取drf jwt扩展默认的认证用户处理结果
        response = super().post(request, *args, **kwargs)
        # 仿照drf jwt扩展对于用户登录的认证⽅式，判断用户是否认证登录成功
        # 如果用户登录认证成功，则合并购物车
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            response = merge_cart_cookie_to_redis(request, response, user)
        return response
