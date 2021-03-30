from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from .serializers import SKUSerializer
from .models import SKU


class SKUListView(ListAPIView):
    """商品列表"""
    # 指定查询集:因为要展示的商品列表需要明确的指定分类，所以重写获取查询集方法
    # queryset = SKU.objects.all()
    # 指定序列化器
    serializer_class = SKUSerializer
    # 指定过滤器:需要指定排序后端
    filter_backends = (OrderingFilter,)
    # 指定排序字段：搭配filter_backends使用的
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        """如果在当前视图中没有定义get/post方法，那么就没法定义一个参数用来接收正则组提取出来的url路径参数，可以利用视图对象的args或kwargs"""
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id, is_launched=True)
