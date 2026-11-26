# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(__file__).with_name("01-存储引擎.md")
text = path.read_text(encoding="utf-8")

marker = "存储引擎选择，在选择存在引擎时"
idx = text.index(marker)
# keep everything before the raw dump; also drop trailing blank lines before it carefully
head = text[:idx].rstrip() + "\n\n"

new = """---

## 理解与实践：按业务选引擎

选择存储引擎时，应根据应用系统特点来选；复杂系统里**一张库也可以多引擎组合**（例如订单用 InnoDB，临时统计用 Memory）。

| 引擎 | 什么时候选（理解） | 现在使用的代替方案
|------|-------------------|
| **InnoDB** | 默认引擎；要事务、外键；并发下要数据一致；除插入/查询外还有大量更新、删除 |
| **MyISAM** | 以读和插入为主，更新/删除很少；对事务完整性、并发要求不高（新项目一般仍优先 InnoDB） | MOGODB(文档数据库)
| **MEMORY** | 数据放内存，访问快，适合临时表/缓存；表不能太大，且**不能保障数据安全**（重启/断电会丢） | Redis(缓存数据库)

### 实践案例 1：订单库用 InnoDB（要事务）

**场景**：下单时「扣库存 + 写订单」必须同成同败。

```sql
CREATE TABLE demo_stock (
  id INT PRIMARY KEY,
  name VARCHAR(50),
  stock INT
) ENGINE = InnoDB;

CREATE TABLE demo_order (
  id INT PRIMARY KEY AUTO_INCREMENT,
  product_id INT,
  qty INT
) ENGINE = InnoDB;

INSERT INTO demo_stock VALUES (1, '键盘', 10);

START TRANSACTION;
UPDATE demo_stock SET stock = stock - 1 WHERE id = 1 AND stock >= 1;
INSERT INTO demo_order (product_id, qty) VALUES (1, 1);
-- 任一步失败就 ROLLBACK；都成功再 COMMIT
COMMIT;
```

**体会**：中途报错执行 `ROLLBACK`，库存和订单一起回到原状——这是 InnoDB 事务能力。

### 实践案例 2：日志/流水偏读写入用 MyISAM（了解即可）

**场景**：只不断追加访问日志，几乎不改不删，对事务要求低。

```sql
CREATE TABLE demo_access_log (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  url VARCHAR(200),
  created_at DATETIME
) ENGINE = MyISAM;

INSERT INTO demo_access_log (user_id, url, created_at)
VALUES (1, '/home', NOW());

SELECT * FROM demo_access_log WHERE user_id = 1;
```

**体会**：写多读多、少更新时 MyISAM 历史上常见；但新项目仍可用 InnoDB 统一运维，不必强行混用。

### 实践案例 3：会话缓存用 MEMORY（可丢）

**场景**：存放登录验证码、短期计数；丢了可重新生成。

```sql
CREATE TABLE demo_sms_code (
  mobile CHAR(11) PRIMARY KEY,
  code CHAR(6),
  expire_at DATETIME
) ENGINE = MEMORY;

INSERT INTO demo_sms_code VALUES ('13800000000', '123456', DATE_ADD(NOW(), INTERVAL 5 MINUTE));
SELECT * FROM demo_sms_code WHERE mobile = '13800000000';
```

**体会**：查很快；重启 MySQL 后表结构还在，**数据没了**。别把用户、订单放进 MEMORY。

### 实践案例 4：同一库组合使用

```sql
-- 核心业务
CREATE TABLE demo_user (id INT PRIMARY KEY, name VARCHAR(50)) ENGINE = InnoDB;

-- 临时排行（可丢，定期重算写入）
CREATE TABLE demo_rank_cache (
  user_id INT PRIMARY KEY,
  score INT
) ENGINE = MEMORY;
```

**体会**：不是「整个库只能选一个引擎」，而是**按表的业务特点分别选**。
"""

path.write_text(head + new, encoding="utf-8")
print("ok")
