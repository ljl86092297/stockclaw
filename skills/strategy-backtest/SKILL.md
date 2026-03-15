---
name: strategy-backtest
description: "股票策略回测，包括策略开发、历史数据回测、绩效评估、参数优化。使用场景：用户需要测试交易策略、评估策略绩效、优化策略参数等。"
metadata: { "openclaw": { "emoji": "🧪", "requires": { "bins": ["python3"] } } }
---

# 策略回测 Skill

股票交易策略回测工具，支持策略开发、历史数据测试、绩效评估和参数优化。

## 使用场景

✅ **使用此Skill当：**

- "测试交易策略"
- "回测策略历史表现"
- "评估策略绩效"
- "优化策略参数"
- "比较不同策略"
- "计算夏普比率、最大回撤"

## 核心功能

### 1. 基础回测框架
```python
class BacktestEngine:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        self.equity_curve = []
        
    def run(self, df, strategy):
        """运行回测"""
        for i in range(len(df)):
            signal = strategy.generate_signal(df.iloc[:i+1])
            price = df.iloc[i]['收盘']
            
            if signal == 'BUY' and self.position == 0:
                # 买入
                self.position = self.capital / price
                self.capital = 0
                self.trades.append({
                    'date': df.iloc[i]['日期'],
                    'action': 'BUY',
                    'price': price,
                    'shares': self.position
                })
                
            elif signal == 'SELL' and self.position > 0:
                # 卖出
                self.capital = self.position * price
                self.trades.append({
                    'date': df.iloc[i]['日期'],
                    'action': 'SELL',
                    'price': price,
                    'shares': self.position
                })
                self.position = 0
            
            # 记录权益曲线
            equity = self.capital + (self.position * price if self.position > 0 else 0)
            self.equity_curve.append(equity)
        
        return self.get_results()
    
    def get_results(self):
        """获取回测结果"""
        final_equity = self.equity_curve[-1] if self.equity_curve else self.initial_capital
        total_return = (final_equity - self.initial_capital) / self.initial_capital * 100
        
        return {
            '初始资金': self.initial_capital,
            '最终权益': final_equity,
            '总收益率': f'{total_return:.2f}%',
            '交易次数': len(self.trades) // 2,
            '交易记录': self.trades
        }
```

### 2. 常见策略模板
```python
# 均线交叉策略
class MACrossStrategy:
    def __init__(self, short_window=5, long_window=20):
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signal(self, df):
        if len(df) < self.long_window:
            return 'HOLD'
        
        df = df.copy()
        df['MA_short'] = df['收盘'].rolling(self.short_window).mean()
        df['MA_long'] = df['收盘'].rolling(self.long_window).mean()
        
        current_short = df['MA_short'].iloc[-1]
        current_long = df['MA_long'].iloc[-1]
        prev_short = df['MA_short'].iloc[-2]
        prev_long = df['MA_long'].iloc[-2]
        
        if current_short > current_long and prev_short <= prev_long:
            return 'BUY'
        elif current_short < current_long and prev_short >= prev_long:
            return 'SELL'
        
        return 'HOLD'

# RSI策略
class RSIStrategy:
    def __init__(self, oversold=30, overbought=70, period=14):
        self.oversold = oversold
        self.overbought = overbought
        self.period = period
    
    def generate_signal(self, df):
        if len(df) < self.period:
            return 'HOLD'
        
        # 计算RSI
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        if current_rsi < self.oversold:
            return 'BUY'
        elif current_rsi > self.overbought:
            return 'SELL'
        
        return 'HOLD'
```

### 3. 绩效评估指标
```python
def calculate_metrics(equity_curve, risk_free_rate=0.03):
    """计算绩效指标"""
    import numpy as np
    
    returns = np.diff(equity_curve) / equity_curve[:-1]
    
    # 总收益率
    total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
    
    # 年化收益率
    annual_return = (1 + total_return) ** (252 / len(equity_curve)) - 1
    
    # 年化波动率
    annual_volatility = np.std(returns) * np.sqrt(252)
    
    # 夏普比率
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
    
    # 最大回撤
    peak = np.maximum.accumulate(equity_curve)
    drawdown = (peak - equity_curve) / peak
    max_drawdown = np.max(drawdown)
    
    # 胜率（假设有交易记录）
    # 这里需要实际的交易盈亏数据
    
    return {
        '总收益率': f'{total_return*100:.2f}%',
        '年化收益率': f'{annual_return*100:.2f}%',
        '年化波动率': f'{annual_volatility*100:.2f}%',
        '夏普比率': f'{sharpe_ratio:.2f}',
        '最大回撤': f'{max_drawdown*100:.2f}%'
    }
```

