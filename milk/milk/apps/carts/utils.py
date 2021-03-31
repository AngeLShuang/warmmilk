import pickle
import base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    """
    登录后合并cookie中的购物车数据到redis中
    :param request: 本次请求对象，获取cookie中的数据
    :param response: 本次响应对象，清除cookie中的数据
    :param user: 登录用户信息，获取user_id
    :return: response
    """
    # 获取cookie中的购物车数据
    cookie_cart_str = request.COOKIES.get('cart')
    # cookie中没有数据就响应结果
    if not cookie_cart_str:
        return response
    # 将cookie中的购物车字符串转成字典
    cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart_str.encode()))

    # 获取redis中的购物车数据
    redis_conn = get_redis_connection('cart')
    redis_cart_dict = redis_conn.hgetall('cart_%s' % user.id)
    redis_cart_selected = redis_conn.smembers('selected_%s' % user.id)
    # redis_cart_dict = {
    # b'sku_id':b'count',
    # b'sku_id':b'count'
    # }
    new_redis_cart_dict = {}
    for sku_id, count in redis_cart_dict.items():
        new_redis_cart_dict[int(sku_id)] = int(count)

    # 遍历cookie_cart_dict，将sku_id和count覆盖到new_redis_cart_dict
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_redis_cart_dict[sku_id] = cookie_dict['count']
        if cookie_dict['selected']:
            redis_cart_selected.add(sku_id)

    # 将redis_cart_dict写入到数据库
    pl = redis_conn.pipeline()
    pl.hmset('cart_%s' % user.id, new_redis_cart_dict)
    pl.sadd('selected_%s' % user.id, *redis_cart_selected)
    pl.execute()
    # 清除cookie
    response.delete_cookie('cart')
    # 响应结果
    return response
