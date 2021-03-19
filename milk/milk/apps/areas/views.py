from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from .models import Area
from . import serializers


class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """省市区视图集：提供单个对象和列表数据"""
    # 区域信息不分页
    pagination_class = None

    # 指定查询集：数据来源
    def get_queryset(self):

        """根据action选择返回的查询集"""
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    # 指定省级数据和子集数据序列化器
    def get_serializer_class(self):

        """根据action选择不同的序列化器"""
        if self.action == 'list':
            return serializers.AreaSerializer
        else:
            return serializers.SubAreaSerializer
