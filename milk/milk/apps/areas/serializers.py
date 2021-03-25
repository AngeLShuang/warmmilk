from rest_framework import serializers

from .models import Area


class AreaSerializer(serializers.ModelSerializer):
    """返回省级数据的序列化器"""

    class Meta:
        model = Area
        fields = ('id', 'name')


class SubAreaSerializer(serializers.ModelSerializer):
    """返回子集数据的序列化器"""
    # 子集样式跟AreaSerializer⼀样
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')
