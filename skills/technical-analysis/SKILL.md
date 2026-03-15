---
name: technical-analysis
description: "股票技术分析，包括趋势分析、形态识别、指标计算、买卖信号检测。使用场景：用户询问技术分析、买卖点、趋势判断、支撑阻力等。"
metadata: { "openclaw": { "emoji": "📊", "requires": { "bins": ["python3"] } } }
---

# 技术分析 Skill (Baostock版本)

基于Baostock数据的股票技术分析工具，支持趋势分析、形态识别、技术指标计算和买卖信号检测。

## 使用场景

✅ **使用此Skill当：**

- "分析股票趋势"
- "识别K线形态"
- "计算技术指标"
- "判断买卖点"
- "寻找支撑阻力位"
- "检测金叉死叉"

## 核心功能

### 1. Baostock数据获取工具函数
```python
import baostock as bs
import pandas as pd
import numpy as np

def get_baostock_data(code, start_date='2025-01-01', end_date='2025-12-31', frequency='d'):
    """
    从Baostock获取股票数据
    """
    # 登录
    lg = bs.login()
    if lg.error_code != '0':
        print(f'Baostock登录失败: {lg.error_msg}')
        return None
    
    # 转换代码格式
    if code.startswith('6'):
        bs_code = f'sh.{code}'
    elif code.startswith('0') or code.startswith('3'):
        bs_code = f'sz.{code}'
    else:
        bs_code = code
    
    # 查询K线数据
    rs = bs.query_history_k_data_plus(bs_code, 
        'date,code,open,high,low,close,volume,amount,turn,pctChg',
        start_date=start_date, end_date=end_date,
        frequency=frequency, adjustflag='3')
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        bs.logout()
        return None
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    
    # 转换数据类型
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    bs.logout()
    return df
```

### 2. 趋势分析
```python
def analyze_trend(df):
    """
    判断趋势方向
    """
    if df.empty or 'close' not in df.columns:
        return {}
    
    # 计算移动平均线
    df['MA5'] = df['close'].rolling(5).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    df['MA60'] = df['close'].rolling(60).mean()
    
    current_close = df['close'].iloc[-1]
    
    # 短期趋势（5日线）
    short_trend = '上涨' if current_close > df['MA5'].iloc[-1] else '下跌'
    
    # 中期趋势（20日线）
    mid_trend = '上涨' if current_close > df['MA20'].iloc[-1] else '下跌'
    
    # 长期趋势（60日线）
    long_trend = '上涨' if current_close > df['MA60'].iloc[-1] else '下跌'
    
    return {
        '短期趋势(MA5)': short_trend,
        '中期趋势(MA20)': mid_trend,
        '长期趋势(MA60)': long_trend,
        '当前价格': current_close,
        'MA5': df['MA5'].iloc[-1],
        'MA20': df['MA20'].iloc[-1],
        'MA60': df['MA60'].iloc[-1]
    }
```

### 3. 技术指标计算
```python
def calculate_indicators(df):
    """
    计算常用技术指标
    """
    if df.empty or 'close' not in df.columns:
        return df
    
    # 确保close是数值类型
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 布林带
    df['BB_Middle'] = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    df['BB_Upper'] = df['BB_Middle'] + 2 * bb_std
    df['BB_Lower'] = df['BB_Middle'] - 2 * bb_std
    
    # 移动平均线
    df['MA5'] = df['close'].rolling(5).mean()
    df['MA10'] = df['close'].rolling(10).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    df['MA30'] = df['close'].rolling(30).mean()
    df['MA60'] = df['close'].rolling(60).mean()
    
    # 成交量均线
    if 'volume' in df.columns:
        df['VMA5'] = df['volume'].rolling(5).mean()
        df['VMA10'] = df['volume'].rolling(10).mean()
    
    return df
```

