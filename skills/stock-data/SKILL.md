---
name: stock-data
description: "获取A股股票数据，包括实时行情、K线数据、基本面信息。使用场景：用户询问股票价格、行情、K线图、技术指标等。"
metadata: { "openclaw": { "emoji": "📈", "requires": { "bins": ["python3"] } } }
---

# 股票数据获取 Skill (Baostock版本)

使用Baostock获取A股股票数据，支持K线数据、财务数据、估值指标等。

## 使用场景

✅ **使用此Skill当：**

- "查看300166的股价"
- "平安银行的K线图"
- "获取股票历史数据"
- "查看技术指标（MACD、KDJ、RSI）"
- "获取股票基本面信息"

## 功能列表

### 1. K线数据 (Baostock支持)
```bash
# 使用baostock获取日K数据
python3 -c "
import baostock as bs
import pandas as pd

# 登录
lg = bs.login()
if lg.error_code != '0':
    print('登录失败:', lg.error_msg)
    exit()

# 查询日K数据
rs = bs.query_history_k_data_plus('sh.600000', 
    'date,code,open,high,low,close,volume,amount,turn,pctChg',
    start_date='2025-01-01', end_date='2025-12-31', 
    frequency='d', adjustflag='3')
    
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
    
df = pd.DataFrame(data_list, columns=rs.fields)
print(f'获取到{len(df)}条记录')
print(df.head())

bs.logout()
"
```

### 2. 财务数据 (Baostock支持)
```bash
# 获取财务数据
python3 -c "
import baostock as bs
import pandas as pd

lg = bs.login()
if lg.error_code != '0':
    print('登录失败:', lg.error_msg)
    exit()

# 利润表数据
rs = bs.query_profit_data('sh.600000', year=2024, quarter=4)
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
    
df = pd.DataFrame(data_list, columns=rs.fields)
print('利润表数据:')
print(df.head())

bs.logout()
"
```

### 3. 估值指标 (Baostock支持)
```bash
# 获取估值指标
python3 -c "
import baostock as bs
import pandas as pd

lg = bs.login()
if lg.error_code != '0':
    print('登录失败:', lg.error_msg)
    exit()

rs = bs.query_daily_basic('sh.600000', start_date='2025-01-01', end_date='2025-01-10')
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
    
df = pd.DataFrame(data_list, columns=rs.fields)
print('估值指标:')
print(df[['date', 'code', 'pe', 'pb', 'ps', 'total_mv']])

bs.logout()
"
```

### 4. 公司基本信息 (Baostock支持)
```bash
# 获取公司基本信息
python3 -c "
import baostock as bs
import pandas as pd

lg = bs.login()
if lg.error_code != '0':
    print('登录失败:', lg.error_msg)
    exit()

rs = bs.query_stock_basic('sh.600000')
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
    
df = pd.DataFrame(data_list, columns=rs.fields)
print('公司基本信息:')
print(df)

bs.logout()
"
```

## 常用命令

### 查看单只股票
```bash
# 获取股票K线数据
python3 -c "
import baostock as bs
import pandas as pd

def get_stock_data(code, start_date='2025-01-01', end_date='2025-12-31'):
    lg = bs.login()
    if lg.error_code != '0':
        return None
    
    # 转换代码格式 (600000 -> sh.600000, 000001 -> sz.000001)
    if code.startswith('6'):
        bs_code = f'sh.{code}'
    else:
        bs_code = f'sz.{code}'
    
    rs = bs.query_history_k_data_plus(bs_code, 
        'date,open,high,low,close,volume,amount,turn,pctChg',
        start_date=start_date, end_date=end_date,
        frequency='d', adjustflag='3')
        
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg'])
    df[['open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg']] = \
        df[['open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg']].astype(float)
    
    bs.logout()
    return df

# 使用示例
df = get_stock_data('600000', '2025-01-01', '2025-01-31')
if df is not None:
    print('最近5天数据:')
    print(df.tail())
else:
    print('获取数据失败')
"
```

