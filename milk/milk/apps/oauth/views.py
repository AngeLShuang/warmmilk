from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from QQLoginTool.QQtool import OAuthQQ
import logging
from django.conf import settings

from milk.utils import error_code as ec

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
            # 使⽤code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)
            # 使⽤access_token向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.info(e)
            return Response(ec.QQ_SERVER_ERR, status=status.HTTP_503_SERVICE_UNAVAILABLE)
