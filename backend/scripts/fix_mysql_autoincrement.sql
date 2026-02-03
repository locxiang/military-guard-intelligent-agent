-- 修复 MySQL 报错: Field 'id' doesn't have a default value (1364)
-- 确保主表 id 列为自增。执行方式示例:
--   mysql -u user -p military_guard < scripts/fix_mysql_autoincrement.sql
-- 或 Docker: docker-compose exec mysql mysql -u user -p military_guard < backend/scripts/fix_mysql_autoincrement.sql

ALTER TABLE import_tasks MODIFY COLUMN id BIGINT NOT NULL AUTO_INCREMENT;
ALTER TABLE case_files MODIFY COLUMN id BIGINT NOT NULL AUTO_INCREMENT;
ALTER TABLE ocr_tasks MODIFY COLUMN id BIGINT NOT NULL AUTO_INCREMENT;
ALTER TABLE doc_generate_tasks MODIFY COLUMN id BIGINT NOT NULL AUTO_INCREMENT;
