# StockClaw 使用操作手册

## 🚀 快速开始

### 安装后首次使用
```bash
# 1. 设置别名（如果还没做）
source ~/.bashrc

# 2. 测试系统
stockclaw analyze 600096

# 3. 查看帮助
stockclaw
```

### 基本命令
```bash
# 分析单只股票
stockclaw analyze 600096

# 分析多只股票
stockclaw multi 600096 000001 600036

# 找出最优股票
stockclaw best 600096 000001 600036

# 查看交易总结
stockclaw summary 7      # 最近7天
stockclaw summary 30     # 最近30天

# 策略优化
stockclaw optimize
```

## 📊 日常使用流程

### 早上开盘前（9:00）
```bash
# 1. 分析关注列表
stockclaw multi 600096 000001 600036 000858

# 2. 找出今日最优
stockclaw best 600096 000001 600036

# 3. 查看具体建议
stockclaw analyze 600096
```

### 盘中监控（实时）
```bash
# 1. 快速分析当前持仓
stockclaw analyze 600096

# 2. 查看风险提示
# （系统会自动计算止损位和风险收益比）

# 3. 记录交易决策
# 使用 record_trade 方法记录买入/卖出
```

### 收盘后（15:00）
```bash
# 1. 查看今日盈亏
stockclaw summary 1

# 2. 分析交易结果
# 系统会自动分析盈利/亏损原因

# 3. 策略优化
stockclaw optimize

# 4. 准备明日计划
stockclaw multi [明日关注列表]
```

## 💰 具体操作示例

### 示例1：买入云天化
```bash
# 1. 分析股票
stockclaw analyze 600096

# 输出示例：
# 当前价: ¥43.13
# 建议: 买入
# 买入价: ¥42.80
# 目标价: ¥45.72 (+6.0%)
# 止损价: ¥41.50 (-3.8%)
# 持有: 5天
# 仓位: 15%

# 2. 记录买入（假设以¥42.90买入）
python3 -c "
import sys
sys.path.append('~/.stockclaw')
from fast_trader_fixed import FastTrader
trader = FastTrader()
trader.record_trade(suggestion_id=7, buy_price=42.90, sell_price=0, position=0.15)
print('✅ 买入记录已保存')
"
```

### 示例2：卖出并分析
```bash
# 1. 卖出（假设以¥44.50卖出）
python3 -c "
import sys
sys.path.append('~/.stockclaw')
from fast_trader_fixed import FastTrader
trader = FastTrader()
# 先获取最近建议ID，然后记录卖出
trader.record_trade(suggestion_id=7, buy_price=42.90, sell_price=44.50, position=0.15)
print('✅ 卖出记录已保存')
"

# 2. 查看具体盈亏
stockclaw summary 1

# 输出示例：
# 交易次数: 1
# 盈利次数: 1
# 胜率: 100.0%
# 总盈亏: +240.00元
# 平均收益: +3.7%

# 3. 查看原因分析
python3 -c "
import sqlite3
db = sqlite3.connect('~/.stockclaw/data/fast_trades.db')
cursor = db.cursor()
cursor.execute('SELECT reason, lesson FROM trades ORDER BY id DESC LIMIT 1')
result = cursor.fetchone()
if result:
    print(f'盈利原因: {result[0]}')
    print(f'经验教训: {result[1]}')
db.close()
"
```

## 🔧 高级功能

### 自定义分析参数
```python
# custom_analysis.py
from fast_trader_fixed import FastTrader

class CustomTrader(FastTrader):
    def analyze(self, code):
        # 调用父类分析
        result = super().analyze(code)
        
        # 自定义逻辑
        if result and result['score'] >= 6:
            # 提高目标收益
            result['exp_return'] = min(result['exp_return'] + 2, 20)
            # 缩短持有时间
            result['days'] = max(result['days'] - 1, 1)
        
        return result

# 使用
trader = CustomTrader()
result = trader.analyze("600096")
```

