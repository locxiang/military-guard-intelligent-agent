"""
数据加密工具模块
符合等保 2.0 数据安全要求
"""
import base64
import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from app.core.config import settings


class EncryptionUtil:
    """
    加密工具类
    用于敏感数据的加密和解密
    """
    
    _fernet: Optional[Fernet] = None
    
    @classmethod
    def _get_fernet(cls) -> Fernet:
        """
        获取 Fernet 加密实例（单例模式）
        
        Returns:
            Fernet: 加密实例
        """
        if cls._fernet is None:
            # 使用 SECRET_KEY 派生加密密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'military_guard_salt',  # 生产环境应从配置读取
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(
                kdf.derive(settings.SECRET_KEY.encode())
            )
            cls._fernet = Fernet(key)
        
        return cls._fernet
    
    @classmethod
    def encrypt(cls, data: str) -> str:
        """
        加密字符串数据
        
        Args:
            data: 明文数据
            
        Returns:
            str: 加密后的数据（Base64编码）
        """
        if not data:
            return ""
        
        fernet = cls._get_fernet()
        encrypted = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    @classmethod
    def decrypt(cls, encrypted_data: str) -> str:
        """
        解密字符串数据
        
        Args:
            encrypted_data: 加密后的数据（Base64编码）
            
        Returns:
            str: 解密后的明文数据
            
        Raises:
            ValueError: 解密失败
        """
        if not encrypted_data:
            return ""
        
        try:
            fernet = cls._get_fernet()
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")
    
    @classmethod
    def hash_data(cls, data: str, algorithm: str = "sha256") -> str:
        """
        对数据进行哈希（不可逆）
        
        Args:
            data: 原始数据
            algorithm: 哈希算法 (md5, sha1, sha256, sha512)
            
        Returns:
            str: 哈希值
        """
        hash_func = getattr(hashlib, algorithm, hashlib.sha256)
        return hash_func(data.encode()).hexdigest()
    
    @classmethod
    def mask_sensitive_data(cls, data: str, visible_chars: int = 4) -> str:
        """
        掩码敏感数据（用于日志记录）
        
        Args:
            data: 原始数据
            visible_chars: 保留可见字符数
            
        Returns:
            str: 掩码后的数据
        """
        if not data or len(data) <= visible_chars:
            return "*" * len(data) if data else ""
        
        visible = data[:visible_chars]
        masked = "*" * (len(data) - visible_chars)
        return visible + masked


class DataSanitizer:
    """
    数据清理工具类
    用于防止 XSS 和注入攻击
    """
    
    # HTML 转义映射
    HTML_ESCAPE_MAP = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;",
    }
    
    @classmethod
    def escape_html(cls, text: str) -> str:
        """
        HTML 转义，防止 XSS 攻击
        
        Args:
            text: 原始文本
            
        Returns:
            str: 转义后的文本
        """
        if not text:
            return ""
        
        result = text
        for char, escaped in cls.HTML_ESCAPE_MAP.items():
            result = result.replace(char, escaped)
        
        return result
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        清理文件名，移除危险字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        if not filename:
            return "untitled"
        
        # 移除路径分隔符和特殊字符
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # 限制长度
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
        
        return sanitized
    
    @classmethod
    def validate_sql_safe(cls, text: str) -> bool:
        """
        验证字符串是否包含 SQL 注入风险
        
        Args:
            text: 待验证的文本
            
        Returns:
            bool: 是否安全
        """
        if not text:
            return True
        
        text_lower = text.lower()
        dangerous_patterns = [
            "union", "select", "insert", "update", "delete",
            "drop", "create", "alter", "exec", "execute",
            "--", "/*", "*/", "xp_", "sp_", "script",
        ]
        
        for pattern in dangerous_patterns:
            if pattern in text_lower:
                return False
        
        return True


