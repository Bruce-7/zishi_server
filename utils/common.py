class CommonUtil:
    @staticmethod
    def string_convert_bool(value):
        """将字符串转换为布尔值"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)