### 批量分析并导出
```bash
# 分析股票列表并导出CSV
python3 -c "
import csv
from fast_trader_fixed import FastTrader

stocks = ['600096', '000001', '600036', '000858', '000002']
trader = FastTrader()

with open('stock_analysis.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['代码', '建议', '当前价', '目标价', '止损价', '持有天数', '预期收益', '风险收益比'])
    
    for code in stocks:
        result = trader.analyze(code)
        if result:
            writer.writerow([
                code,
                result['rec'],
                f'{result[\"price\"]:.2f}',
                f'{result[\"target\"]:.2f}',
                f'{result[\"stop\"]:.2f}',
                result['days'],
                f'{result[\"exp_return\"]}%',
                f'{result[\"risk_reward\"]:.2f}'
            ])

print('✅ 分析结果已导出到 stock_analysis.csv')
"
```

### 自动监控脚本
```bash
#!/bin/bash
# auto_monitor.sh
# 自动监控股票并发送提醒

STOCKS="600096 000001 600036"
ALERT_PRICE=45.00  # 提醒价格

while true; do
    for stock in $STOCKS; do
        # 获取当前价格（简化示例）
        PRICE=$(python3 -c "
import sys
sys.path.append('~/.stockclaw')
from fast_trader_fixed import FastTrader
trader = FastTrader()
result = trader.analyze('$stock')
if result:
    print(result['price'])
        ")
        
        if (( $(echo "$PRICE >= $ALERT_PRICE" | bc -l) )); then
            echo "🚨 $stock 价格达到 ¥$PRICE，超过提醒价 ¥$ALERT_PRICE"
            # 这里可以添加邮件、短信等通知
        fi
    done
    
    sleep 300  # 每5分钟检查一次
done
```

## 📈 绩效分析

### 查看详细绩效报告
```bash
# 生成月度报告
python3 -c "
import sqlite3
from datetime import datetime, timedelta

db = sqlite3.connect('~/.stockclaw/data/fast_trades.db')
cursor = db.cursor()

# 本月数据
start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
cursor.execute('''
    SELECT 
        COUNT(*) as total_trades,
        SUM(CASE WHEN result = \"盈利\" THEN 1 ELSE 0 END) as wins,
        SUM(profit) as total_profit,
        AVG(profit_pct) as avg_return,
        MIN(profit_pct) as worst_trade,
        MAX(profit_pct) as best_trade
    FROM trades
    WHERE sell_date >= ?
''', (start_date,))

stats = cursor.fetchone()
db.close()

if stats and stats[0] > 0:
    total, wins, profit, avg, worst, best = stats
    win_rate = wins / total * 100
    
    print('📊 本月绩效报告')
    print('='*40)
    print(f'交易次数: {total}')
    print(f'盈利次数: {wins}')
    print(f'胜率: {win_rate:.1f}%')
    print(f'总盈亏: ¥{profit:.2f}')
    print(f'平均收益: {avg:.2f}%')
    print(f'最佳交易: {best:.2f}%')
    print(f'最差交易: {worst:.2f}%')
    print(f'风险收益比: {abs(avg/worst):.2f}' if worst < 0 else '风险收益比: N/A')
"
```

### 策略回测
```bash
# 回测最近30天建议
python3 -c "
import sqlite3
from datetime import datetime, timedelta

db = sqlite3.connect('~/.stockclaw/data/fast_trades.db')
cursor = db.cursor()

# 获取最近30天建议
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
cursor.execute('''
    SELECT s.code, s.rec, s.exp_return, 
           COALESCE(t.profit_pct, 0) as actual_return,
           CASE WHEN t.profit_pct IS NULL THEN '未执行'
                WHEN t.profit_pct > 0 THEN '盈利'
                ELSE '亏损' END as status
    FROM suggestions s
    LEFT JOIN trades t ON s.id = t.sug_id
    WHERE s.date >= ?
    ORDER BY s.date DESC
''', (start_date,))

results = cursor.fetchall()
db.close()

print('📈 策略回测报告（最近30天）')
print('='*50)
for row in results:
    code, rec, exp, actual, status = row
    diff = actual - exp if actual != 0 else 0
    print(f'{code}: {rec} (预期{exp}%, 实际{actual:.1f}%, {status}, 偏差{diff:+.1f}%)')
"
```