## 常用回测命令

### 均线交叉策略回测
```bash
python3 -c "
import akshare as ak
import pandas as pd
import numpy as np

# 获取数据
code = '000001'
df = ak.stock_zh_a_hist(symbol=code, period='daily', start_date='20230101', end_date='20241231')

# 创建策略
class MACrossStrategy:
    def __init__(self, short=5, long=20):
        self.short = short
        self.long = long
    
    def generate_signal(self, df):
        if len(df) < self.long:
            return 'HOLD'
        
        df = df.copy()
        df['MA_short'] = df['收盘'].rolling(self.short).mean()
        df['MA_long'] = df['收盘'].rolling(self.long).mean()
        
        current_short = df['MA_short'].iloc[-1]
        current_long = df['MA_long'].iloc[-1]
        prev_short = df['MA_short'].iloc[-2]
        prev_long = df['MA_long'].iloc[-2]
        
        if current_short > current_long and prev_short <= prev_long:
            return 'BUY'
        elif current_short < current_long and prev_short >= prev_long:
            return 'SELL'
        return 'HOLD'

# 运行回测
strategy = MACrossStrategy(short=5, long=20)
engine = BacktestEngine(initial_capital=100000)

results = engine.run(df, strategy)
print('均线交叉策略回测结果:')
for key, value in results.items():
    if key != '交易记录':
        print(f'{key}: {value}')
"
```

### RSI策略回测
```bash
python3 -c "
import akshare as ak
import pandas as pd
import numpy as np

# 获取数据
code = '300166'
df = ak.stock_zh_a_hist(symbol=code, period='daily', start_date='20230101', end_date='20241231')

# 创建策略
class RSIStrategy:
    def __init__(self, oversold=30, overbought=70, period=14):
        self.oversold = oversold
        self.overbought = overbought
        self.period = period
    
    def generate_signal(self, df):
        if len(df) < self.period:
            return 'HOLD'
        
        # 计算RSI
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        if current_rsi < self.oversold:
            return 'BUY'
        elif current_rsi > self.overbought:
            return 'SELL'
        return 'HOLD'

# 运行回测
strategy = RSIStrategy(oversold=30, overbought=70, period=14)
engine = BacktestEngine(initial_capital=100000)

results = engine.run(df, strategy)
print('RSI策略回测结果:')
for key, value in results.items():
    if key != '交易记录':
        print(f'{key}: {value}')
"
```

### 策略参数优化
```bash
python3 -c "
import akshare as ak
import pandas as pd
import numpy as np
from itertools import product

# 获取数据
code = '000001'
df = ak.stock_zh_a_hist(symbol=code, period='daily', start_date='20230101', end_date='20241231')

# 参数网格
short_windows = [3, 5, 8, 10]
long_windows = [20, 30, 50, 60]

best_result = None
best_params = None

for short, long in product(short_windows, long_windows):
    if short >= long:
        continue
    
    # 运行回测
    strategy = MACrossStrategy(short=short, long=long)
    engine = BacktestEngine(initial_capital=100000)
    results = engine.run(df, strategy)
    
    # 提取收益率
    final_equity = results['最终权益']
    return_rate = (final_equity - 100000) / 100000
    
    if best_result is None or return_rate > best_result:
        best_result = return_rate
        best_params = (short, long)

print(f'最佳参数: 短期={best_params[0]}日, 长期={best_params[1]}日')
print(f'最佳收益率: {best_result*100:.2f}%')
"
```

## 安装依赖

```bash
pip install akshare pandas numpy
```

## 注意事项

- 回测结果不代表未来表现
- 考虑交易成本（佣金、印花税）
- 注意过拟合问题
- 使用样本外数据验证
- 结合市场环境分析