### 批量获取多只股票
```bash
# 获取多只股票基本信息
python3 -c "
import baostock as bs
import pandas as pd

def get_multiple_stocks(codes):
    lg = bs.login()
    if lg.error_code != '0':
        return None
    
    results = {}
    for code in codes:
        if code.startswith('6'):
            bs_code = f'sh.{code}'
        else:
            bs_code = f'sz.{code}'
        
        # 获取公司信息
        rs = bs.query_stock_basic(bs_code)
        info_list = []
        while (rs.error_code == '0') & rs.next():
            info_list.append(rs.get_row_data())
        
        if info_list:
            info_df = pd.DataFrame(info_list, columns=rs.fields)
            results[code] = info_df
    
    bs.logout()
    return results

# 使用示例
stocks = ['600000', '000001', '300166']
stock_info = get_multiple_stocks(stocks)
for code, info in stock_info.items():
    print(f'{code}: {info.iloc[0][\"code_name\"] if not info.empty else \"未找到\"}')
"
```

### 技术指标计算
```bash
# 基于Baostock数据计算技术指标
python3 -c "
import baostock as bs
import pandas as pd
import numpy as np

def calculate_technical_indicators(df):
    # 确保数据类型正确
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    
    # 移动平均线
    df['MA5'] = df['close'].rolling(5).mean()
    df['MA10'] = df['close'].rolling(10).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    return df

# 获取数据并计算指标
lg = bs.login()
if lg.error_code == '0':
    rs = bs.query_history_k_data_plus('sh.600000', 
        'date,close,volume',
        start_date='2025-01-01', end_date='2025-03-31',
        frequency='d', adjustflag='3')
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    df = pd.DataFrame(data_list, columns=['date', 'close', 'volume'])
    df[['close', 'volume']] = df[['close', 'volume']].astype(float)
    
    df = calculate_technical_indicators(df)
    print('技术指标计算结果:')
    print(df[['date', 'close', 'MA5', 'MA20', 'RSI', 'MACD']].tail())
    
    bs.logout()
else:
    print('登录失败:', lg.error_msg)
"
```

## Baostock支持的数据类型

### ✅ 支持的数据
1. **K线数据**: 日、周、月、5分钟、15分钟、30分钟、60分钟
2. **财务数据**: 利润表、资产负债表、现金流量表
3. **估值指标**: PE、PB、PS、总市值、流通市值
4. **公司信息**: 名称、行业、地区、上市日期
5. **行业分类**: 行业归属信息
6. **成长能力**: 营收增长率、净利润增长率等
7. **营运能力**: 应收账款周转率、存货周转率等
8. **杜邦分析**: ROE分解指标

### ❌ 不支持的数据
1. 实时行情（有延迟）
2. 新闻数据
3. 社交媒体数据
4. 非A股市场数据
5. 期权、期货数据

## 安装依赖

```bash
pip install baostock pandas numpy
```

## 注意事项

1. **需要登录**: Baostock需要先登录才能使用
2. **数据延迟**: 非实时数据，通常有T+1延迟
3. **代码格式**: A股代码需要转换为sh.或sz.前缀
4. **频率限制**: 避免过于频繁的请求
5. **数据质量**: Baostock数据相对准确，适合量化分析
6. **免费使用**: Baostock完全免费，无需API密钥

## 代码转换工具

```python
def convert_to_baostock_code(code):
    '''将普通股票代码转换为Baostock格式'''
    if code.startswith('6'):
        return f'sh.{code}'
    elif code.startswith('0') or code.startswith('3'):
        return f'sz.{code}'
    else:
        return code  # 已经是baostock格式或无法识别
```

## 错误处理

```python
import baostock as bs

# 登录
lg = bs.login()
if lg.error_code != '0':
    print(f'Baostock登录失败: {lg.error_msg}')
    # 处理登录失败的情况
    exit(1)

try:
    # 执行查询
    rs = bs.query_history_k_data_plus('sh.600000', 'date,close', start_date='2025-01-01', end_date='2025-01-31')
    if rs.error_code != '0':
        print(f'查询失败: {rs.error_msg}')
    else:
        # 处理数据
        pass
finally:
    # 确保登出
    bs.logout()
```