## 🔍 故障排除

### 常见问题及解决

**问题1：命令找不到**
```bash
# 检查别名设置
source ~/.bashrc
type stockclaw

# 手动运行
~/.stockclaw/stockclaw.sh analyze 600096
```

**问题2：Python模块导入错误**
```bash
# 检查Python路径
python3 -c "import sys; print(sys.path)"

# 添加路径
export PYTHONPATH="$PYTHONPATH:$HOME/.stockclaw"
```

**问题3：数据库连接错误**
```bash
# 检查数据库文件
ls -la ~/.stockclaw/data/

# 修复权限
chmod 644 ~/.stockclaw/data/*.db

# 重建数据库
rm ~/.stockclaw/data/fast_trades.db
sqlite3 ~/.stockclaw/data/fast_trades.db < ~/.stockclaw/data/init_database.sql
```

**问题4：数据获取失败**
```bash
# 检查网络连接
ping www.baidu.com

# 检查数据源
python3 -c "
from utils.data_source_manager import get_data_source_manager
manager = get_data_source_manager()
print('数据源状态:', manager.status)
"
```

## 📱 集成到其他系统

### 集成到交易软件
```python
# integration_example.py
import subprocess
import json

def get_stock_signal(stock_code):
    """获取股票信号"""
    result = subprocess.run(
        ['stockclaw', 'analyze', stock_code],
        capture_output=True,
        text=True
    )
    
    # 解析输出
    lines = result.stdout.split('\n')
    signal = {
        'code': stock_code,
        'recommendation': '未知',
        'price': 0,
        'target': 0,
        'stop': 0
    }
    
    for line in lines:
        if '当前价:' in line:
            signal['price'] = float(line.split('¥')[1])
        elif '建议:' in line:
            signal['recommendation'] = line.split('建议:')[1].strip()
        elif '目标价:' in line:
            signal['target'] = float(line.split('¥')[1].split()[0])
        elif '止损价:' in line:
            signal['stop'] = float(line.split('¥')[1])
    
    return signal

# 使用
signal = get_stock_signal('600096')
print(json.dumps(signal, indent=2, ensure_ascii=False))
```

### 集成到监控面板
```html
<!-- dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>StockClaw 监控面板</title>
    <script>
        async function updateStocks() {
            const stocks = ['600096', '000001', '600036'];
            const results = [];
            
            for (const stock of stocks) {
                const response = await fetch(`/api/analyze/${stock}`);
                const data = await response.json();
                results.push(data);
            }
            
            // 更新界面
            updateDashboard(results);
        }
        
        setInterval(updateStocks, 60000); // 每分钟更新
    </script>
</head>
<body>
    <h1>StockClaw 实时监控</h1>
    <div id="dashboard"></div>
</body>
</html>
```

## 📚 学习资源

### 内置学习材料
```bash
# 查看学习记录
ls -la ~/.stockclaw/learning/

# 查看具体学习内容
cat ~/.stockclaw/learning/2026-03/03-15_ATR指标学习/README.md
```

### 技能文档
```bash
# 查看可用技能
ls -la ~/.stockclaw/skills/

# 查看技能说明
cat ~/.stockclaw/skills/technical-analysis/SKILL.md
```

## 🆘 技术支持

### 获取帮助
```bash
# 查看系统状态
stockclaw --help

# 查看日志
tail -f ~/.stockclaw/stockclaw.log

# 重置系统
~/.stockclaw/reset_system.sh
```

### 报告问题
1. 检查日志：`cat ~/.stockclaw/error.log`
2. 收集信息：`~/.stockclaw/diagnose.sh`
3. 提交Issue：https://github.com/ljl86092297/stockclaw/issues

## ✅ 使用检查清单

- [ ] 安装完成并测试通过
- [ ] 数据库初始化完成
- [ ] 基本命令可以正常使用
- [ ] 数据获取正常
- [ ] 交易记录功能正常
- [ ] 绩效分析功能正常
- [ ] 备份策略已建立
- [ ] 监控脚本已设置（可选）

---

**记住：投资有风险，本系统仅为分析工具，不构成投资建议。**