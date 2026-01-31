"""
应用配置管理
符合等保 2.0 规范
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    应用配置
    符合等保 2.0 安全配置要求
    """
    
    # 应用基础配置
    APP_NAME: str = "保卫核心业务智能体"
    APP_ENV: str = "development"  # development/production
    DEBUG: bool = True
    # SECRET_KEY 应从环境变量读取，生产环境必须使用强密钥
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # 数据库配置
    DATABASE_URL: Optional[str] = None
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "user"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "military_guard"
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 524288000  # 500MB
    ALLOWED_EXTENSIONS: str = ".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"  # 允许的文件扩展名
    
    # JWT配置
    # JWT_SECRET_KEY 应从环境变量读取，生产环境必须使用强密钥
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7  # 刷新Token过期天数
    
    # 密码策略配置（等保 2.0 要求）
    PASSWORD_MIN_LENGTH: int = 8  # 最小长度
    PASSWORD_REQUIRE_UPPERCASE: bool = True  # 需要大写字母
    PASSWORD_REQUIRE_LOWERCASE: bool = True  # 需要小写字母
    PASSWORD_REQUIRE_DIGIT: bool = True  # 需要数字
    PASSWORD_REQUIRE_SPECIAL: bool = True  # 需要特殊字符
    PASSWORD_MAX_AGE_DAYS: int = 90  # 密码最大有效期（天）
    
    # 安全配置（等保 2.0 要求）
    ENABLE_HTTPS: bool = False  # 生产环境必须启用 HTTPS
    SESSION_TIMEOUT_MINUTES: int = 30  # 会话超时时间
    MAX_LOGIN_ATTEMPTS: int = 5  # 最大登录尝试次数
    LOGIN_LOCKOUT_MINUTES: int = 30  # 登录锁定时间（分钟）
    
    # 速率限制配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_CALLS: int = 100  # 允许的请求次数
    RATE_LIMIT_PERIOD: int = 60  # 时间窗口（秒）
    
    # 审计日志配置
    AUDIT_LOG_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 365  # 审计日志保留天数
    
    # CORS配置（生产环境需要严格配置）
    # 通过 nginx 代理时，前端和后端在同一域名下，不会有跨域问题
    # 但为了兼容直接访问后端的情况，保留 CORS 配置
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost,http://127.0.0.1,http://localhost:5173,http://127.0.0.1:5173")
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # OCR配置
    TESSERACT_LANG: str = "chi_sim+eng"
    
    # AI 模型配置（通义千问）
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    QWEN_MODEL: str = "qwen-plus"  # 可选: qwen-turbo, qwen-plus, qwen-max
    
    @property
    def cors_origins_list(self) -> list:
        """获取 CORS 源列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def database_url(self) -> str:
        """获取数据库连接URL"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
