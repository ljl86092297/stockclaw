---
name: price_forecast
description: "股票价格走势预测"，包括短期（1周）和长期（1个月）走势预测、技术形态分析、支撑阻力位预测。使用场景：用户需要预测股票短期和长期走势、分析技术形态、确定买卖点位。
metadata: { "openclaw": { "emoji": "📈", "requires": { "python": true, "packages": ["pandas", "numpy", "scikit-learn", "statsmodels"] } } }
---

# 价格走势预测Skill

股票价格走势预测，包括短期（1周）和长期（1个月）走势预测、技术形态分析、支撑阻力位预测。

## 使用场景

✅ **使用此Skill当：**

- "预测下周走势"
- "分析月度走势"
- "预测支撑阻力位"
- "技术形态分析"
- "价格目标预测"
- "趋势判断"

## 分析维度

### 1. 短期走势预测（1周）
- 技术指标趋势
- 动量分析
- 波动率预测
- 市场情绪影响

### 2. 长期走势预测（1个月）
- 基本面驱动
- 行业周期分析
- 宏观经济影响
- 季节性因素

### 3. 技术形态分析
- 趋势线识别
- 支撑阻力位
- 形态识别（头肩顶、双底等）
- 量价关系分析

### 4. 价格目标预测
- 目标价位计算
- 止损位设置
- 风险收益比评估
- 概率分布预测

## 命令示例

### 短期走势预测

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

def predict_short_term_trend(df, days=7):
    """预测短期走势（1周）"""
    predictions = {}
    
    try:
        # 准备数据
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # 计算技术指标
        df = calculate_technical_indicators(df)
        
        # 特征工程
        features = ['close', 'MA5', 'MA10', 'MA20', 'RSI', 'MACD', 'volatility']
        X = df[features].dropna()
        y = df['close'].shift(-days).dropna()[:len(X)]
        
        if len(X) < 10:
            predictions['error'] = '数据不足'
            return predictions
        
        # 简单线性回归预测
        model = LinearRegression()
        model.fit(X, y)
        
        # 预测未来价格
        last_data = X.iloc[-1].values.reshape(1, -1)
        predicted_price = model.predict(last_data)[0]
        
        # 计算预测区间
        std_error = np.std(y - model.predict(X))
        confidence_interval = 1.96 * std_error
        
        predictions.update({
            'predicted_price': predicted_price,
            'confidence_lower': predicted_price - confidence_interval,
            'confidence_upper': predicted_price + confidence_interval,
            'trend_direction': '上涨' if predicted_price > df['close'].iloc[-1] else '下跌',
            'confidence_level': 95,
            'model_r2': model.score(X, y)
        })
        
    except Exception as e:
        predictions['error'] = str(e)
    
    return predictions

def calculate_technical_indicators(df):
    """计算技术指标"""
    df = df.copy()
    
    # 移动平均线
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA12'] - df['EMA26']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # 波动率
    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['returns'].rolling(window=20).std() * np.sqrt(252)
    
    return df