### 4. 买卖信号生成
```python
def generate_signals(df):
    """
    生成买卖信号
    """
    signals = []
    
    if df.empty:
        return signals
    
    # 确保有足够的计算列
    required_cols = ['MA5', 'MA10', 'MACD', 'MACD_Signal', 'RSI', 'BB_Upper', 'BB_Lower']
    if not all(col in df.columns for col in required_cols):
        return signals
    
    # 金叉信号
    if df['MA5'].iloc[-1] > df['MA10'].iloc[-1] and df['MA5'].iloc[-2] <= df['MA10'].iloc[-2]:
        signals.append('5日线上穿10日线（金叉）')
    
    # 死叉信号
    if df['MA5'].iloc[-1] < df['MA10'].iloc[-1] and df['MA5'].iloc[-2] >= df['MA10'].iloc[-2]:
        signals.append('5日线下穿10日线（死叉）')
    
    # MACD金叉
    if df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1] and df['MACD'].iloc[-2] <= df['MACD_Signal'].iloc[-2]:
        signals.append('MACD金叉')
    
    # MACD死叉
    if df['MACD'].iloc[-1] < df['MACD_Signal'].iloc[-1] and df['MACD'].iloc[-2] >= df['MACD_Signal'].iloc[-2]:
        signals.append('MACD死叉')
    
    # RSI超买超卖
    if df['RSI'].iloc[-1] > 70:
        signals.append('RSI超买（>70）')
    elif df['RSI'].iloc[-1] < 30:
        signals.append('RSI超卖（<30）')
    
    # 布林带突破
    current_close = df['close'].iloc[-1]
    if current_close > df['BB_Upper'].iloc[-1]:
        signals.append('突破布林带上轨')
    elif current_close < df['BB_Lower'].iloc[-1]:
        signals.append('跌破布林带下轨')
    
    # 价格与均线关系
    if current_close > df['MA5'].iloc[-1] and current_close > df['MA10'].iloc[-1] and current_close > df['MA20'].iloc[-1]:
        signals.append('多头排列')
    elif current_close < df['MA5'].iloc[-1] and current_close < df['MA10'].iloc[-1] and current_close < df['MA20'].iloc[-1]:
        signals.append('空头排列')
    
    return signals
```

### 5. 支撑阻力分析
```python
def analyze_support_resistance(df, lookback_period=20):
    """
    分析支撑阻力位
    """
    if df.empty or 'high' not in df.columns or 'low' not in df.columns:
        return {}
    
    recent_df = df.tail(lookback_period)
    
    # 近期高低点
    recent_high = recent_df['high'].max()
    recent_low = recent_df['low'].min()
    current = df['close'].iloc[-1]
    
    result = {
        '当前价格': current,
        '近期高点': recent_high,
        '近期低点': recent_low,
        '距离高点(%)': ((recent_high - current) / current * 100) if current > 0 else 0,
        '距离低点(%)': ((current - recent_low) / current * 100) if current > 0 else 0
    }
    
    # 斐波那契回撤
    if recent_high != recent_low:
        price_range = recent_high - recent_low
        result['斐波那契回撤位'] = {
            '23.6%': recent_high - price_range * 0.236,
            '38.2%': recent_high - price_range * 0.382,
            '50.0%': recent_high - price_range * 0.5,
            '61.8%': recent_high - price_range * 0.618,
            '78.6%': recent_high - price_range * 0.786
        }
    
    return result
```

## 常用分析命令

