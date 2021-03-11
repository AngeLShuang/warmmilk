from django_redis.pool import ConnectionFactory


class DecodeConnectionFactory(ConnectionFactory):
    """解决python3 django-redis 默认输出bytes类型"""

    def get_connection(self, params):
        params['decode_responses'] = True
        return super().get_connection(params)
