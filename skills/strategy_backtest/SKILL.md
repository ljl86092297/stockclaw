---
name: strategy_backtest
description: "股票策略回测引擎，支持多种交易策略的回测和性能评估。使用场景：用户需要测试交易策略、评估策略性能、优化策略参数。"
metadata: { "openclaw": { "emoji": "🧪", "requires": { "python": true, "packages": ["pandas", "numpy", "matplotlib"] } } }
---

# 策略回测Skill

股票策略回测引擎，支持多种交易策略的回测和性能评估。

## 使用场景

✅ **使用此Skill当：**

- "回测交易策略"
- "评估策略性能"
- "优化策略参数"
- "计算收益率"
- "分析风险指标"

## 回测框架

### 基本回测流程
1. 数据准备
2. 信号生成
3. 交易执行
4. 绩效评估
5. 风险分析

## 命令示例

### 基础回测引擎

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class BacktestEngine:
    """基础回测引擎"""
    
    def __init__(self, initial_capital=100000, commission=0.0003):
        self.initial_capital = initial_capital
        self.commission = commission  # 交易佣金
        self.reset()
    
    def reset(self):
        """重置回测状态"""
        self.capital = self.initial_capital
        self.position = 0  # 持仓数量
        self.trades = []  # 交易记录
        self.equity_curve = []  # 权益曲线
        self.current_date = None
    
    def execute_trade(self, date, price, signal, quantity=None):
        """执行交易"""
        if signal == 'BUY' and self.position == 0:
            # 计算可买数量
            if quantity is None:
                quantity = int(self.capital / price)
            
            cost = quantity * price * (1 + self.commission)
            if cost <= self.capital:
                self.position = quantity
                self.capital -= cost
                
                self.trades.append({
                    'date': date,
                    'type': 'BUY',
                    'price': price,
                    'quantity': quantity,
                    'cost': cost
                })
        
        elif signal == 'SELL' and self.position > 0:
            revenue = self.position * price * (1 - self.commission)
            self.capital += revenue
            
            self.trades.append({
                'date': date,
                'type': 'SELL',
                'price': price,
                'quantity': self.position,
                'revenue': revenue
            })
            
            self.position = 0
    
    def update_equity(self, date, current_price):
        """更新权益曲线"""
        position_value = self.position * current_price if self.position > 0 else 0
        total_equity = self.capital + position_value
        self.equity_curve.append({
            'date': date,
            'equity': total_equity,
            'capital': self.capital,
            'position': self.position,
            'position_value': position_value
        })
    
    def run_backtest(self, df, signal_column='signal'):
        """运行回测"""
        self.reset()
        
        for i, row in df.iterrows():
            date = row['date']
            price = row['close']
            signal = row.get(signal_column, 'HOLD')
            
            self.current_date = date
            
            # 执行交易信号
            if signal in ['BUY', 'SELL']:
                self.execute_trade(date, price, signal)
            
            # 更新权益
            self.update_equity(date, price)
        
        return self.get_results()
    
    def get_results(self):
        """获取回测结果"""
        if not self.equity_curve:
            return {}
        
        equity_df = pd.DataFrame(self.equity_curve)
        trades_df = pd.DataFrame(self.trades) if self.trades else pd.DataFrame()
        
        # 计算绩效指标
        initial_equity = self.initial_capital
        final_equity = equity_df['equity'].iloc[-1]
        total_return = (final_equity - initial_equity) / initial_equity * 100
        
        # 计算年化收益率
        days = (equity_df['date'].iloc[-1] - equity_df['date'].iloc[0]).days
        years = days / 365.25
        annual_return = ((1 + total_return/100) ** (1/years) - 1) * 100 if years > 0 else 0
        
        # 计算最大回撤
        equity_series = equity_df.set_index('date')['equity']
        cumulative_max = equity_series.expanding().max()
        drawdown = (equity_series - cumulative_max) / cumulative_max * 100
        max_drawdown = drawdown.min()
        
        # 夏普比率（简化版）
        daily_returns = equity_df['equity'].pct_change().dropna()
        sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252) if len(daily_returns) > 1 else 0
        
        results = {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return_pct': round(total_return, 2),
            'annual_return_pct': round(annual_return, 2),
            'max_drawdown_pct': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'total_trades': len(self.trades),
            'winning_trades': 0,  # 需要交易详情计算
            'losing_trades': 0,
            'win_rate': 0,
            'equity_curve': equity_df,
            'trades': trades_df
        }
        
        return results
