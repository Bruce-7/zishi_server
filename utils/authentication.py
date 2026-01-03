"""
自定义认证类
允许无效或空 token 继续访问公共接口
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class OptionalJWTAuthentication(JWTAuthentication):
    """
    可选的 JWT 认证
    
    如果提供了有效的 token,则认证成功
    如果 token 无效或未提供,则返回 None,允许匿名访问
    """
    
    def authenticate(self, request):
        """
        尝试认证,失败时返回 None 而不是抛出异常
        """
        header = self.get_header(request)
        
        # 如果没有 Authorization 头,返回 None(匿名用户)
        if header is None:
            return None
        
        raw_token = self.get_raw_token(header)
        
        # 如果无法获取 token,返回 None
        if raw_token is None:
            return None
        
        try:
            # 验证 token
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, AuthenticationFailed):
            # token 无效时返回 None,允许继续访问公共接口
            # 如果接口需要认证,会在权限检查时被拦截
            return None
