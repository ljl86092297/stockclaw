# ADX指标学习记录
## 学习时间：2026-03-15 20:52
## 学习目标：掌握ADX指标的计算和应用

## 1. ADX指标基本概念

### 什么是ADX？
ADX（Average Directional Index，平均趋向指数）是衡量趋势强度的技术指标，由Welles Wilder开发。

### 核心组成
1. **+DI（正向指标）** - 上升趋势强度
2. **-DI（负向指标）** - 下降趋势强度  
3. **ADX线** - 整体趋势强度

### 计算公式
```
TR = MAX(High - Low, |High - PrevClose|, |Low - PrevClose|)
+DM = High - PrevHigh (如果>0且>|Low - PrevLow|)
-DM = PrevLow - Low (如果>0且>|High - PrevHigh|)

+DI = 100 * EMA(+DM) / EMA(TR)
-DI = 100 * EMA(-DM) / EMA(TR)
DX = 100 * |(+DI) - (-DI)| / |(+DI) + (-DI)|
ADX = EMA(DX)
```

## 2. ADX指标解读

### 趋势强度判断
- **ADX > 25**：趋势明显
- **ADX > 40**：趋势强劲
- **ADX < 20**：趋势不明显，震荡市
- **ADX < 10**：极度震荡

### 趋势方向判断
- **+DI > -DI**：上升趋势
- **-DI > +DI**：下降趋势
- **+DI与-DI交叉**：趋势转换信号

## 3. 交易信号

### 买入信号
1. **ADX从20以下上升到25以上** + **+DI上穿-DI** = 强烈买入
2. **ADX持续上升** + **价格创新高** = 趋势延续

### 卖出信号
1. **ADX从高位回落** + **-DI上穿+DI** = 卖出
2. **ADX > 40后开始下降** = 趋势可能结束

### 观望信号
1. **ADX < 20** = 震荡市，观望
2. **+DI和-DI纠缠** = 方向不明

## 4. ADX在短线交易中的应用

### 短线优势
1. **过滤震荡市** - ADX<20时避免交易
2. **确认趋势强度** - 只交易ADX>25的股票
3. **识别趋势转换** - +DI/-DI交叉点

### 短线策略
```python
def adx_strategy(adx, plus_di, minus_di):
    if adx < 20:
        return "观望"  # 震荡市
    elif adx > 25 and plus_di > minus_di:
        return "买入"  # 上升趋势
    elif adx > 25 and minus_di > plus_di:
        return "卖出"  # 下降趋势
    else:
        return "持有"
```

## 5. 代码实现

### ADX计算函数
```python
import pandas as pd
import numpy as np

def calculate_adx(df, period=14):
    """
    计算ADX指标
    df: 包含high, low, close的DataFrame
    period: 计算周期，默认14
    """
    # 计算真实波幅(TR)
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = abs(df['high'] - df['close'].shift(1))
    df['low_close'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    
    # 计算方向运动(DM)
    df['up_move'] = df['high'] - df['high'].shift(1)
    df['down_move'] = df['low'].shift(1) - df['low']
    
    df['+DM'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
    df['-DM'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
    
    # 计算平滑值
    df['TR_smooth'] = df['TR'].rolling(window=period).mean()
    df['+DM_smooth'] = df['+DM'].rolling(window=period).mean()
    df['-DM_smooth'] = df['-DM'].rolling(window=period).mean()
    
    # 计算方向指标(DI)
    df['+DI'] = 100 * df['+DM_smooth'] / df['TR_smooth']
    df['-DI'] = 100 * df['-DM_smooth'] / df['TR_smooth']
    
    # 计算方向指数(DX)和ADX
    df['DX'] = 100 * abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])
    df['ADX'] = df['DX'].rolling(window=period).mean()
    
    return df[['+DI', '-DI', 'ADX']].iloc[-1]
```

## 6. 集成到短线交易系统

### 修改短线评分系统
```python
def calculate_short_term_score_with_adx(df):
    """
    包含ADX的短线评分
    """
    score = 0
    
    # 基础技术指标（原有）
    current_price = df['close'].iloc[-1]
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    if current_price > ma5: score += 1
    
    # 成交量
    volume_ratio = df['volume'].iloc[-1] / df['volume'].mean()
    if volume_ratio > 1.5: score += 2
    elif volume_ratio > 1.0: score += 1
    
    # ADX指标（新增）
    adx_data = calculate_adx(df)
    adx = adx_data['ADX']
    plus_di = adx_data['+DI']
    minus_di = adx_data['-DI']
    
    if adx > 25:
        score += 2  # 趋势明显
        if plus_di > minus_di:
            score += 1  # 上升趋势
    elif adx < 20:
        score -= 1  # 震荡市，降低评分
    
    return score, adx_data
```

## 7. 实战应用：云天化ADX分析

### 数据获取
```python
# 获取云天化数据
from utils.data_source_manager import get_data_source_manager
manager = get_data_source_manager()
df = manager.get_stock_data("600096", "2026-02-01", "2026-03-15")

# 计算ADX
adx_result = calculate_adx(df)
print(f"ADX: {adx_result['ADX']:.2f}")
print(f"+DI: {adx_result['+DI']:.2f}")
print(f"-DI: {adx_result['-DI']:.2f}")

# 判断趋势
if adx_result['ADX'] > 25:
    if adx_result['+DI'] > adx_result['-DI']:
        print("趋势：上升趋势明显")
    else:
        print("趋势：下降趋势明显")
else:
    print("趋势：震荡市，趋势不明显")
```

## 8. 学习总结

### 掌握要点
1. ✅ ADX衡量趋势强度，不指示方向
2. ✅ +DI和-DI指示趋势方向
3. ✅ ADX>25为有效趋势，ADX<20为震荡市
4. ✅ 短线交易应优先选择ADX>25的股票

### 系统集成计划
1. 将ADX计算函数添加到 `utils/` 目录
2. 修改短线交易系统的评分算法
3. 在分析报告中增加ADX指标显示
4. 基于ADX优化买入/卖出条件

### 下一步学习
- 结合ADX与其他指标（如MACD、RSI）
- 开发基于ADX的趋势跟踪策略
- 回测ADX策略的历史表现

## 9. 代码文件
- `adx_calculator.py` - ADX计算函数
- `adx_strategy.py` - ADX交易策略
- 集成到 `fast_trader_fixed.py`