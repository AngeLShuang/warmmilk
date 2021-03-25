from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from QQLoginTool.QQtool import OAuthQQ
import logging
from django.conf import settings

from milk.utils import error_code as ec
from .models import OAuthQQUser
from .utils import generate_save_user_token
from .serializers import QQAuthUserSerializer

logger = logging.getLogger('django')


class QQAuthURLView(APIView):
    """提供QQ登录网址"""

    def get(self, request):
        # next表示从哪个界面进⼊到的登录界面，将来登录成功后，就⾃动回到那个界面
        next = request.query_params.get('next', '/')
        # 获取QQ登录界面网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()
        return Response({'login_url': login_url})


class QQAuthUserView(APIView):
    """OAuth2.0认证:处理扫码回调操作"""

    def get(self, request):

        # 提取code请求参数
        code = request.query_params.get('code')
        if not code:
            return Response(ec.QQ_CODE_ERR, status=status.HTTP_400_BAD_REQUEST)
        # 创建OAuthQQ对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 使用code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)
            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.info(e)
            return Response(ec.QQ_SERVER_ERR, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 使用openid查询该QQ用户是否在商城中绑定过用户
        try:
            oauthqquser_model = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果openid没绑定商城用户，创建用户并绑定到openid
            # 为了能够在后续的绑定用户操作中前端可以使用openid，在这⾥将openid签名后响应给前端
            access_token_openid = generate_save_user_token(openid)
            return Response({'access_token': access_token_openid})
        else:
            # 如果openid已绑定商城用户，直接生成JWT token，并返回
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            # 获取oauth_user关联的user
            user = oauthqquser_model.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Response({'token': token, 'user_id': user.id, 'username': user.username})

    def post(self, request):
        """使用open_id绑定一杯热牛奶用户"""
        # 获取序列化器对象
        serializer = QQAuthUserSerializer(data=request.data)
        # 开启校验
        serializer.is_valid(raise_exception=True)
        # 保存校验结果，并接收
        user = serializer.save()
        # 生成JWT token，并响应
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return Response({'token': token, 'username': user.username, 'user_id': user.id})
