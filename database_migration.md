# StockClaw 数据库移植指南

## 📦 数据库文件说明

### 本地数据库文件（不上传Git）
```
fast_trades.db          # 短线交易数据库
short_term_trades.db    # 短线交易历史
stock_data.db           # 分析结果数据库
```

### 数据库结构
```sql
-- 主要表结构
suggestions: 交易建议表
  - id, code, date, price, ma5, volume_ratio, change_5d
  - rec, buy_price, target, stop, days, position
  - exp_return, risk_reward

trades: 实际交易表
  - id, sug_id, code, buy_date, buy_price, sell_date, sell_price
  - profit, profit_pct, result, reason, lesson
```

## 🔄 数据库移植方法

### 方法一：直接复制数据库文件
```bash
# 1. 从源机器复制数据库
scp user@source-machine:~/.stockclaw/data/fast_trades.db ~/.stockclaw/data/

# 2. 或使用U盘等介质复制
cp /media/usb/stockclaw_data/fast_trades.db ~/.stockclaw/data/

# 3. 设置正确权限
chmod 644 ~/.stockclaw/data/fast_trades.db
```

### 方法二：导出为SQL文件再导入
```bash
# 1. 在源机器导出
sqlite3 fast_trades.db .dump > fast_trades_backup.sql

# 2. 传输SQL文件
scp fast_trades_backup.sql user@new-machine:~

# 3. 在新机器导入
sqlite3 ~/.stockclaw/data/fast_trades.db < fast_trades_backup.sql
```

### 方法三：使用Python脚本迁移
```python
# migrate_database.py
import sqlite3
import json

def migrate_database(source_db, target_db):
    """迁移数据库"""
    source = sqlite3.connect(source_db)
    target = sqlite3.connect(target_db)
    
    # 复制suggestions表
    source.execute("SELECT * FROM suggestions")
    rows = source.fetchall()
    
    for row in rows:
        target.execute('''
        INSERT INTO suggestions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', row)
    
    # 复制trades表
    source.execute("SELECT * FROM trades")
    rows = source.fetchall()
    
    for row in rows:
        target.execute('''
        INSERT INTO trades VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', row)
    
    target.commit()
    source.close()
    target.close()
    print("✅ 数据库迁移完成")

# 使用
migrate_database("old_fast_trades.db", "new_fast_trades.db")
```

## 📊 数据验证

### 验证数据库完整性
```bash
# 1. 检查表结构
sqlite3 fast_trades.db ".schema"

# 2. 统计数据量
sqlite3 fast_trades.db "SELECT COUNT(*) FROM suggestions;"
sqlite3 fast_trades.db "SELECT COUNT(*) FROM trades;"

# 3. 查看最新记录
sqlite3 fast_trades.db "SELECT * FROM suggestions ORDER BY date DESC LIMIT 5;"
sqlite3 fast_trades.db "SELECT * FROM trades ORDER BY sell_date DESC LIMIT 5;"
```

### 验证Python访问
```python
import sqlite3

db = sqlite3.connect("fast_trades.db")
cursor = db.cursor()

# 检查表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("数据库表:", tables)

# 检查数据
cursor.execute("SELECT COUNT(*) FROM suggestions")
count = cursor.fetchone()[0]
print(f"建议记录数: {count}")

db.close()
```

## 🚀 完整移植流程

### 步骤1：在新机器安装StockClaw
```bash
# 克隆代码
git clone https://github.com/ljl86092297/stockclaw.git
cd stockclaw

# 运行安装脚本
./install.sh

# 设置别名
~/.stockclaw/setup_alias.sh
source ~/.bashrc
```

### 步骤2：迁移数据库
```bash
# 方法A：直接复制（推荐）
cp /path/to/old/fast_trades.db ~/.stockclaw/data/

# 方法B：导出导入
sqlite3 /path/to/old/fast_trades.db .dump > backup.sql
sqlite3 ~/.stockclaw/data/fast_trades.db < backup.sql
```

### 步骤3：验证移植
```bash
# 验证安装
stockclaw analyze 600096

# 验证数据库
stockclaw summary 30

# 测试功能
stockclaw multi 600096 000001 600036
stockclaw best 600096 000001
stockclaw optimize
```

## 🔧 故障排除

### 问题1：数据库文件损坏
```bash
# 修复数据库
sqlite3 fast_trades.db ".dump" | sqlite3 fast_trades_fixed.db
mv fast_trades_fixed.db fast_trades.db
```

### 问题2：权限问题
```bash
# 设置正确权限
chmod 644 ~/.stockclaw/data/*.db
chmod 755 ~/.stockclaw/stockclaw.sh
```

### 问题3：Python依赖缺失
```bash
# 安装依赖
pip3 install pandas numpy

# 或使用requirements.txt
pip3 install -r requirements.txt
```

### 问题4：数据库版本不兼容
```bash
# 导出为兼容格式
sqlite3 old.db ".dump" | sqlite3 new.db

# 或使用Python转换
python3 migrate_database.py old.db new.db
```

## 📈 数据备份策略

### 自动备份脚本
```bash
#!/bin/bash
# backup_stockclaw.sh
BACKUP_DIR="$HOME/stockclaw_backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# 备份数据库
cp "$HOME/.stockclaw/data/fast_trades.db" "$BACKUP_DIR/fast_trades_$DATE.db"

# 备份配置
cp -r "$HOME/.stockclaw/config" "$BACKUP_DIR/config_$DATE"

# 保留最近7天备份
find "$BACKUP_DIR" -name "*.db" -mtime +7 -delete

echo "✅ 备份完成: $BACKUP_DIR/fast_trades_$DATE.db"
```

### 添加到cron定时备份
```bash
# 编辑crontab
crontab -e

# 添加每天凌晨2点备份
0 2 * * * ~/stockclaw_backup.sh
```

## 💡 最佳实践

1. **定期备份数据库** - 至少每周一次
2. **版本控制配置** - 将config.yaml加入Git
3. **分离数据与代码** - 数据库不上传Git
4. **测试环境验证** - 先在测试环境移植
5. **文档记录** - 记录移植步骤和问题

## 📞 技术支持

如果移植遇到问题：
1. 检查错误日志：`tail -f ~/.stockclaw/error.log`
2. 验证Python环境：`python3 -c "import pandas; import sqlite3"`
3. 检查数据库完整性：`sqlite3 fast_trades.db "PRAGMA integrity_check;"`
4. 查看GitHub Issues：https://github.com/ljl86092297/stockclaw/issues

## ✅ 移植检查清单

- [ ] 代码克隆完成
- [ ] 安装脚本运行成功
- [ ] 数据库文件复制完成
- [ ] 权限设置正确
- [ ] Python依赖安装完成
- [ ] 功能测试通过
- [ ] 数据验证完成
- [ ] 备份策略建立