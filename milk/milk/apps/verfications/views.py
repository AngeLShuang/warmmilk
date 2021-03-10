from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from random import randint
# from django_redis import get_redis_connection

from milk.libs.yuntongxun.sms import CCP
from milk.utils import error_code as ec

from verfications import constants as ver_con


# Create your views here.
class SMSCodeView(APIView):
    """短信验证码"""

    def get(self, request, mobile):
        # 1.生成验证码
        sms_code = "%06d" % randint(0, 999999)
        # 2.创建Redis连接对象
        redis_conn = get_redis_connection('verify_codes')
        # 3.把验证码存储到redis数据库
        redis_conn.setex(ver_con.VERIFICATIONS_SMS % mobile, 300, sms_code)
        # 4.利用容联云通讯发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 5.响应
        return Response(ec.SUCCESS)
