# 07 · MySQL 管理

## 目标

掌握日常管理入门：配置与变量、用户权限、备份恢复思路；能完成「建用户、授权、逻辑备份」一类操作。

## 大纲

### 1. 安装与目录直觉

- 程序文件 / 数据目录 / 错误日志 / 配置文件（`my.cnf` / `my.ini`）  
- Windows / Linux 差异（按本机环境补充路径）

### 2. 系统变量与状态

```sql
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE '%character%';
SHOW STATUS LIKE 'Threads_connected';

-- 会话 / 全局
SET SESSION sql_mode = '...';
SET GLOBAL max_connections = 200;  -- 需权限；重启是否持久看配置文件
```

### 3. 用户与权限（DCL）

```sql
CREATE USER 'app'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT, INSERT, UPDATE ON demo.* TO 'app'@'%';
FLUSH PRIVILEGES;   -- 部分场景需要
SHOW GRANTS FOR 'app'@'%';
REVOKE INSERT ON demo.* FROM 'app'@'%';
DROP USER 'app'@'%';
```

- 最小权限原则：能只读就不要给写；能单库就不要 `*.*`  
- 主机匹配：`'user'@'localhost'` vs `'user'@'%'`

### 4. 备份与恢复入门

| 方式 | 工具/手段 | 说明 |
|------|-----------|------|
| 逻辑备份 | `mysqldump` | 易上手，适合中小库 |
| 物理备份 | 数据文件拷贝 / xtrabackup 等 | 大库、热备场景 |
| 增量思路 | Binlog | 时间点恢复（PITR）了解 |

```bash
# 逻辑备份示例
mysqldump -u root -p --single-transaction --databases demo > demo.sql

# 恢复
mysql -u root -p < demo.sql
```

### 5. 日常巡检清单（了解）

- 连接数、慢查询、磁盘与 binlog 增长  
- 主从延迟（若有复制）  
- 权限与账号审计

### 6. 与「运维」篇的边界

- 本篇：库内管理与备份入门  
- 更重的监控、高可用、复制拓扑可放到 [运维](../运维/)（待补）

## 小结

- 管理三件套：配置变量、权限账号、备份恢复  
- 授权遵循最小权限；备份要「练过恢复」才算数  
- `--single-transaction` 适合 InnoDB 热备逻辑导出

## 常见坑 / 面试点

- 只改 `SET GLOBAL` 不改配置文件 → 重启丢失  
- `mysqldump` 大表锁与一致性选项要分清引擎  
- 面试：逻辑备份 vs 物理备份；如何做时间点恢复  