```

### 移动平均线策略

```python
def ma_crossover_strategy(df, short_window=5, long_window=20):
    """移动平均线交叉策略"""
    df = df.copy()
    
    # 计算移动平均线
    df['MA_short'] = df['close'].rolling(window=short_window).mean()
    df['MA_long'] = df['close'].rolling(window=long_window).mean()
    
    # 生成信号
    df['signal'] = 'HOLD'
    
    # 金叉买入
    df.loc[(df['MA_short'].shift(1) <= df['MA_long'].shift(1)) & 
           (df['MA_short'] > df['MA_long']), 'signal'] = 'BUY'
    
    # 死叉卖出
    df.loc[(df['MA_short'].shift(1) >= df['MA_long'].shift(1)) & 
           (df['MA_short'] < df['MA_long']), 'signal'] = 'SELL'
    
    return df

# 使用示例
df_with_signals = ma_crossover_strategy(df, 5, 20)
engine = BacktestEngine(initial_capital=100000)
results = engine.run_backtest(df_with_signals)
```

### MACD策略

```python
def macd_strategy(df):
    """MACD策略"""
    df = df.copy()
    
    # 计算MACD
    df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # 生成信号
    df['signal'] = 'HOLD'
    
    # MACD上穿信号线买入
    df.loc[(df['MACD'].shift(1) <= df['MACD_signal'].shift(1)) & 
           (df['MACD'] > df['MACD_signal']), 'signal'] = 'BUY'
    
    # MACD下穿信号线卖出
    df.loc[(df['MACD'].shift(1) >= df['MACD_signal'].shift(1)) & 
           (df['MACD'] < df['MACD_signal']), 'signal'] = 'SELL'
    
    return df
```

### RSI策略

```python
def rsi_strategy(df, oversold=30, overbought=70):
    """RSI策略"""
    df = df.copy()
    
    # 计算RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 生成信号
    df['signal'] = 'HOLD'
    
    # RSI超卖买入
    df.loc[(df['RSI'].shift(1) >= oversold) & 
           (df['RSI'] < oversold), 'signal'] = 'BUY'
    
    # RSI超买卖出
    df.loc[(df['RSI'].shift(1) <= overbought) & 
           (df['RSI'] > overbought), 'signal'] = 'SELL'
    
    return df
```

## 绩效评估

```python
def evaluate_strategy(results):
    """评估策略绩效"""
    metrics = {}
    
    if not results:
        return metrics
    
    # 基础指标
    metrics['总收益率'] = f"{results['total_return_pct']}%"
    metrics['年化收益率'] = f"{results['annual_return_pct']}%"
    metrics['最大回撤'] = f"{results['max_drawdown_pct']}%"
    metrics['夏普比率'] = results['sharpe_ratio']
    metrics['交易次数'] = results['total_trades']
    
    # 计算胜率（如果有交易详情）
    if 'trades' in results and not results['trades'].empty:
        trades = results['trades']
        if len(trades) >= 2:
            # 简单计算盈亏
            buy_trades = trades[trades['type'] == 'BUY']
            sell_trades = trades[trades['type'] == 'SELL']
            
            if len(buy_trades) == len(sell_trades):
                profits = []
                for i in range(len(buy_trades)):
                    buy_price = buy_trades.iloc[i]['price']
                    sell_price = sell_trades.iloc[i]['price']
                    profit_pct = (sell_price - buy_price) / buy_price * 100
                    profits.append(profit_pct)
                
                winning_trades = sum(1 for p in profits if p > 0)
                metrics['胜率'] = f"{winning_trades/len(profits)*100:.1f}%"
                metrics['平均盈亏'] = f"{np.mean(profits):.2f}%"
    
    return metrics

