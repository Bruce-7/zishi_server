import logging

from rest_framework import status
from rest_framework.response import Response as RestResponse

log = logging.getLogger(__name__)


class ResponseUtil(RestResponse):
    """自定义响应
    
    响应结构匹配客户端 Dart 的 ApiResponse 模型：
    {
        "code": 200,
        "message": "success",
        "data": {...},
    }
    """

    def __init__(self,
                 code=None,
                 message='success',
                 data=None,
                 http_status=None,
                 headers=None,
                 exception=False,
                 **kwargs):
        """
        初始化响应
        
        Args:
            code: API 状态码，默认使用 http_status
            message: 响应消息
            data: 响应数据
            http_status: HTTP 状态码
            headers: 响应头
            exception: 是否为异常响应
        """
        # 如果没有指定 code，使用 http_status
        if code is None:
            code = http_status if http_status is not None else status.HTTP_200_OK

        # 构建响应数据结构
        response_data = {
            'code': code,
            'message': message,
            'data': data,
        }

        # 添加其他自定义字段
        response_data.update(kwargs)

        log.debug(f'响应结果: {response_data}')
        super().__init__(data=response_data, status=http_status, headers=headers, exception=exception)
