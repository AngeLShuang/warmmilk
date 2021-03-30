from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_redis import get_redis_connection
import pickle
import base64

from . import serializers
from goods.models import SKU


class CartView(APIView):
    """操作购物车：增删改查"""

    def perform_authentication(self, request):
        """
        重写子类的用户验证方法，不在进入视图前就检查JWT
        保证用户未登录也可以进入下面的请求方法
        """
        pass

    def post(self, request):
        """添加购物车"""
        # 创建序列化器对象并验证字段
        serializer = serializers.CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 创建响应对象
        response = Response(serializer.data, status=status.HTTP_201_CREATED)

        # 获取user,用于判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None
        # 判断用户是否登录
        if user is not None and user.is_authenticated:
            # 用户已登录，redis操作购物车
            """
            hash:{"sku_id_1":2，"sku_id_2":6}
            set:[sku_id_1]
            """
            redis_conn = get_redis_connection('cart')
            # 创建管道操作redis,提升访问数据库效率
            pl = redis_conn.pipeline()
            # 新增购物车数据
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 新增选中的状态
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            # 执行管道
            pl.execute()
        else:
            # 用户未登录，cookie操作购物车
            cart_str = request.COOKIES.get('cart')
            if cart_str:  # 用户操作过cookie购物车
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:  # 用户从没有操作过cookie购物车
                cart_dict = {}
            # 判断要加入购物车的商品是否已经在购物车中
            # 如有相同商品，累加求和，反之，直接赋值
            if sku_id in cart_dict:
                # 累加求和
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('cart', cookie_cart_str)
        return response

    def get(self, request):
        """读取购物车"""
        try:
            user = request.user
        except Exception:
            user = None
            # 判断用户是否登录
        if user is not None and user.is_authenticated:
            # 创建连接到redis对象
            redis_conn = get_redis_connection('cart')
            # 获取redis中的购物车数据
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            # 获取redis中的选中状态
            redis_selected = redis_conn.smembers('selected_%s' % user.id)
            # 将redis中的两个数据统⼀格式，跟cookie中的格式⼀致，⽅便统⼀查询
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }
        else:
            # 用户未登录，cookie操作购物车
            cart_str = request.COOKIES.get('cart')
            if cart_str:  # 用户操作过cookie购物车
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:  # 用户从没有操作过cookie购物车
                cart_dict = {}
        # 查询购物车数据
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        # 补充count和selected字段
        for sku in skus:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']
        # 创建序列化器序列化商品数据
        serializer = serializers.CartSKUSerializer(skus, many=True)
        # 响应结果
        return Response(serializer.data)

    def put(self, request):
        """修改购物车"""
        # 创建序列化器对象并验证字段
        serializer = serializers.CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 获取校验后的参数
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        # 获取user,用于判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None
        # 判断用户是否登录
        if user is not None and user.is_authenticated:
            # 用户已登录，操作redis购物车
            # 创建连接到redis对象
            redis_conn = get_redis_connection('cart')
            # 管道
            pl = redis_conn.pipeline()
            # 因为接口设计为幂等的，直接覆盖
            pl.hset('cart_%s' % user.id, sku_id, count)
            # 是否选中
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()
            # 响应
            return Response(serializer.data)
        else:
            # 用户未登录，cookie操作购物车
            cart_str = request.COOKIES.get('cart')
            if cart_str:  # 用户操作过cookie购物车
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:  # 用户从没有操作过cookie购物车
                cart_dict = {}
            # 因为接口设计为幂等的，直接覆盖
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 创建响应对象
            response = Response(serializer.data)
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('cart', cookie_cart_str)
            return response

    def delete(self, request):
        """删除购物车"""
        # 创建序列化器对象并验证字段
        serializer = serializers.CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 获取校验后的参数
        sku_id = serializer.validated_data.get('sku_id')

        # 获取user,用于判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None
        # 判断用户是否登录
        if user is not None and user.is_authenticated:
            # 用户已登录，操作redis购物车
            # 创建连接到redis对象
            redis_conn = get_redis_connection('cart')
            # 管道
            pl = redis_conn.pipeline()
            # 删除键，就等价于删除了整条记录
            pl.hdel('cart_%s' % user.id, sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
            # 删除结束后，没有响应的数据，只需要响应状态码即可
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 用户未登录，cookie操作购物车
            cart_str = request.COOKIES.get('cart')
            if cart_str:  # 用户操作过cookie购物车
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:  # 用户从没有操作过cookie购物车
                cart_dict = {}
            # 创建响应对象
            response = Response(status=status.HTTP_204_NO_CONTENT)
            if sku_id in cart_dict:
                del cart_dict[sku_id]
                # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串

            if len(cart_dict.keys()):
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 响应结果并将购物车数据写入到cookie
                response.set_cookie('cart', cookie_cart_str)
            else:
                response.delete_cookie('cart')
            return response
