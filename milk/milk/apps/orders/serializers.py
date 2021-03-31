from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers
from goods.models import SKU
from .models import OrderInfo, OrderGoods


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    # float 1.23 ==> 123 * 10 ^ -2 --> 1.299999999
    # Decimal 1.23 1 23
    # max_digits ⼀共多少位；decimal_places：⼩数点保留⼏位
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class CommitOrderSerializer(serializers.ModelSerializer):
    """提交订单"""

    class Meta:
        model = OrderInfo
        # order_id ：输出；address 和 pay_method : 输入
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True
            },
            'pay_method': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        """保存订单"""
        # 获取当前下单用户
        user = self.context['request'].user
        # ⽣成订单编号 20180704174607000000001
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # 获取校验之后的地址和支付方式
        address = validated_data.get('address')
        pay_method = validated_data.get('pay_method')
        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()
            try:
                # 保存订单基本信息 OrderInfo
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )
                # 从redis读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('carts')
                # {b'1':b'1', b'2':'2', b'3':b'3'}
                redis_cart = redis_conn.hgetall('cart_%s' % user.id)
                # [1, 3]
                selected = redis_conn.smembers('selected_%s' % user.id)
                # 将被勾选的购物车商品筛选出来
                carts = {}
                for sku_id in selected:
                    carts[int(sku_id)] = int(redis_cart[sku_id])
                # 先查询出所有的商品的sku_id，再去实时查询库存
                sku_ids = carts.keys()
                # 遍历购物车中被勾选的商品信息
                for sku_id in sku_ids:
                    # 查询sku信息
                    sku = SKU.objects.get(id=sku_id)
                    # 判断库存
                    sku_count = carts[sku.id]
                    if sku_count > sku.stock:
                        # 库存不足，回滚
                        transaction.savepoint_rollback(save_id)
                        raise serializers.ValidationError('库存不足')
                    # 减少库存，增加销量
                    sku.stock -= sku_count
                    sku.sales += sku_count
                    sku.save()
                    # 修改SPU销量
                    sku.goods.sales += sku_count
                    sku.goods.save()
                    # 保存订单商品信息 OrderGoods
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price,
                    )
                    # 保存商品订单中总价和总数量
                    order.total_count += sku_count
                    order.total_amount += (sku_count * sku.price)
                # 总价加入邮费
                order.total_amount += order.freight
                # 最后保存商品订单
                order.save()
            except Exception:
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError('库存不足')
            # 提交事务
            transaction.savepoint_commit(save_id)
            # 清除购物车中已结算的商品
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, *selected)
            pl.srem('selected_%s' % user.id, *selected)
            pl.execute()
            # 保存完成
            return order
