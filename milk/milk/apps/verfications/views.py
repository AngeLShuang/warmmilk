from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from random import randint
from django_redis import get_redis_connection

from milk.utils import error_code as ec
from celery_tasks.sms import tasks as ts

from verfications import constants as ver_con


# Create your views here.
class SMSCodeView(APIView):
    """短信验证码"""

    def get(self, request, mobile):
        # 创建Redis连接对象
        redis_conn = get_redis_connection('verify_codes')
        # 先从redis获取发送标记
        send_flag = redis_conn.get(ver_con.VERIFICATIONS_SMS_FLAG % mobile)
        if send_flag:
            return Response(ec.FREQUENT_CALLS_ERR, status=status.HTTP_400_BAD_REQUEST)

        # 生成验证码
        sms_code = "%06d" % randint(0, 999999)

        # 创建redis管道：把多次redis操作装入管道中，一次性执行，减少redis连接操作，减轻压力
        pl = redis_conn.pipeline()
        # 把验证码存储到redis数据库
        pl.setex(ver_con.VERIFICATIONS_SMS % mobile, ver_con.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 存储一个标记，表示此手机号已发送过短信 标记有效期为60秒
        pl.setex(ver_con.VERIFICATIONS_SMS_FLAG % mobile, ver_con.SEND_SMS_CODE_INTERVAL, 1)
        # 执行管道
        pl.execute()

        # 利用容联云通讯发送短信验证码 把任务往队列里添加，worker自动处理
        ts.send_sms_code.delay(mobile, sms_code)
        # 响应
        return Response(ec.SUCCESS)
