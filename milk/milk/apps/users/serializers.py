from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from celery_tasks.email.tasks import send_verify_email
from .models import User, Address
from goods.models import SKU

import re
from django_redis import get_redis_connection


class CreateUserSerializer(serializers.ModelSerializer):
    """注册序列化器"""
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.CharField(label='同意协议', write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', 'token')
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):
        # 判断两次密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不⼀致')
        # 判断短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('⽆效的短信验证码')
        if data['sms_code'] != int(real_sms_code):
            raise serializers.ValidationError('短信验证码错误')
        return data

    def create(self, validated_data):
        """
        创建用户
        """
        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']
        user = User.objects.create(**validated_data)
        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])
        user.save()
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER  # 引用jwt中的叫jwt_payload_handler函数
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """用户详细信息序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')


class EmailSerializer(serializers.ModelSerializer):
    """
    邮箱序列化器
    """

    class Meta:
        model = User
        fields = ('id', 'email')
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        instance.email = validated_data['email']
        instance.save()
        send_verify_email.delay(instance.email, verify_url=instance.generate_email_verify_url())
        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    """
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """
        验证手机号
        """

        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def create(self, validated_data):
        user = self.context['request'].user

        validated_data['user'] = user
        return Address.objects.create(**validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    province = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address
        fields = ('title',)


class UserBrowseHistorySerializer(serializers.Serializer):
    """添加浏览记录的校验"""
    sku_id = serializers.IntegerField(label='商品SKU编号', min_value=1)

    def validate_sku_id(self, value):
        """校验sku_id"""
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku id 不存在')
        # 没有异常就返回校验之后的sku_id
        return value

    def create(self, validated_data):
        """存储浏览记录的行为"""
        # 获取用户信息
        user_id = self.context['request'].user.id
        # 读取验证后的sku_id
        sku_id = validated_data['sku_id']
        # 获取连接都redis对象
        redis_conn = get_redis_connection('history')
        pl = redis_conn.pipeline()
        # 去重
        pl.lrem('history_%s' % user_id, 0, sku_id)
        # 保存
        pl.lpush('history_%s' % user_id, sku_id)
        # 截取最前面的五个元素
        pl.ltrim('history_%s' % user_id, 0, 4)
        # 执行
        pl.execute()
        # 返回
        return validated_data
