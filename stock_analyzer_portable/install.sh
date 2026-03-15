#!/bin/bash
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
