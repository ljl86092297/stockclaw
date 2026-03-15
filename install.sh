#!/bin/bash
# StockClaw 一键安装脚本
# 版本: 1.0
# 功能: 安装短线交易系统 + 数据库初始化

echo "🚀 StockClaw 安装开始"
echo "========================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python3，请先安装"
    exit 1
fi

echo "✅ Python3 已安装"

# 创建安装目录
INSTALL_DIR="$HOME/.stockclaw"
DATA_DIR="$INSTALL_DIR/data"
CONFIG_DIR="$INSTALL_DIR/config"

mkdir -p "$INSTALL_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$CONFIG_DIR"

echo "📁 创建目录: $INSTALL_DIR"

# 复制核心文件
echo "📦 复制核心文件..."

# 复制Python脚本
cp fast_trader_fixed.py "$INSTALL_DIR/"
cp simple_analyzer.py "$INSTALL_DIR/"
cp stock_analyzer.py "$INSTALL_DIR/"
cp analyze_ytf.py "$INSTALL_DIR/"

# 复制工具函数
mkdir -p "$INSTALL_DIR/utils"
cp utils/data_source_manager.py "$INSTALL_DIR/utils/"

# 复制技能（可选）
mkdir -p "$INSTALL_DIR/skills"
cp -r skills/* "$INSTALL_DIR/skills/" 2>/dev/null || true

# 创建数据库结构
echo "🗄️ 初始化数据库..."

cat > "$DATA_DIR/init_database.sql" << 'EOF'
-- StockClaw 数据库结构
-- 短线交易系统

CREATE TABLE IF NOT EXISTS suggestions (
    id INTEGER PRIMARY KEY,
    code TEXT,
    date TEXT,
    price REAL,
    ma5 REAL,
    volume_ratio REAL,
    change_5d REAL,
    rec TEXT,
    buy_price REAL,
    target REAL,
    stop REAL,
    days INTEGER,
    position REAL,
    exp_return REAL,
    risk_reward REAL
);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY,
    sug_id INTEGER,
    code TEXT,
    buy_date TEXT,
    buy_price REAL,
    sell_date TEXT,
    sell_price REAL,
    profit REAL,
    profit_pct REAL,
    result TEXT,
    reason TEXT,
    lesson TEXT
);
EOF

# 初始化数据库
if command -v sqlite3 &> /dev/null; then
    sqlite3 "$DATA_DIR/fast_trades.db" < "$DATA_DIR/init_database.sql"
    echo "✅ 数据库初始化完成: $DATA_DIR/fast_trades.db"
else
    echo "⚠️  sqlite3 未安装，数据库将首次运行时创建"
fi

# 创建配置文件
cat > "$CONFIG_DIR/config.yaml" << 'EOF'
# StockClaw 配置
database:
  path: "~/.stockclaw/data/fast_trades.db"
  
trading:
  holding_days_min: 1
  holding_days_max: 14
  target_return_min: 5
  target_return_max: 20
  stop_loss_max: 8
  position_max: 0.25
  
data_source:
  primary: "baostock"
  backup: "akshare"
  cache_days: 7
EOF

# 创建启动脚本
cat > "$INSTALL_DIR/stockclaw.sh" << 'EOF'
#!/bin/bash
# StockClaw 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Commands:"
    echo "  analyze <stock_code>     分析单只股票"
    echo "  multi <code1> <code2>... 分析多只股票"
    echo "  best <code1> <code2>...  找出最优股票"
    echo "  summary [days]           获取交易总结"
    echo "  optimize                 策略优化"
    echo ""
    echo "Examples:"
    echo "  $0 analyze 600096"
    echo "  $0 multi 600096 000001 600036"
    echo "  $0 best 600096 000001"
    echo "  $0 summary 7"
    exit 1
fi

COMMAND="$1"
shift

case "$COMMAND" in
    analyze)
        python3 fast_trader_fixed.py "$@"
        ;;
    multi)
        python3 -c "
import sys
sys.path.append('.')
from fast_trader_fixed import FastTrader
trader = FastTrader()
codes = sys.argv[1:]
for code in codes:
    result = trader.analyze(code)
    if result:
        print(f'{code}: {result[\"rec\"]} (预期{result[\"exp_return\"]}%)')
        " "$@"
        ;;
    best)
        python3 -c "
import sys
sys.path.append('.')
from fast_trader_fixed import FastTrader
trader = FastTrader()
codes = sys.argv[1:]
best = trader.find_best(codes)
if best:
    print(f'最优: {best[\"code\"]}')
    print(f'建议: {best[\"rec\"]}')
    print(f'预期收益: {best[\"exp_return\"]}%')
    print(f'持有: {best[\"days\"]}天')
        " "$@"
        ;;
    summary)
        DAYS="${1:-7}"
        python3 -c "
import sys
sys.path.append('.')
from fast_trader_fixed import FastTrader
trader = FastTrader()
summary = trader.get_summary($DAYS)
if summary:
    for k, v in summary.items():
        print(f'{k}: {v}')
else:
    print('暂无交易记录')
        "
        ;;
    optimize)
        python3 -c "
import sys
sys.path.append('.')
from fast_trader_fixed import FastTrader
trader = FastTrader()
trader.optimize()
        "
        ;;
    *)
        echo "未知命令: $COMMAND"
        exit 1
        ;;
esac
EOF

chmod +x "$INSTALL_DIR/stockclaw.sh"

# 创建快捷命令
cat > "$INSTALL_DIR/setup_alias.sh" << 'EOF'
#!/bin/bash
# 设置别名

echo "添加 StockClaw 到 PATH..."
echo 'export PATH="$PATH:$HOME/.stockclaw"' >> ~/.bashrc
echo 'alias stockclaw="~/.stockclaw/stockclaw.sh"' >> ~/.bashrc

echo ""
echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "  1. 重新打开终端或运行: source ~/.bashrc"
echo "  2. 使用命令:"
echo "     stockclaw analyze 600096      # 分析股票"
echo "     stockclaw multi 600096 000001 # 多股分析"
echo "     stockclaw best 600096 000001  # 找出最优"
echo "     stockclaw summary 7           # 7天总结"
echo "     stockclaw optimize            # 策略优化"
echo ""
echo "数据库位置: ~/.stockclaw/data/fast_trades.db"
echo "配置位置: ~/.stockclaw/config/config.yaml"
EOF

chmod +x "$INSTALL_DIR/setup_alias.sh"

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install pandas numpy sqlite3 2>/dev/null || echo "⚠️  依赖安装失败，请手动安装: pip3 install pandas numpy"

echo ""
echo "🎉 StockClaw 安装完成！"
echo ""
echo "📋 下一步:"
echo "  1. 设置别名: ~/.stockclaw/setup_alias.sh"
echo "  2. 重新打开终端或运行: source ~/.bashrc"
echo "  3. 开始使用: stockclaw analyze 600096"
echo ""
echo "📁 安装目录: $INSTALL_DIR"
echo "🗄️  数据库: $DATA_DIR/fast_trades.db"
echo "⚙️  配置: $CONFIG_DIR/config.yaml"