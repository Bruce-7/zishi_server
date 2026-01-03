"""
自定义异常处理器
统一所有错误响应格式,包括认证、权限、404等错误
"""
from rest_framework.views import exception_handler

from utils.response import ResponseUtil


def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    
    将所有异常响应统一为自定义格式:
    {
        "code": 401,
        "message": "身份认证信息未提供。",
        "data": null
    }
    """
    # 调用 DRF 默认的异常处理器
    response = exception_handler(exc, context)

    if response is not None:
        # 获取错误信息
        if isinstance(response.data, dict):
            # 如果是字典,尝试获取 detail 字段
            error_message = response.data.get('detail', str(response.data))
        elif isinstance(response.data, list):
            # 如果是列表,取第一个元素
            error_message = str(response.data[0]) if response.data else '请求失败'
        else:
            error_message = str(response.data)

        # 使用自定义响应格式
        return ResponseUtil(
            code=response.status_code,
            message=error_message,
            data=None,
            http_status=response.status_code,
            exception=True
        )

    return response
