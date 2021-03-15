# 成功
SUCCESS = {
    "errcode": 0,
    "message": "success",
    "data": {}
}

# 参数错误
PARAMETER_ERR = {
    "errcode": 1,
    "message": "Parameter error"
}

# 参数错误
SERVER_ERR = {
    "errcode": 2,
    "message": "服务器内部错误"
}

"""注册部分error 范围2000~2999"""
FREQUENT_CALLS_ERR = {
    "errcode": 2000,
    "message": "Frequent calls"
}

QQ_SERVER_ERR = {
    "errcode": 2001,
    "message": "QQ服务异常"
}

QQ_CODE_ERR = {
    "errcode": 2002,
    "message": "缺少code"
}
