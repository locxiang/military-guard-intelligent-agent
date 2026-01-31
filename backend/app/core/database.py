"""
数据库连接管理模块
支持 SQLAlchemy 2.0 异步操作
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy 模型基类"""
    pass


# 创建异步数据库引擎
# 注意：pymysql 不支持异步，需要使用 aiomysql 或 asyncmy
# 这里使用 asyncmy 作为 MySQL 异步驱动
database_url = settings.database_url
if "mysql+pymysql://" in database_url:
    database_url = database_url.replace("mysql+pymysql://", "mysql+asyncmy://")
elif "mysql://" in database_url and "mysql+asyncmy://" not in database_url:
    database_url = database_url.replace("mysql://", "mysql+asyncmy://")

# 确保数据库连接使用 UTF-8 编码
# 在连接字符串中添加 charset 参数
if "?" not in database_url:
    database_url += "?charset=utf8mb4"
elif "charset=" not in database_url:
    database_url += "&charset=utf8mb4"
else:
    # 如果已有 charset 参数，确保是 utf8mb4
    import re
    database_url = re.sub(r'charset=[^&]+', 'charset=utf8mb4', database_url)

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,  # 开发环境打印SQL
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_pre_ping=True,  # 连接前检查连接是否有效
    pool_recycle=3600,  # 连接回收时间（秒）
    future=True,
    # 设置连接参数确保使用 UTF-8
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
        "init_command": "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci",
    } if "asyncmy" in database_url else {}
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    用于 FastAPI 路由中
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    初始化数据库
    创建所有表结构（如果不存在）
    """
    async with engine.begin() as conn:
        # 通过 SQLAlchemy 创建表结构（如果不存在）
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    关闭数据库连接
    """
    await engine.dispose()
