from rest_framework.pagination import LimitOffsetPagination


class Pagination(LimitOffsetPagination):
    """自定义分页类
    
    使用 LimitOffsetPagination 支持客户端通过 offset 和 limit 参数控制分页
    - offset: 从第几条记录开始
    - limit: 获取多少条记录
    - 默认每次返回 20 条
    - 最大限制 200 条,即使客户端传入超过 200 也只返回 200 条
    
    使用示例:
        GET /api/resource/?offset=0&limit=20  # 获取前 20 条
        GET /api/resource/?offset=20&limit=50  # 从第 21 条开始,获取 50 条
        GET /api/resource/?offset=0&limit=300  # 获取 300 条,实际只返回 200 条
    """
    default_limit = 20  # 默认每次返回的记录数
    limit_query_param = 'limit'  # 客户端指定每次获取数量的参数名
    offset_query_param = 'offset'  # 客户端指定起始位置的参数名
    max_limit = 200  # 最大限制,防止客户端请求过多数据