class RSAKeyManager:
    """
    RSA 密钥管理类
    用于前端密码加密传输
    """
    
    _private_key = None
    _public_key_pem = None
    _key_dir = Path(__file__).parent.parent.parent / "keys"
    
    @classmethod
    def _ensure_key_dir(cls):
        """确保密钥目录存在"""
        cls._key_dir.mkdir(exist_ok=True, mode=0o700)  # 仅所有者可访问
    
    @classmethod
    def _get_key_paths(cls) -> Tuple[Path, Path]:
        """获取密钥文件路径"""
        cls._ensure_key_dir()
        private_key_path = cls._key_dir / "rsa_private_key.pem"
        public_key_path = cls._key_dir / "rsa_public_key.pem"
        return private_key_path, public_key_path
    
    @classmethod
    def generate_key_pair(cls, key_size: int = 2048) -> None:
        """
        生成 RSA 密钥对
        
        Args:
            key_size: 密钥长度（默认 2048 位）
        """
        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        # 获取公钥
        public_key = private_key.public_key()
        
        # 序列化私钥
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # 序列化公钥
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # 保存密钥
        private_key_path, public_key_path = cls._get_key_paths()
        private_key_path.write_bytes(private_pem)
        public_key_path.write_bytes(public_pem)
        
        # 设置文件权限（仅所有者可读写）
        os.chmod(private_key_path, 0o600)
        os.chmod(public_key_path, 0o644)
        
        # 更新内存中的密钥
        cls._private_key = private_key
        cls._public_key_pem = public_pem.decode('utf-8')
    
    @classmethod
    def load_keys(cls) -> None:
        """从文件加载密钥"""
        private_key_path, public_key_path = cls._get_key_paths()
        
        if not private_key_path.exists() or not public_key_path.exists():
            # 如果密钥不存在，生成新的密钥对
            cls.generate_key_pair()
            return
        
        # 加载私钥
        private_pem = private_key_path.read_bytes()
        cls._private_key = serialization.load_pem_private_key(
            private_pem,
            password=None,
            backend=default_backend()
        )
        
        # 加载公钥
        public_pem = public_key_path.read_bytes()
        cls._public_key_pem = public_pem.decode('utf-8')
    
    @classmethod
    def get_public_key_pem(cls) -> str:
        """
        获取公钥（PEM 格式）
        
        Returns:
            str: PEM 格式的公钥
        """
        if cls._public_key_pem is None:
            cls.load_keys()
        return cls._public_key_pem
    
    @classmethod
    def decrypt_password(cls, encrypted_password: str) -> str:
        """
        解密密码
        
        Args:
            encrypted_password: Base64 编码的加密密码
            
        Returns:
            str: 解密后的明文密码
            
        Raises:
            ValueError: 解密失败
        """
        if cls._private_key is None:
            cls.load_keys()
        
        try:
            # Base64 解码
            encrypted_bytes = base64.b64decode(encrypted_password)
            
            # RSA 解密 - 使用 PKCS1v15 填充（与 JSEncrypt 兼容）
            # JSEncrypt 默认使用 PKCS1 填充，所以后端也需要使用相同的填充方式
            decrypted = cls._private_key.decrypt(
                encrypted_bytes,
                padding.PKCS1v15()
            )
            
            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError(f"密码解密失败: {str(e)}")
    
    @classmethod
    def get_public_key_for_frontend(cls) -> dict:
        """
        获取前端可用的公钥格式（JSON 格式，便于前端使用）
        
        Returns:
            dict: 包含公钥信息的字典
        """
        public_key_pem = cls.get_public_key_pem()
        
        # 移除 PEM 格式的头部和尾部，只保留密钥内容
        key_content = public_key_pem.replace('-----BEGIN PUBLIC KEY-----', '')
        key_content = key_content.replace('-----END PUBLIC KEY-----', '')
        key_content = key_content.replace('\n', '').strip()
        
        return {
            "publicKey": public_key_pem,  # 完整 PEM 格式
            "publicKeyBase64": key_content,  # Base64 格式（用于某些前端库）
        }