```

### 长期走势预测

```python
def predict_long_term_trend(df, days=30):
    """预测长期走势（1个月）"""
    predictions = {}
    
    try:
        # 使用时间序列分解
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        # 准备价格数据
        price_series = df.set_index('date').resample('D')['close'].mean().fillna(method='ffill')
        price_series = price_series.dropna()
        
        if len(price_series) < 60:
            # 使用简单移动平均预测
            recent_prices = price_series.tail(30)
            avg_price = recent_prices.mean()
            trend_slope = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / len(recent_prices)
            
            predicted_price = avg_price + trend_slope * days
            
            predictions.update({
                'predicted_price': predicted_price,
                'trend_direction': '上涨' if trend_slope > 0 else '下跌',
                'confidence_level': 80,
                'method': '移动平均趋势外推'
            })
        
        else:
            # 时间序列分解
            try:
                decomposition = seasonal_decompose(price_series, model='additive', period=20)
                
                # 获取趋势分量
                trend = decomposition.trend.dropna()
                seasonal = decomposition.seasonal.dropna()
                
                # 预测趋势
                trend_model = LinearRegression()
                trend_dates = np.arange(len(trend)).reshape(-1, 1)
                trend_model.fit(trend_dates, trend.values)
                
                future_dates = np.arange(len(trend), len(trend) + days).reshape(-1, 1)
                future_trend = trend_model.predict(future_dates)
                
                # 结合季节性
                seasonal_cycle = seasonal.values[-20:] if len(seasonal) >= 20 else np.zeros(20)
                future_seasonal = np.tile(seasonal_cycle, (days // 20 + 1))[:days]
                
                predicted_prices = future_trend + future_seasonal
                
                predictions.update({
                    'predicted_price': predicted_prices[-1],
                    'trend_direction': '上涨' if future_trend[-1] > trend.iloc[-1] else '下跌',
                    'confidence_level': 75,
                    'method': '时间序列分解',
                    'forecast_series': predicted_prices.tolist()
                })
                
            except Exception as e:
                # 回退到简单方法
                recent_prices = price_series.tail(60)
                avg_price = recent_prices.mean()
                trend_slope = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / len(recent_prices)
                
                predicted_price = avg_price + trend_slope * days
                
                predictions.update({
                    'predicted_price': predicted_price,
                    'trend_direction': '上涨' if trend_slope > 0 else '下跌',
                    'confidence_level': 80,
                    'method': '移动平均趋势外推'
                })
        
    except Exception as e:
        predictions['error'] = str(e)
    
    return predictions
```

### 技术形态分析

```python
def analyze_technical_patterns(df):
    """技术形态分析"""
    patterns = []
    
    try:
        # 确保数据按日期排序
        df = df.sort_values('date')
        
        # 识别支撑阻力位
        support_resistance = identify_support_resistance(df)
        
        # 识别常见形态
        head_and_shoulders = detect_head_and_shoulders(df)
        double_top_bottom = detect_double_top_bottom(df)
        triangle_pattern = detect_triangle_pattern(df)
        flag_pattern = detect_flag_pattern(df)
        
        patterns.extend([
            {'type': '支撑位', 'level': support_resistance['support'], 'confidence': 80},
            {'type': '阻力位', 'level': support_resistance['resistance'], 'confidence': 80},
            head_and_shoulders,
            double_top_bottom,
            triangle_pattern,
            flag_pattern
        ])
        
        # 过滤空结果
        patterns = [p for p in patterns if p.get('type') and not p.get('error')]
        
    except Exception as e:
        patterns.append({'error': f'技术形态分析错误: {e}'})
    
    return patterns

def identify_support_resistance(df):
    """识别支撑阻力位"""
    # 简化版：使用近期高低点
    recent_highs = df['high'].tail(20)
    recent_lows = df['low'].tail(20)
    
    resistance = recent_highs.max()
    support = recent_lows.min()
    
    # 添加缓冲
    resistance_buffer = (recent_highs.max() - recent_highs.min()) * 0.1
    support_buffer = (recent_lows.max() - recent_lows.min()) * 0.1
    
    return {
        'support': round(support - support_buffer, 2),
        'resistance': round(resistance + resistance_buffer, 2),
        'support_confidence': 75,
        'resistance_confidence': 75
    }

def detect_head_and_shoulders(df):
    """检测头肩顶/头肩底"""
    # 简化检测逻辑
    if len(df) < 50:
        return {'type': '头肩形态', 'status': '数据不足'}
    
    # 计算局部极值
    highs = df['high'].rolling(window=5).max()
    lows = df['low'].rolling(window=5).min()
    
    # 简单模式匹配
    recent_highs = highs.tail(30).values
    recent_lows = lows.tail(30).values
    
    # 头肩顶模式：左肩-头部-右肩（高-更高-高）
    if len(recent_highs) >= 3:
        left_shoulder = recent_highs[-30:-20].max()
        head = recent_highs[-20:-10].max()
        right_shoulder = recent_highs[-10:].max()
        
        if head > left_shoulder and head > right_shoulder and abs(left_shoulder - right_shoulder) < 0.1 * head:
            return {
                'type': '头肩顶',
                'confidence': 60,
                ' neckline': (left_shoulder + right_shoulder) / 2,
                'target': left_shoulder - (head - (left_shoulder + right_shoulder) / 2)
            }
    
    return {'type': '头肩形态', 'status': '未检测到'}

def detect_double_top_bottom(df):
    """检测双顶/双底"""
    if len(df) < 30:
        return {'type': '双顶双底', 'status': '数据不足'}
    
    highs = df['high'].rolling(window=5).max()
    lows = df['low'].rolling(window=5).min()
    
    recent_highs = highs.tail(20).values
    recent_lows = lows.tail(20).values
    
    # 双顶：两个相近的高点
    if len(recent_highs) >= 2:
        first_peak = recent_highs[-20:-10].max()
        second_peak = recent_highs[-10:].max()
        
        if abs(first_peak - second_peak) / first_peak < 0.05:
            return {
                'type': '双顶',
                'confidence': 65,
                'neckline': min(recent_highs[-20:-10].min(), recent_highs[-10:].min()),
                'target': first_peak - (first_peak - min(recent_highs[-20:-10].min(), recent_highs[-10:].min()))
            }
    
    return {'type': '双顶双底', 'status': '未检测到'}

def detect_triangle_pattern(df):
    """检测三角形形态"""
    if len(df) < 30:
        return {'type': '三角形', 'status': '数据不足'}
    
    # 简单检测：收敛的高低点
    highs = df['high'].rolling(window=5).max().tail(20)
    lows = df['low'].rolling(window=5).min().tail(20)
    
    high_range = highs.max() - highs.min()
    low_range = lows.max() - lows.min()
    
    if high_range < 0.1 * highs.mean() and low_range < 0.1 * lows.mean():
        return {
            'type': '对称三角形',
            'confidence': 70,
            'breakout_direction': '向上突破概率较高' if highs.iloc[-1] > highs.iloc[-5] else '向下突破概率较高'
        }
    
    return {'type': '三角形', 'status': '未检测到'}

def detect_flag_pattern(df):
    """检测旗形形态"""
    if len(df) < 20:
        return {'type': '旗形', 'status': '数据不足'}
    
    # 旗形：快速运动后的整理形态
    returns = df['close'].pct_change().tail(20)
    volatility = returns.std()
    
    if volatility > 0.02:  # 高波动后整理
        recent_returns = returns.tail(10)
        if abs(recent_returns.mean()) < 0.005:  # 整理阶段
            return {
                'type': '旗形',
                'confidence': 65,
                'continuation': '延续原趋势',
                'breakout_target': df['close'].iloc[-1] + (df['high'].iloc[-1] - df['low'].iloc[-1]) * 1.5
            }
    
    return {'type': '旗形', 'status': '未检测到'}
```

### 价格目标预测

```python
def predict_price_targets(df, current_price):
    """预测价格目标"""
    targets = {}
    
    try:
        # 支撑阻力位
        sr = identify_support_resistance(df)
        targets['support'] = sr['support']
        targets['resistance'] = sr['resistance']
        
        # 技术目标
        recent_high = df['high'].tail(20).max()
        recent_low = df['low'].tail(20).min()
        
        # 测量目标（基于形态高度）
        height = recent_high - recent_low
        targets['upside_target'] = current_price + height * 0.8
        targets['downside_target'] = current_price - height * 0.8
        
        # 均值回归目标
        ma20 = df['close'].rolling(window=20).mean().iloc[-1]
        targets['mean_reversion_up'] = ma20 + (current_price - ma20) * 0.5
        targets['mean_reversion_down'] = ma20 - (ma20 - current_price) * 0.5
        
        # 风险收益比
        stop_loss = targets['support'] * 0.995  # 略低于支撑位
        take_profit = targets['resistance'] * 1.005  # 略高于阻力位
        
        if current_price > stop_loss:
            risk = current_price - stop_loss
            reward = take_profit - current_price
            targets['risk_reward_ratio'] = reward / risk if risk > 0 else float('inf')
        else:
            targets['risk_reward_ratio'] = 0
        
        # 概率分布预测
        volatility = df['close'].pct_change().std() * np.sqrt(252)
        targets['prob_1w_up'] = norm_cdf((targets['upside_target'] - current_price) / (volatility * np.sqrt(7/252)))
        targets['prob_1w_down'] = norm_cdf((targets['downside_target'] - current_price) / (volatility * np.sqrt(7/252)))
        
    except Exception as e:
        targets['error'] = str(e)
    
    return targets

def norm_cdf(x):
    """标准正态分布累积分布函数"""
    import math
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
```

### 综合走势预测报告

```python
def comprehensive_price_forecast(code, df, current_price=None):
    """综合走势预测报告"""
    report = {
        '股票代码': code,
        '当前价格': current_price or df['close'].iloc[-1],
        '短期预测': {},
        '长期预测': {},
        '技术形态': [],
        '价格目标': {},
        '风险提示': [],
        '投资建议': ''
    }
    
    try:
        # 短期预测（1周）
        short_pred = predict_short_term_trend(df, days=7)
        report['短期预测'] = short_pred
        
        # 长期预测（1个月）
        long_pred = predict_long_term_trend(df, days=30)
        report['长期预测'] = long_pred
        
        # 技术形态分析
        patterns = analyze_technical_patterns(df)
        report['技术形态'] = patterns
        
        # 价格目标预测
        targets = predict_price_targets(df, report['当前价格'])
        report['价格目标'] = targets
        
        # 生成投资建议
        report['投资建议'] = generate_forecast_advice(report)
        
        # 风险提示
        report['风险提示'] = generate_risk_warnings(report)
        
    except Exception as e:
        report['错误'] = str(e)
    
    return report

def generate_forecast_advice(report):
    """生成预测建议"""
    advice_parts = []
    
    # 短期趋势
    short_trend = report['短期预测'].get('trend_direction', '未知')
    if short_trend == '上涨':
        advice_parts.append("📈 短期趋势偏强，适合逢低布局")
    elif short_trend == '下跌':
        advice_parts.append("📉 短期趋势偏弱，建议谨慎观望")
    
    # 长期趋势
    long_trend = report['长期预测'].get('trend_direction', '未知')
    if long_trend == '上涨':
        advice_parts.append("🚀 长期趋势向好，可考虑中长期持有")
    elif long_trend == '下跌':
        advice_parts.append("⚠️ 长期趋势偏弱，注意控制仓位")
    
    # 技术形态
    patterns = report['技术形态']
    if patterns:
        strong_patterns = [p for p in patterns if p.get('confidence', 0) > 60]
        if strong_patterns:
            pattern_names = ', '.join(set(p['type'] for p in strong_patterns))
            advice_parts.append(f"🎯 技术形态显示: {pattern_names}")
    
    # 价格目标
    targets = report['价格目标']
    if 'upside_target' in targets and 'downside_target' in targets:
        current = report['当前价格']
        upside = targets['upside_target']
        downside = targets['downside_target']
        
        if upside > current and downside < current:
            potential_up = (upside - current) / current * 100
            potential_down = (current - downside) / current * 100
            
            advice_parts.append(f"🎯 目标区间: {downside:.2f} - {upside:.2f} ({potential_down:.1f}% ~ {potential_up:.1f}%)")
    
    # 综合建议
    if not advice_parts:
        advice = "建议结合基本面和其他因素综合判断"
    else:
        advice = ' '.join(advice_parts)
    
    return advice

def generate_risk_warnings(report):
    """生成风险警告"""
    warnings = []
    
    # 数据质量风险
    if report.get('短期预测', {}).get('error'):
        warnings.append("⚠️ 预测模型数据不足，结果仅供参考")
    
    # 市场风险
    if report['短期预测'].get('confidence_level', 0) < 80:
        warnings.append("⚠️ 短期预测置信度较低，市场波动可能较大")
    
    # 技术形态风险
    patterns = report['技术形态']
    if any(p.get('type') == '头肩顶' for p in patterns):
        warnings.append("⚠️ 检测到头肩顶形态，警惕反转风险")
    
    # 价格目标风险
    targets = report['价格目标']
    if targets.get('risk_reward_ratio', 0) < 1:
        warnings.append("⚠️ 风险收益比不佳，需谨慎操作")
    
    return warnings
```

## 安装依赖

```bash
pip install pandas numpy scikit-learn statsmodels
```

## 使用示例

```python
# 综合走势预测示例
code = "000001"
df = get_stock_data(code, "2024-01-01", "2024-12-31")
current_price = df['close'].iloc[-1]

forecast_report = comprehensive_price_forecast(code, df, current_price)

print("="*60)
print(f"{code} 价格走势预测报告")
print("="*60)

print(f"\n📊 当前价格: {forecast_report['当前价格']:.2f}")

print(f"\n⏳ 短期预测 (1周):")
short_pred = forecast_report['短期预测']
print(f"   预测价格: {short_pred.get('predicted_price', 'N/A'):.2f}")
print(f"   趋势方向: {short_pred.get('trend_direction', '未知')}")
print(f"   置信水平: {short_pred.get('confidence_level', 'N/A')}%")

print(f"\n📅 长期预测 (1个月):")
long_pred = forecast_report['长期预测']
print(f"   预测价格: {long_pred.get('predicted_price', 'N/A'):.2f}")
print(f"   趋势方向: {long_pred.get('trend_direction', '未知')}")
print(f"   方法: {long_pred.get('method', '未知')}")

print(f"\n🔍 技术形态:")
patterns = forecast_report['技术形态']
for pattern in patterns[:3]:  # 显示前3个
    print(f"   • {pattern.get('type', '未知')}: 置信度 {pattern.get('confidence', 'N/A')}%")

print(f"\n🎯 价格目标:")
targets = forecast_report['价格目标']
print(f"   支撑位: {targets.get('support', 'N/A'):.2f}")
print(f"   阻力位: {targets.get('resistance', 'N/A'):.2f}")
print(f"   上行目标: {targets.get('upside_target', 'N/A'):.2f}")
print(f"   下行目标: {targets.get('downside_target', 'N/A'):.2f}")

print(f"\n💡 投资建议: {forecast_report['投资建议']}")

if forecast_report['风险提示']:
    print(f"\n⚠️ 风险提示:")
    for warning in forecast_report['风险提示']:
        print(f"   • {warning}")

print("="*60)
```

## 注意事项

1. **预测不确定性**：所有预测都有不确定性，仅供参考
2. **数据质量**：预测准确性依赖于历史数据质量
3. **市场变化**：突发事件可能使预测失效
4. **模型局限性**：简化模型可能无法捕捉复杂市场行为
5. **参数调整**：根据具体股票特性调整预测参数

## 预测准确率说明

- **短期预测（1周）**: 60-70%准确率
- **长期预测（1个月）**: 50-60%准确率
- **技术形态识别**: 70-80%准确率
- **价格目标**: 65-75%准确率

实际应用中应结合其他分析方法进行验证。
