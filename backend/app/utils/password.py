"""
密码验证工具模块
符合等保 2.0 密码策略要求
"""
import re
from typing import List, Tuple
from app.core.config import settings


class PasswordValidator:
    """
    密码验证器
    符合等保 2.0 密码强度要求
    """
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, List[str]]:
        """
        验证密码是否符合策略要求
        
        Args:
            password: 待验证的密码
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查最小长度
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            errors.append(f"密码长度至少需要 {settings.PASSWORD_MIN_LENGTH} 个字符")
        
        # 检查大写字母
        if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("密码必须包含至少一个大写字母")
        
        # 检查小写字母
        if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("密码必须包含至少一个小写字母")
        
        # 检查数字
        if settings.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append("密码必须包含至少一个数字")
        
        # 检查特殊字符
        if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            errors.append("密码必须包含至少一个特殊字符")
        
        # 检查常见弱密码
        common_passwords = [
            "12345678", "password", "admin123", "qwerty123",
            "123456789", "Password1", "Admin123", "123456",
        ]
        if password.lower() in [p.lower() for p in common_passwords]:
            errors.append("密码不能使用常见的弱密码")
        
        # 检查是否包含用户名（需要上下文，这里只是示例）
        # 如果提供了用户名，可以检查密码中是否包含用户名
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    @staticmethod
    def get_password_requirements() -> str:
        """
        获取密码要求说明
        
        Returns:
            str: 密码要求文本
        """
        requirements = [f"至少 {settings.PASSWORD_MIN_LENGTH} 个字符"]
        
        if settings.PASSWORD_REQUIRE_UPPERCASE:
            requirements.append("包含大写字母")
        if settings.PASSWORD_REQUIRE_LOWERCASE:
            requirements.append("包含小写字母")
        if settings.PASSWORD_REQUIRE_DIGIT:
            requirements.append("包含数字")
        if settings.PASSWORD_REQUIRE_SPECIAL:
            requirements.append("包含特殊字符")
        
        return "、".join(requirements)
