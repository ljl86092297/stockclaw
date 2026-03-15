#!/usr/bin/env python3
"""
简单股票分析器 - 具体数值 + 明确建议
数据库本地存储，可一键移植
"""

import sys
import os
import sqlite3
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

sys.path.append('/home/openclaw/.openclaw/workspace')
from utils.data_source_manager import get_data_source_manager

def init_database(db_path="stock_data.db"):
    """初始化数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 分析结果表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_code TEXT,
        analysis_date DATE,
        
        -- 价格指标
        current_price REAL,
        ma5 REAL,
        ma10 REAL,
        ma20 REAL,
        atr REAL,
        volume_ratio REAL,
        price_position REAL,
        
        -- 基本面
        pe REAL,
        pb REAL,
        
        -- 建议
        recommendation TEXT,
        buy_min REAL,
        buy_max REAL,
        target1 REAL,
        target2 REAL,
        stop_loss REAL,
        holding_days INTEGER,
        
        -- 条件
        buy_conditions TEXT,
        sell_conditions TEXT,
        stop_conditions TEXT,
        
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    return db_path

def analyze_stock(stock_code):
    """分析单只股票"""
    print(f"\n{'='*80}")
    print(f"🎯 {stock_code} 具体分析报告")
    print(f"{'='*80}")
    
    # 获取数据
    manager = get_data_source_manager()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    
    df = manager.get_stock_data(stock_code, start_date, end_date)
    if df is None or df.empty:
        print("❌ 无法获取数据")
        return
    
    # 计算技术指标
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    
    current_price = df['close'].iloc[-1]
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    ma10 = df['close'].rolling(10).mean().iloc[-1]
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    
    # ATR
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().iloc[-1]
    
    # 成交量
    avg_volume = df['volume'].mean()
    latest_volume = df['volume'].iloc[-1]
    volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 0
    
    # 价格位置
    period_high = df['high'].max()
    period_low = df['low'].min()
    price_position = (current_price - period_low) / (period_high - period_low) * 100 if period_high > period_low else 50
    
    # 获取基本面
    try:
        import baostock as bs
        lg = bs.login()
        pe = pb = 0
        
        rs = bs.query_history_k_data_plus(
            f"sh.{stock_code}" if stock_code.startswith('6') else f"sz.{stock_code}",
            'peTTM,pbMRQ',
            start_date='2025-03-01',
            end_date='2025-03-15'
        )
        
        if rs.error_code == '0':
            data = []
            while rs.next():
                data.append(rs.get_row_data())
            if data:
                pe = float(data[-1][0]) if data[-1][0] != '' else 0
                pb = float(data[-1][1]) if data[-1][1] != '' else 0
        
        bs.logout()
    except:
        pe = pb = 0
    
    # 计算综合评分
    score = 0
    if current_price > ma5: score += 1
    if current_price > ma20: score += 1
    if 30 < price_position < 70: score += 1
    if volume_ratio > 0.8: score += 1
    if 0 < pe < 20: score += 2
    elif 0 < pe < 30: score += 1
    if 0 < pb < 2: score += 1
    
    # 生成建议
    if score >= 7:
        recommendation = "强烈买入"
        buy_min = min(current_price * 0.97, ma20 * 0.98)
        buy_max = current_price * 1.03
        target1 = current_price * 1.08
        target2 = current_price * 1.15
        stop_loss = current_price - atr * 2
        holding_days = 90
    elif score >= 5:
        recommendation = "买入"
        buy_min = min(current_price * 0.96, ma20 * 0.97)
        buy_max = current_price * 1.02
        target1 = current_price * 1.06
        target2 = current_price * 1.12
        stop_loss = current_price - atr * 2
        holding_days = 60
    elif score >= 3:
        recommendation = "持有"
        buy_min = ma20 * 0.95
        buy_max = ma20 * 0.98
        target1 = current_price * 1.05
        target2 = current_price * 1.10
        stop_loss = current_price * 0.93
        holding_days = 30
    elif score >= 1:
        recommendation = "卖出"
        buy_min = buy_max = target1 = target2 = stop_loss = 0
        holding_days = 7
    else:
        recommendation = "强烈卖出"
        buy_min = buy_max = target1 = target2 = stop_loss = 0
        holding_days = 0
    
    # 输出报告
    print(f"\n📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"📊 当前价格: ¥{current_price:.2f}")
    
    print(f"\n📈 技术指标:")
    print(f"  MA5: ¥{ma5:.2f} ({'高于' if current_price > ma5 else '低于'}当前价)")
    print(f"  MA10: ¥{ma10:.2f}")
    print(f"  MA20: ¥{ma20:.2f} (支撑位)")
    print(f"  ATR: {atr:.4f}")
    print(f"  量比: {volume_ratio:.2f}")
    print(f"  价格位置: {price_position:.1f}%")
    
    print(f"\n🏢 基本面:")
    print(f"  市盈率: {pe:.2f}")
    print(f"  市净率: {pb:.2f}")
    
    print(f"\n🏆 综合评分: {score}/10")
    print(f"📊 投资评级: {recommendation}")
    
    print(f"\n{'─'*40}")
    print("🎯 具体操作建议")
    print(f"{'─'*40}")
    
    if recommendation == "强烈买入":
        print("✅ 决策: 立即买入")
        print(f"   买入区间: ¥{buy_min:.2f} - ¥{buy_max:.2f}")
        print(f"   目标价位: ¥{target1:.2f} (第一目标)")
        print(f"              ¥{target2:.2f} (第二目标)")
        print(f"   止损价位: ¥{stop_loss:.2f}")
        print(f"   建议持有: {holding_days} 天")
        
        print(f"\n⚡ 买入条件:")
        print(f"  • 价格跌至¥{ma20:.2f}附近")
        print(f"  • 出现利好新闻")
        print(f"  • 成交量放大")
        
    elif recommendation == "买入":
        print("✅ 决策: 建议买入")
        print(f"   买入区间: ¥{buy_min:.2f} - ¥{buy_max:.2f}")
        print(f"   目标价位: ¥{target1:.2f}")
        print(f"   止损价位: ¥{stop_loss:.2f}")
        print(f"   建议持有: {holding_days} 天")
        
    elif recommendation == "持有":
        print("🟡 决策: 观望/持有")
        print(f"   等待价格: ¥{buy_min:.2f} 以下")
        print(f"   如已持有，止损位: ¥{stop_loss:.2f}")
        
    elif recommendation == "卖出":
        print("🔴 决策: 建议卖出")
        print(f"   如持有，建议卖出")
        
    elif recommendation == "强烈卖出":
        print("🔴 决策: 立即卖出")
        print(f"   如持有，立即卖出")
    
    print(f"\n🚨 止损条件:")
    print(f"  • 价格跌破¥{stop_loss:.2f}")
    print(f"  • 出现重大利空")
    
    print(f"\n🔄 重新评估条件:")
    print(f"  • 出现重大新闻")
    print(f"  • 技术形态改变")
    print(f"  • 成交量异常")
    
    # 风险收益分析
    if current_price > 0 and target1 > 0 and stop_loss > 0:
        potential_return = (target1 - current_price) / current_price * 100
        potential_loss = (current_price - stop_loss) / current_price * 100
        
        print(f"\n📊 风险收益分析:")
        print(f"   潜在收益: {potential_return:.1f}%")
        print(f"   潜在亏损: {potential_loss:.1f}%")
        
        if potential_return > potential_loss * 2:
            print("   ✅ 风险收益比较佳")
        elif potential_return > potential_loss:
            print("   ⚠️ 风险收益比一般")
        else:
            print("   ❌ 风险收益比较差")
    
    # 保存到数据库
    db_path = init_database()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO stock_analysis (
        stock_code, analysis_date, current_price, ma5, ma10, ma20,
        atr, volume_ratio, price_position, pe, pb,
        recommendation, buy_min, buy_max, target1, target2, stop_loss, holding_days,
        buy_conditions, sell_conditions, stop_conditions
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        stock_code,
        datetime.now().strftime('%Y-%m-%d'),
        current_price, ma5, ma10, ma20, atr, volume_ratio, price_position, pe, pb,
        recommendation, buy_min, buy_max, target1, target2, stop_loss, holding_days,
        json.dumps(["价格跌至支撑位", "出现利好新闻"]),
        json.dumps(["达到目标价位", "出现利空新闻"]),
        json.dumps([f"跌破{stop_loss:.2f}", "基本面恶化"])
    ))
    
    conn.commit()
    conn.close()
    
    print(f"\n💾 分析结果已保存到: {db_path}")
    print(f"📅 下次评估: {(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}")
    print(f"\n{'='*80}")
    print("💎 核心观点: ", end="")
    
    if recommendation in ["强烈买入", "买入"]:
        print("估值合理，技术面支持，建议买入")
    elif recommendation == "持有":
        print("无明显优势，建议等待更好时机")
    else:
        print("存在风险，建议规避")
    
    print(f"{'='*80}\n")

def create_portable_package():
    """创建可移植包"""
    import shutil
    
    package_dir = "stock_analyzer_portable"
    os.makedirs(package_dir, exist_ok=True)
    
    # 1. 复制必要文件
    shutil.copy2(__file__, os.path.join(package_dir, "analyzer.py"))
    
    # 2. 创建数据库结构文件
    schema = '''-- StockAnalyzer 数据库结构
CREATE TABLE IF NOT EXISTS stock_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT,
    analysis_date DATE,
    current_price REAL,
    ma5 REAL,
    ma10 REAL,
    ma20 REAL,
    atr REAL,
    volume_ratio REAL,
    price_position REAL,
    pe REAL,
    pb REAL,
    recommendation TEXT,
    buy_min REAL,
    buy_max REAL,
    target1 REAL,
    target2 REAL,
    stop_loss REAL,
    holding_days INTEGER,
    buy_conditions TEXT,
    sell_conditions TEXT,
    stop_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''
    
    with open(os.path.join(package_dir, "database_schema.sql"), 'w') as f:
        f.write(schema)
    
    # 3. 创建安装脚本
    install_script = '''#!/bin/bash
echo "🚀 安装 StockAnalyzer..."
echo "========================"

# 创建目录
mkdir -p ~/.stock_analyzer
mkdir -p ~/.stock_analyzer/data

# 复制文件
cp analyzer.py ~/.stock_analyzer/
cp database_schema.sql ~/.stock_analyzer/

# 初始化数据库
cd ~/.stock_analyzer
sqlite3 data/stock_analysis.db < database_schema.sql

# 创建启动脚本
cat > ~/.stock_analyzer/analyze.sh << 'EOF'
#!/bin/bash
cd ~/.stock_analyzer
python3 analyzer.py "$@"
EOF

chmod +x ~/.stock_analyzer/analyze.sh

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "  分析股票: ~/.stock_analyzer/analyze.sh 600096"
echo ""
echo "数据库位置: ~/.stock_analyzer/data/stock_analysis.db"
echo "分析历史: sqlite3 ~/.stock_analyzer/data/stock_analysis.db 'SELECT * FROM stock_analysis;'"
echo ""
'''
    
    with open(os.path.join(package_dir, "install.sh"), 'w') as f:
        f.write(install_script)
    
    os.chmod(os.path.join(package_dir, "install.sh"), 0o755)
    
    # 4. 创建README
    readme = '''# StockAnalyzer 可移植包

## 安装方法
```bash
# 解压后运行
./install.sh
```

## 使用方法
```bash
# 分析股票
~/.stock_analyzer/analyze.sh 600096

# 或添加别名到.bashrc
echo "alias analyze='~/.stock_analyzer/analyze.sh'" >> ~/.bashrc
source ~/.bashrc
analyze 600096
```

## 数据库
- 位置: ~/.stock_analyzer/data/stock_analysis.db
- 不上传Git，本地存储
- 可复制到其他机器

## 功能
- 具体技术指标数值
- 明确买入/卖出/止损价格
- 风险收益分析
- 历史记录存储

## 数据迁移
复制 ~/.stock_analyzer/data/stock_analysis.db 文件即可。
'''
    
    with open(os.path.join(package_dir, "README.md"), 'w') as f:
        f.write(readme)
    
    # 5. 打包
    shutil.make_archive("stock_analyzer_portable", 'gztar', package_dir)
    
    print(f"\n📦 可移植包已创建: stock_analyzer_portable.tar.gz")
    print(f"   包含: analyzer.py + 数据库结构 + 安装脚本")
    print(f"   数据库文件不上传Git，本地存储")

if __name__ == "__main__":
    # 分析云天化
    analyze_stock("600096")
    
    # 创建可移植包
    create_portable_package()
    
    print("\n🎯 系统特点:")
    print("   1. 具体指标数值: MA5, MA20, ATR, PE等")
    print("   2. 明确建议: 买入区间、目标价、止损价、持有时间")
    print("   3. 数据库存储: 本地SQLite，不上传Git")
    print("   4. 一键移植: 安装脚本自动部署")
    print("   5. 自我改进: 历史记录可回溯验证")