### 完整技术分析
```bash
python3 -c "
import baostock as bs
import pandas as pd
import numpy as np

# 导入上面定义的函数
def get_baostock_data(code, start_date='2025-01-01', end_date='2025-12-31', frequency='d'):
    lg = bs.login()
    if lg.error_code != '0':
        return None
    
    if code.startswith('6'):
        bs_code = f'sh.{code}'
    elif code.startswith('0') or code.startswith('3'):
        bs_code = f'sz.{code}'
    else:
        bs_code = code
    
    rs = bs.query_history_k_data_plus(bs_code, 
        'date,code,open,high,low,close,volume,amount,turn,pctChg',
        start_date=start_date, end_date=end_date,
        frequency=frequency, adjustflag='3')
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        bs.logout()
        return None
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    bs.logout()
    return df

def calculate_indicators(df):
    if df.empty or 'close' not in df.columns:
        return df
    
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 移动平均线
    df['MA5'] = df['close'].rolling(5).mean()
    df['MA10'] = df['close'].rolling(10).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    
    return df

def analyze_trend(df):
    if df.empty or 'close' not in df.columns:
        return {}
    
    current_close = df['close'].iloc[-1]
    
    short_trend = '上涨' if current_close > df['MA5'].iloc[-1] else '下跌'
    mid_trend = '上涨' if current_close > df['MA20'].iloc[-1] else '下跌'
    
    return {
        '短期趋势(MA5)': short_trend,
        '中期趋势(MA20)': mid_trend,
        '当前价格': current_close,
        'MA5': df['MA5'].iloc[-1],
        'MA20': df['MA20'].iloc[-1]
    }

def generate_signals(df):
    signals = []
    
    if df.empty:
        return signals
    
    required_cols = ['MA5', 'MA10', 'MACD', 'MACD_Signal', 'RSI']
    if not all(col in df.columns for col in required_cols):
        return signals
    
    # 金叉信号
    if df['MA5'].iloc[-1] > df['MA10'].iloc[-1] and df['MA5'].iloc[-2] <= df['MA10'].iloc[-2]:
        signals.append('5日线上穿10日线（金叉）')
    
    # MACD金叉
    if df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1] and df['MACD'].iloc[-2] <= df['MACD_Signal'].iloc[-2]:
        signals.append('MACD金叉')
    
    # RSI超买超卖
    if df['RSI'].iloc[-1] > 70:
        signals.append('RSI超买（>70）')
    elif df['RSI'].iloc[-1] < 30:
        signals.append('RSI超卖（<30）')
    
    return signals

# 主程序
code = '600000'  # 浦发银行
df = get_baostock_data(code, '2025-01-01', '2025-03-15')

if df is not None and not df.empty:
    df = calculate_indicators(df)
    trend = analyze_trend(df)
    signals = generate_signals(df)
    
    print(f'股票: {code}')
    print('趋势分析:')
    for key, value in trend.items():
        print(f'  {key}: {value}')
    
    print('\\n技术信号:')
    if signals:
        for signal in signals:
            print(f'  • {signal}')
    else:
        print('  • 无明显信号')
    
    print('\\n最新指标值:')
    print(f'  收盘价: {df[\"close\"].iloc[-1]:.2f}')
    print(f'  MA5: {df[\"MA5\"].iloc[-1]:.2f}')
    print(f'  MA20: {df[\"MA20\"].iloc[-1]:.2f}')
    print(f'  RSI: {df[\"RSI\"].iloc[-1]:.2f}')
    print(f'  MACD: {df[\"MACD\"].iloc[-1]:.4f}')
else:
    print('获取数据失败')
"
```

### 快速趋势判断
```bash
python3 -c "
import baostock as bs
import pandas as pd

def quick_trend_analysis(code):
    lg = bs.login()
    if lg.error_code != '0':
        return None
    
    if code.startswith('6'):
        bs_code = f'sh.{code}'
    else:
        bs_code = f'sz.{code}'
    
    rs = bs.query_history_k_data_plus(bs_code, 
        'date,close',
        start_date='2025-01-01', end_date='2025-03-15',
        frequency='d', adjustflag='3')
    
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        bs.logout()
        return None
    
    df = pd.DataFrame(data_list, columns=['date', 'close'])
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    
    # 计算移动平均线
    df['MA5'] = df['close'].rolling(5).mean()
    df['MA20'] = df
## ATR（平均真实波幅）分析

### ATR指标计算
```bash
# 使用ATR模块进行分析
python3 -c "
    ATR分析命令示例
    """
    example_code = '''
# ATR分析示例
import sys
sys.path.append('/home/openclaw/.openclaw/workspace')
from skills.technical-analysis.atr_module import atr_analysis
from utils.data_source_manager import get_data_source_manager

# 获取数据
manager = get_data_source_manager()
df = manager.get_stock_data('000001', start_date='2025-01-01', end_date='2025-03-01')

if df is not None:
    # 进行ATR分析
    results = atr_analysis(df, period=14, method='wilder')
    
    print("📊 ATR分析结果:")
"
```