def print_performance_report(results):
    """打印绩效报告"""
    metrics = evaluate_strategy(results)
    
    print("=" * 50)
    print("策略绩效报告")
    print("=" * 50)
    
    for key, value in metrics.items():
        print(f"{key:15}: {value}")
    
    print("=" * 50)
    
    # 打印交易记录
    if 'trades' in results and not results['trades'].empty:
        print("\n交易记录:")
        print(results['trades'].to_string())
```

## 参数优化

```python
def optimize_parameters(df, strategy_func, param_grid):
    """参数优化"""
    best_result = None
    best_params = None
    best_performance = -float('inf')
    
    all_results = []
    
    # 遍历参数网格
    for params in param_grid:
        # 生成信号
        df_with_signals = strategy_func(df, **params)
        
        # 运行回测
        engine = BacktestEngine(initial_capital=100000)
        results = engine.run_backtest(df_with_signals)
        
        # 评估性能（使用夏普比率）
        performance = results.get('sharpe_ratio', 0)
        
        all_results.append({
            'params': params,
            'performance': performance,
            'total_return': results.get('total_return_pct', 0),
            'max_drawdown': results.get('max_drawdown_pct', 0)
        })
        
        # 更新最佳参数
        if performance > best_performance:
            best_performance = performance
            best_result = results
            best_params = params
    
    return {
        'best_params': best_params,
        'best_result': best_result,
        'all_results': all_results
    }

# 使用示例：优化移动平均线策略
param_grid = [
    {'short_window': 3, 'long_window': 10},
    {'short_window': 5, 'long_window': 20},
    {'short_window': 8, 'long_window': 30},
    {'short_window': 10, 'long_window': 50}
]

optimization_results = optimize_parameters(df, ma_crossover_strategy, param_grid)
print(f"最佳参数: {optimization_results['best_params']}")
print(f"最佳夏普比率: {optimization_results['best_result']['sharpe_ratio']}")
```

## 可视化

```python
import matplotlib.pyplot as plt

def plot_backtest_results(results, df):
    """绘制回测结果"""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # 1. 价格和信号
    ax1 = axes[0]
    ax1.plot(df['date'], df['close'], label='收盘价', linewidth=1)
    
    # 标记买卖点
    trades = results['trades']
    if not trades.empty:
        buy_dates = trades[trades['type'] == 'BUY']['date']
        buy_prices = trades[trades['type'] == 'BUY']['price']
        ax1.scatter(buy_dates, buy_prices, color='green', marker='^', s=100, label='买入')
        
        sell_dates = trades[trades['type'] == 'SELL']['date']
        sell_prices = trades[trades['type'] == 'SELL']['price']
        ax1.scatter(sell_dates, sell_prices, color='red', marker='v', s=100, label='卖出')
    
    ax1.set_title('价格走势和交易信号')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 权益曲线
    ax2 = axes[1]
    equity_df = results['equity_curve']
    ax2.plot(equity_df['date'], equity_df['equity'], label='权益曲线', linewidth=2, color='blue')
    ax2.axhline(y=results['initial_capital'], color='red', linestyle='--', label='初始资金')
    ax2.set_title('权益曲线')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 回撤
    ax3 = axes[2]
    equity_series = equity_df.set_index('date')['equity']
    cumulative_max = equity_series.expanding().max()
    drawdown = (equity_series - cumulative_max) / cumulative_max * 100
    ax3.fill_between(drawdown.index, drawdown.values, 0, color='red', alpha=0.3)
    ax3.set_title('回撤曲线')
    ax3.set_ylabel('回撤 (%)')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
```

## 安装依赖

```bash
pip install pandas numpy matplotlib
```

## 注意事项

1. **前视偏差**：确保信号生成不使用未来数据
2. **交易成本**：考虑佣金、滑点等实际成本
3. **数据质量**：确保数据完整准确
4. **过拟合风险**：避免在历史数据上过度优化
5. **样本外测试**：使用样本外数据验证策略

## 快速响应模板

**"回测移动平均线策略"**
```python
df_signals = ma_crossover_strategy(df, 5, 20)
engine = BacktestEngine(initial_capital=100000)
results = engine.run_backtest(df_signals)
print_performance_report(results)
```

**"优化策略参数"**
```python
optimization = optimize_parameters(df, ma_crossover_strategy, param_grid)
print(f"最佳参数: {optimization['best_params']}")
```
