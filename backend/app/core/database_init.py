"""
数据库初始化与结构同步模块
- 检查每个表是否存在，不存在则创建
- 检查每个表是否为空，为空则初始化数据
- 检查每个表结构是否与模型一致，不一致则同步
"""
from loguru import logger
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Inspector
from typing import Dict, Optional, Any

from app.core.database import Base, engine
from app.models import User, CaseFile, ImportTask, DocGenerateTask, OcrTask, DocTemplate
from app.core.audit import AuditLog  # 确保审计日志表参与 create_all


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        self.engine = None
        self.inspector: Optional[Inspector] = None
        
        # 表初始化配置：表名 -> 配置
        self.table_configs = {
            'users': {
                'model': User,
                'data_file': 'users.json',  # JSON 数据文件
            },
            'case_files': {
                'model': CaseFile,
                'data_file': 'case_files.json',  # JSON 数据文件
            },
            'import_tasks': {
                'model': ImportTask,
                'data_file': 'import_tasks.json',  # JSON 数据文件（可能为空）
            },
            'doc_generate_tasks': {
                'model': DocGenerateTask,
                'data_file': 'doc_generate_tasks.json',  # JSON 数据文件（可能为空）
            },
            'ocr_tasks': {
                'model': OcrTask,
                'data_file': 'ocr_tasks.json',  # JSON 数据文件（可能为空）
            },
            'doc_templates': {
                'model': DocTemplate,
                'data_file': 'doc_templates.json',  # 模板初始数据（可选）
            },
        }
    
    async def initialize(self):
        """初始化数据库"""
        try:
            # 使用全局引擎
            self.engine = engine
            
            # 创建检查器
            async with self.engine.connect() as conn:
                await conn.run_sync(self._create_inspector)
            
            logger.info("🔍 开始检查数据库初始化状态...")
            
            # 1. 确保所有表存在
            await self._ensure_tables_exist()
            
            # 2. 检查并初始化每个表的数据
            await self._init_table_data()
            
            # 3. 同步每个表的结构
            await self._sync_all_tables_structure()
            
            # 4. 结构同步后再次确保主键自增（避免同步时误改 id 或历史表缺自增）
            async with self.engine.begin() as conn:
                await self._ensure_primary_key_autoincrement(conn)
            
            logger.info("✅ 数据库初始化检查完成")
            
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {str(e)}")
            raise
    
    def _create_inspector(self, conn):
        """创建检查器（同步方法）"""
        self.inspector = inspect(conn)
    
    async def _ensure_tables_exist(self):
        """确保所有表存在，且主键 id 为自增（表结构初始化）"""
        logger.info("📋 表结构初始化：检查并创建表...")
        
        # 1. 创建所有表（若不存在）
        async with self.engine.begin() as conn:
            await conn.execute(text("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"))
            await conn.execute(text("SET CHARACTER SET utf8mb4"))
            await conn.run_sync(Base.metadata.create_all)
        logger.info("📋 表结构初始化：create_all 已完成")
        
        # 2. 单独事务：确保主表 id 列为自增（MySQL 1364 必须，与 create_all 分开提交）
        async with self.engine.begin() as conn:
            await self._ensure_primary_key_autoincrement(conn)
        
        # 3. 其他表结构修补
        async with self.engine.begin() as conn:
            await conn.execute(text("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"))
            await self._fix_doc_templates(conn)
        
        # 4. 校验：确认 import_tasks.id 为自增
        await self._verify_autoincrement()
        logger.info("✅ 表结构初始化完成")
    
    async def _fix_doc_templates(self, conn):
        """确保 doc_templates 表结构正确（id 自增已在 _ensure_primary_key_autoincrement 中统一处理）"""
        try:
            await conn.execute(text("""
                ALTER TABLE doc_templates 
                ADD COLUMN file_path VARCHAR(500) NULL 
                COMMENT '模板文件路径（.docx 公文文件）'
            """))
            logger.info("✅ doc_templates.file_path 已添加")
        except Exception as e:
            if "Duplicate column" in str(e) or "1060" in str(e):
                logger.debug("doc_templates.file_path 已存在，跳过")
            else:
                logger.debug(f"doc_templates.file_path 修复跳过: {e}")

    async def _ensure_primary_key_autoincrement(self, conn):
        """
        表结构初始化：确保主表 id 列为自增。
        MySQL 若 id 未设置 AUTO_INCREMENT，INSERT 不写 id 会报 1364: Field 'id' doesn't have a default value。
        """
        tables_with_auto_id = ["import_tasks", "case_files", "ocr_tasks", "doc_generate_tasks", "doc_templates"]
        critical_tables = ["import_tasks", "case_files"]
        logger.info("📋 表结构初始化：确保主键 id 自增...")
        for table_name in tables_with_auto_id:
            try:
                await conn.execute(text(
                    f"ALTER TABLE `{table_name}` MODIFY COLUMN id BIGINT NOT NULL AUTO_INCREMENT"
                ))
                logger.info(f"✅ {table_name}.id 已设为自增")
            except Exception as e:
                err = str(e)
                if "1146" in err or "doesn't exist" in err.lower():
                    logger.debug(f"表 {table_name} 不存在，跳过: {e}")
                else:
                    logger.warning(f"表 {table_name}.id 自增设置失败: {e}")
                    if table_name in critical_tables:
                        raise

    async def _verify_autoincrement(self):
        """校验 import_tasks / case_files 的 id 是否为自增，若不是则打错并抛错"""
        for table_name in ("import_tasks", "case_files"):
            async with self.engine.connect() as conn:
                r = await conn.execute(text("""
                    SELECT COLUMN_NAME, EXTRA
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :tname AND COLUMN_NAME = 'id'
                """), {"tname": table_name})
                row = r.fetchone()
            if not row:
                logger.warning(f"表 {table_name} 或列 id 不存在，跳过自增校验")
                continue
            extra = (row[1] or "").lower()
            if "auto_increment" not in extra:
                msg = f"表 {table_name} 的 id 列未设置为自增。请删除该表后重启应用，或手动执行: ALTER TABLE {table_name} MODIFY COLUMN id BIGINT NOT NULL AUTO_INCREMENT"
                logger.error(msg)
                raise RuntimeError(msg)
            logger.info(f"✅ 校验通过：{table_name}.id 为自增")
    
    async def _init_table_data(self):
        """初始化表数据（分表检查）"""
        logger.info("📊 检查并初始化表数据...")
        
        # 确保数据库使用 UTF-8 编码
        async with self.engine.begin() as conn:
            # 设置会话字符集为 utf8mb4（必须在每个操作前设置）
            await conn.execute(text("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"))
            await conn.execute(text("SET CHARACTER SET utf8mb4"))
            await conn.execute(text("SET character_set_client = utf8mb4"))
            await conn.execute(text("SET character_set_connection = utf8mb4"))
            await conn.execute(text("SET character_set_results = utf8mb4"))
            
            for table_name, config in self.table_configs.items():
                await self._check_and_init_table_data(conn, table_name, config)
    
    async def _check_and_init_table_data(self, conn: AsyncSession, table_name: str, config: dict):
        """检查并初始化单个表的数据"""
        try:
            # 检查表是否为空
            is_empty = await self._is_table_empty(conn, table_name)
            
            if not is_empty:
                logger.debug(f"表 {table_name} 已有数据，跳过初始化")
                return
            
            # 检查是否有数据文件配置
            data_file = config.get('data_file')
            if not data_file:
                logger.debug(f"表 {table_name} 无数据文件配置，跳过初始化")
                return
            
            logger.info(f"表 {table_name} 为空，开始初始化...")
            
            # 从 JSON 文件加载并插入数据
            await self._init_table_from_json(conn, table_name, config['model'], data_file)
            
            logger.info(f"✅ 表 {table_name} 数据初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 初始化表 {table_name} 数据失败: {str(e)}")
            raise
    
    async def _is_table_empty(self, conn: AsyncSession, table_name: str) -> bool:
        """检查表是否为空"""
        try:
            result = await conn.execute(
                text(f"SELECT COUNT(*) as count FROM `{table_name}`")
            )
            count = result.scalar()
            return count == 0
        except Exception as e:
            # 如果表不存在，返回 True（需要初始化）
            logger.debug(f"检查表 {table_name} 是否为空时出错（可能表不存在）: {str(e)}")
            return True
    
    async def _init_table_from_json(self, conn: AsyncSession, table_name: str, model, json_file: str):
        """从 JSON 文件初始化表数据"""
        import json
        from pathlib import Path
        from datetime import datetime
        
        json_path = Path(__file__).parent.parent.parent / 'scripts' / 'data' / json_file
        
        if not json_path.exists():
            logger.warning(f"JSON 文件不存在: {json_path}")
            return
        
        # 再次确保连接使用 UTF-8 编码
        await conn.execute(text("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"))
        await conn.execute(text("SET CHARACTER SET utf8mb4"))
        
        # 读取 JSON 文件（确保 UTF-8 编码）
        try:
            json_content = json_path.read_text(encoding='utf-8')
            # 确保 JSON 内容是 UTF-8 编码的字符串
            if isinstance(json_content, bytes):
                json_content = json_content.decode('utf-8')
            data_list = json.loads(json_content, strict=False)
        except UnicodeDecodeError as e:
            logger.error(f"JSON 文件编码错误 {json_path}: {str(e)}")
            return
        except Exception as e:
            logger.error(f"读取 JSON 文件失败 {json_path}: {str(e)}")
            return
        
        if not data_list:
            logger.debug(f"JSON 文件 {json_file} 为空，跳过初始化")
            return
        
        # 转换数据格式并插入（确保 UTF-8 编码）
        inserted_count = 0
        for data_item in data_list:
            try:
                # 转换字段名：驼峰转下划线
                db_data = self._convert_to_db_format(data_item, model)
                
                # 确保所有字符串字段都是 UTF-8 编码
                db_data = self._ensure_utf8_encoding(db_data)
                
                # 构建 INSERT 语句
                table = model.__table__
                stmt = table.insert().values(**db_data)
                
                await conn.execute(stmt)
                inserted_count += 1
                
            except Exception as e:
                error_msg = str(e)
                import traceback
                # 忽略重复插入等错误
                if any(keyword in error_msg for keyword in [
                    'Duplicate entry', 'Duplicate key', 'already exists'
                ]):
                    logger.debug(f"数据已存在，跳过: {error_msg[:100]}")
                else:
                    logger.error(f"插入数据时出错: {error_msg}")
                    logger.error(f"错误详情: {traceback.format_exc()}")
                    # 不继续插入，记录错误后返回
                    raise
        
        if inserted_count > 0:
            logger.info(f"✅ 已从 {json_file} 初始化表 {table_name} ({inserted_count} 条记录)")
        else:
            logger.debug(f"表 {table_name} 的数据已存在或无需初始化")
    
    def _convert_to_db_format(self, data: dict, model) -> dict:
        """将 JSON 数据转换为数据库格式"""
        from datetime import datetime
        
        db_data = {}
        table = model.__table__
        
        for key, value in data.items():
            # JSON 文件使用下划线命名，直接使用
            if key not in table.columns:
                # 如果字段不存在，尝试转换驼峰命名
                snake_key = self._camel_to_snake(key)
                if snake_key in table.columns:
                    key = snake_key
                else:
                    # 字段不存在，跳过
                    continue
            
            # 处理值
            column = table.columns[key]
            
            # 处理日期时间字段
            if 'DateTime' in str(column.type) and isinstance(value, str):
                try:
                    db_data[key] = datetime.fromisoformat(value.replace(' ', 'T'))
                except:
                    db_data[key] = value
            # 处理 JSON 字段
            elif 'JSON' in str(column.type):
                db_data[key] = value  # JSON 字段直接使用
            # 处理其他字段
            else:
                db_data[key] = value
        
        return db_data
    
    def _camel_to_snake(self, name: str) -> str:
        """将驼峰命名转换为下划线命名"""
        import re
        # 在大写字母前插入下划线，然后转小写
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _ensure_utf8_encoding(self, data: dict) -> dict:
        """确保所有字符串字段都是 UTF-8 编码"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                # 字符串已经是 Unicode 字符串，直接使用
                # Python 3 中字符串默认就是 Unicode，不需要额外转换
                result[key] = value
            elif isinstance(value, bytes):
                # 如果是字节串，解码为 UTF-8
                try:
                    result[key] = value.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果解码失败，尝试忽略错误
                    result[key] = value.decode('utf-8', errors='ignore')
            elif isinstance(value, (dict, list)):
                # 递归处理嵌套的字典和列表
                result[key] = self._ensure_utf8_in_nested(value)
            else:
                result[key] = value
        return result
    
    def _ensure_utf8_in_nested(self, obj):
        """递归确保嵌套结构中的字符串都是 UTF-8"""
        if isinstance(obj, dict):
            return {k: self._ensure_utf8_in_nested(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._ensure_utf8_in_nested(item) for item in obj]
        elif isinstance(obj, str):
            # Python 3 字符串已经是 Unicode，直接返回
            return obj
        elif isinstance(obj, bytes):
            # 如果是字节串，解码为 UTF-8
            try:
                return obj.decode('utf-8')
            except UnicodeDecodeError:
                return obj.decode('utf-8', errors='ignore')
        else:
            return obj
    
    
    async def _sync_all_tables_structure(self):
        """同步所有表的结构"""
        logger.info("🔄 检查并同步表结构...")
        
        async with self.engine.begin() as conn:
            for table_name, config in self.table_configs.items():
                await self._sync_table_structure(conn, table_name, config['model'])
    
    async def _sync_table_structure(self, conn: AsyncSession, table_name: str, model):
        """同步单个表的结构"""
        try:
            # 获取期望的列定义（从模型）
            expected_columns = self._get_expected_columns(model)
            
            # 获取实际的列定义（从数据库）
            actual_columns = await self._get_actual_columns(conn, table_name)
            
            # 对比差异
            diff = self._compare_columns(expected_columns, actual_columns)
            
            if diff:
                # 生成并执行 ALTER TABLE
                alter_sql = self._generate_alter_table(table_name, diff)
                if alter_sql:
                    await conn.execute(text(alter_sql))
                    logger.info(f"✅ 表 {table_name} 结构已同步")
                else:
                    logger.debug(f"表 {table_name} 结构差异无法自动同步，需要手动处理")
            else:
                logger.debug(f"表 {table_name} 结构已是最新")
                
        except Exception as e:
            logger.warning(f"同步表 {table_name} 结构时出错: {str(e)}")
            # 不阻止启动，只记录警告
    
    def _get_expected_columns(self, model) -> Dict[str, dict]:
        """获取期望的列定义（从 SQLAlchemy 模型）"""
        columns = {}
        for column in model.__table__.columns:
            columns[column.name] = {
                'type': str(column.type),
                'nullable': column.nullable,
                'default': column.default,
                'primary_key': column.primary_key,
            }
        return columns
    
    async def _get_actual_columns(self, conn: AsyncSession, table_name: str) -> Dict[str, dict]:
        """获取实际的列定义（从数据库）"""
        columns = {}
        
        # 使用 INFORMATION_SCHEMA 查询
        result = await conn.execute(text(f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COLUMN_KEY
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """))
        
        for row in result:
            columns[row.COLUMN_NAME] = {
                'type': row.DATA_TYPE,
                'nullable': row.IS_NULLABLE == 'YES',
                'default': row.COLUMN_DEFAULT,
                'primary_key': row.COLUMN_KEY == 'PRI',
            }
        
        return columns
    
    def _compare_columns(self, expected: Dict[str, dict], actual: Dict[str, dict]) -> Dict[str, Any]:  # type: ignore
        """对比列定义差异"""
        diff = {
            'add': [],  # 需要添加的列
            'modify': [],  # 需要修改的列
        }
        
        # 检查需要添加的列
        for col_name, col_def in expected.items():
            if col_name not in actual:
                diff['add'].append((col_name, col_def))
        
        # 检查需要修改的列（类型、可空性等）
        for col_name, expected_def in expected.items():
            if col_name in actual:
                # 不修改主键列，避免 MySQL 丢失 AUTO_INCREMENT（MODIFY id 会去掉自增）
                if expected_def.get('primary_key'):
                    continue
                actual_def = actual[col_name]
                # 简化比较：只检查类型和可空性
                if (expected_def['type'] != actual_def['type'] or 
                    expected_def['nullable'] != actual_def['nullable']):
                    diff['modify'].append((col_name, expected_def))
        
        return diff
    
    def _generate_alter_table(self, table_name: str, diff: Dict[str, Any]) -> Optional[str]:
        """生成 ALTER TABLE 语句"""
        alter_statements = []
        
        # 添加新列（跳过主键，主键由建表时创建）
        for col_name, col_def in diff['add']:
            if col_def.get('primary_key'):
                continue
            nullable = 'NULL' if col_def['nullable'] else 'NOT NULL'
            alter_statements.append(f"ADD COLUMN `{col_name}` {col_def['type']} {nullable}")
        
        # 修改列（跳过主键，避免 MODIFY id 时 MySQL 丢失 AUTO_INCREMENT）
        for col_name, col_def in diff['modify']:
            if col_def.get('primary_key'):
                continue
            nullable = 'NULL' if col_def['nullable'] else 'NOT NULL'
            alter_statements.append(f"MODIFY COLUMN `{col_name}` {col_def['type']} {nullable}")
        
        if alter_statements:
            return f"ALTER TABLE `{table_name}` {', '.join(alter_statements)}"
        
        return None


# 全局初始化器实例
_initializer: Optional[DatabaseInitializer] = None


async def initialize_database():
    """初始化数据库（入口函数）"""
    global _initializer
    
    if _initializer is None:
        _initializer = DatabaseInitializer()
    
    await _initializer.initialize()
