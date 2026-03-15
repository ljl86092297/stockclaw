# StockAnalyzer 可移植包

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
