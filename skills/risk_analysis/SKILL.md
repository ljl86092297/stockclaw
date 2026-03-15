---
name: risk_analysis
description: "股票风险分析，包括市场风险、个股风险、行业风险、财务风险、流动性风险等。使用场景：用户需要评估投资风险、识别潜在风险因素、进行风险控制。"
metadata: { "openclaw": { "emoji": "⚠️", "requires": { "python": true, "packages": ["pandas", "numpy", "scipy"] } } }
---

# 风险分析Skill

股票风险分析，包括市场风险、个股风险、行业风险、财务风险、流动性风险等。

## 使用场景

✅ **使用此Skill当：**

- "评估投资风险"
- "识别风险因素"
- "风险控制建议"
- "波动率分析"
- "最大回撤分析"
- "VaR风险值计算"

## 分析维度

### 1. 市场风险
- 系统性风险
- 宏观经济风险
- 政策风险
- 行业周期风险

### 2. 个股风险
- 财务风险
- 经营风险
- 管理风险
- 合规风险

### 3. 流动性风险
- 交易量风险
- 换手率风险
- 大单冲击成本
- 市场深度分析

### 4. 波动率风险
- 历史波动率
- 隐含波动率
- 波动率聚类
- 波动率预测

### 5. 极端风险
- 尾部风险
- 黑天鹅事件
- 压力测试
- 情景分析

## 命令示例

### 波动率分析

```python
import pandas as pd
import numpy as np
from scipy.stats import norm

def analyze_volatility(df):
    """波动率分析"""
    risk_metrics = {}
    
    try:
        # 计算历史波动率
        returns = df['close'].pct_change().dropna()
        
        if len(returns) < 10:
            risk_metrics['error'] = '数据不足'
            return risk_metrics
        
        # 日波动率
        daily_vol = returns.std()
        annual_vol = daily_vol * np.sqrt(252)
        
        # 波动率聚类分析
        rolling_vol_20 = returns.rolling(window=20).std() * np.sqrt(252)
        rolling_vol_60 = returns.rolling(window=60).std() * np.sqrt(252)
        
        # 波动率状态
        current_vol = rolling_vol_20.iloc[-1]
        long_term_avg = rolling_vol_60.mean()
        
        vol_state = '高波动' if current_vol > long_term_avg * 1.5 else \
                   '低波动' if current_vol < long_term_avg * 0.7 else '正常波动'
        
        risk_metrics.update({
            'daily_volatility': round(daily_vol * 100, 2),
            'annual_volatility': round(annual_vol * 100, 2),
            'current_vol_state': vol_state,
            'volatility_ratio': round(current_vol / long_term_avg, 2),
            'volatility_trend': '上升' if rolling_vol_20.iloc[-1] > rolling_vol_20.iloc[-5] else '下降',
            'max_drawdown': calculate_max_drawdown(df)
        })
        
    except Exception as e:
        risk_metrics['error'] = str(e)
    
    return risk_metrics

def calculate_max_drawdown(df):
    """计算最大回撤"""
    try:
        equity_curve = df['close'].cummax()
        drawdown = (df['close'] - equity_curve) / equity_curve * 100
        max_drawdown = drawdown.min()
        return round(max_drawdown, 2)
    except:
        return 0.0
```

### VaR风险值计算

```python
def calculate_var(df, confidence_level=0.95, holding_period=1):
    """计算VaR（风险价值）"""
    risk_metrics = {}
    
    try:
        returns = df['close'].pct_change().dropna()
        
        if len(returns) < 30:
            risk_metrics['error'] = '数据不足'
            return risk_metrics
        
        # 历史模拟法
        sorted_returns = np.sort(returns.values)
        var_index = int(len(sorted_returns) * (1 - confidence_level))
        historical_var = -sorted_returns[var_index]
        
        # 参数法（正态分布）
        mean_return = returns.mean()
        std_return = returns.std()
        parametric_var = -(mean_return + norm.ppf(confidence_level) * std_return)
        
        # 蒙特卡洛模拟（简化版）
        simulated_returns = np.random.normal(mean_return, std_return, 10000)
        mc_var = -np.percentile(simulated_returns, (1 - confidence_level) * 100)
        
        risk_metrics.update({
            'historical_var': round(historical_var * 100, 2),
            'parametric_var': round(parametric_var * 100, 2),
            'monte_carlo_var': round(mc_var * 100, 2),
            'confidence_level': confidence_level,
            'holding_period_days': holding_period,
            'expected_shortfall': calculate_expected_shortfall(returns, confidence_level)
        })
        
    except Exception as e:
        risk_metrics['error'] = str(e)
    
    return risk_metrics

def calculate_expected_shortfall(returns, confidence_level=0.95):
    """计算期望短缺（ES）"""
    try:
        sorted_returns = np.sort(returns.values)
        var_index = int(len(sorted_returns) * (1 - confidence_level))
        tail_losses = sorted_returns[:var_index]
        
        if len(tail_losses) > 0:
            es = -tail_losses.mean()
            return round(es * 100, 2)
        return 0.0
    except:
        return 0.0
```

### 流动性风险分析

```python
def analyze_liquidity_risk(df, volume_data=None):
    """流动性风险分析"""
    liquidity_metrics = {}
    
    try:
        # 成交量分析
        if volume_data is None and 'volume' in df.columns:
            volume = df['volume']
        else:
            volume = volume_data
            
        if volume is not None and len(volume) > 10:
            avg_volume = volume.mean()
            current_volume = volume.iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # 换手率分析
            if 'turnover_rate' in df.columns:
                turnover = df['turnover_rate']
                avg_turnover = turnover.mean()
                current_turnover = turnover.iloc[-1]
                turnover_ratio = current_turnover / avg_turnover if avg_turnover > 0 else 1
            else:
                turnover_ratio = 1
            
            # 流动性评分
            liquidity_score = 50
            
            # 成交量影响
            if volume_ratio < 0.5:
                liquidity_score -= 30
                liquidity_status = '流动性差'
            elif volume_ratio < 0.8:
                liquidity_score -= 15
                liquidity_status = '流动性一般'
            elif volume_ratio > 2:
                liquidity_score += 10
                liquidity_status = '流动性好'
            else:
                liquidity_status = '流动性正常'
            
            # 换手率影响
            if turnover_ratio < 0.5:
                liquidity_score -= 20
            elif turnover_ratio > 2:
                liquidity_score += 10
            
            liquidity_score = max(0, min(100, liquidity_score))
            
            liquidity_metrics.update({
                'avg_volume': avg_volume,
                'current_volume': current_volume,
                'volume_ratio': round(volume_ratio, 2),
                'liquidity_status': liquidity_status,
                'liquidity_score': liquidity_score,
                'turnover_ratio': round(turnover_ratio, 2)
            })
        
    except Exception as e:
        liquidity_metrics['error'] = str(e)
    
    return liquidity_metrics
```

### 个股风险分析

```python
def analyze_stock_risk(fundamental_data, technical_data, market_data):
    """个股风险分析"""
    stock_risk = {
        'overall_risk': 50,
        'risk_categories': {},
        'risk_factors': [],
        'recommendation': '中性'
    }
    
    try:
        # 财务风险
        financial_risk = assess_financial_risk(fundamental_data)
        stock_risk['risk_categories']['财务风险'] = financial_risk
        
        # 技术风险
        technical_risk = assess_technical_risk(technical_data)
        stock_risk['risk_categories']['技术风险'] = technical_risk
        
        # 市场风险
        market_risk = assess_market_risk(market_data)
        stock_risk['risk_categories']['市场风险'] = market_risk
        
        # 流动性风险
        liquidity_risk = assess_liquidity_risk(technical_data)
        stock_risk['risk_categories']['流动性风险'] = liquidity_risk
        
        # 综合风险评分
        weights = {
            '财务风险': 0.3,
            '技术风险': 0.25,
            '市场风险': 0.25,
            '流动性风险': 0.2
        }
        
        total_weight = sum(weights.values())
        weighted_score = 0
        
        for category, score in stock_risk['risk_categories'].items():
            if isinstance(score, dict) and 'score' in score:
                weighted_score += score['score'] * weights.get(category, 0)
        
        stock_risk['overall_risk'] = round(weighted_score / total_weight, 1)
        
        # 风险等级
        if stock_risk['overall_risk'] >= 70:
            stock_risk['risk_level'] = '高风险'
            stock_risk['recommendation'] = '谨慎投资'
        elif stock_risk['overall_risk'] >= 50:
            stock_risk['risk_level'] = '中风险'
            stock_risk['recommendation'] = '适度参与'
        else:
            stock_risk['risk_level'] = '低风险'
            stock_risk['recommendation'] = '可考虑配置'
        
        # 识别主要风险因素
        for category, risk_info in stock_risk['risk_categories'].items():
            if isinstance(risk_info, dict) and 'high_risk_factors' in risk_info:
                stock_risk['risk_factors'].extend(risk_info['high_risk_factors'])
        
    except Exception as e:
        stock_risk['error'] = str(e)
    
    return stock_risk

def assess_financial_risk(fundamental_data):
    """评估财务风险"""
    risk_info = {
        'score': 50,
        'high_risk_factors': [],
        'details': {}
    }
    
    try:
        # 资产负债率
        if '资产负债率' in fundamental_data:
            debt_ratio = fundamental_data['资产负债率']
            if debt_ratio > 70:
                risk_info['high_risk_factors'].append(f"资产负债率过高 ({debt_ratio:.1f}%)")
                risk_info['score'] += 30
            elif debt_ratio > 50:
                risk_info['score'] += 15
        
        # 流动比率
        if '流动比率' in fundamental_data:
            current_ratio = fundamental_data['流动比率']
            if current_ratio < 1:
                risk_info['high_risk_factors'].append(f"流动比率过低 ({current_ratio:.2f})")
                risk_info['score'] += 25
            elif current_ratio < 1.5:
                risk_info['score'] += 10
        
        # ROE
        if 'ROE' in fundamental_data:
            roe = fundamental_data['ROE']
            if roe < 5:
                risk_info['high_risk_factors'].append(f"ROE偏低 ({roe:.1f}%)")
                risk_info['score'] += 20
            elif roe < 10:
                risk_info['score'] += 10
        
        # 净利率
        if '净利率' in fundamental_data:
            net_margin = fundamental_data['净利率']
            if net_margin < 5:
                risk_info['high_risk_factors'].append(f"净利率偏低 ({net_margin:.1f}%)")
                risk_info['score'] += 15
        
        risk_info['score'] = min(100, risk_info['score'])
        risk_info['details'] = {
            '资产负债率': fundamental_data.get('资产负债率', 'N/A'),
            '流动比率': fundamental_data.get('流动比率', 'N/A'),
            'ROE': fundamental_data.get('ROE', 'N/A'),
            '净利率': fundamental_data.get('净利率', 'N/A')
        }
        
    except Exception as e:
        risk_info['error'] = str(e)
    
    return risk_info

def assess_technical_risk(technical_data):
    """评估技术风险"""
    risk_info = {
        'score': 50,
        'high_risk_factors': [],
        'details': {}
    }
    
    try:
        # 趋势风险
        if 'trend_direction' in technical_data:
            trend = technical_data['trend_direction']
            if trend == '下跌':
                risk_info['high_risk_factors'].append("技术趋势偏弱")
                risk_info['score'] += 20
        
        # 超买超卖
        if 'RSI' in technical_data:
            rsi = technical_data['RSI']
            if rsi > 70:
                risk_info['high_risk_factors'].append(f"RSI超买 ({rsi:.1f})")
                risk_info['score'] += 15
            elif rsi < 30:
                risk_info['high_risk_factors'].append(f"RSI超卖 ({rsi:.1f})")
                risk_info['score'] += 10
        
        # MACD信号
        if 'macd_signal' in technical_data:
            macd_signal = technical_data['macd_signal']
            if macd_signal == '死叉':
                risk_info['high_risk_factors'].append("MACD死叉信号")
                risk_info['score'] += 15
        
        # 波动率
        if 'volatility' in technical_data:
            volatility = technical_data['volatility']
            if volatility > 3:
                risk_info['high_risk_factors'].append(f"波动率过高 ({volatility:.2f}%)")
                risk_info['score'] += 20
        
        risk_info['score'] = min(100, risk_info['score'])
        
    except Exception as e:
        risk_info['error'] = str(e)
    
    return risk_info

def assess_market_risk(market_data):
    """评估市场风险"""
    risk_info = {
        'score': 50,
        'high_risk_factors': [],
        'details': {}
    }
    
    try:
        # 市场宽度
        if 'market_width' in market_data:
            market_width = market_data['market_width']
            if market_width < -20:
                risk_info['high_risk_factors'].append(f"市场宽度为负 ({market_width:.1f}%)")
                risk_info['score'] += 25
        
        # 涨停板数量
        if 'limit_up_count' in market_data:
            limit_up_count = market_data['limit_up_count']
            if limit_up_count < 10 and market_data.get('total_stocks', 0) > 3000:
                risk_info['high_risk_factors'].append("涨停板数量偏少")
                risk_info['score'] += 15
        
        # 北向资金
        if 'northbound_trend' in market_data:
            north_trend = market_data['northbound_trend']
            if north_trend == '流出':
                risk_info['high_risk_factors'].append("北向资金持续流出")
                risk_info['score'] += 20
        
        risk_info['score'] = min(100, risk_info['score'])
        
    except Exception as e:
        risk_info['error'] = str(e)
    
    return risk_info

def assess_liquidity_risk(technical_data):
    """评估流动性风险"""
    risk_info = {
        'score': 50,
        'high_risk_factors': [],
        'details': {}
    }
    
    try:
        # 成交量
        if 'volume_ratio' in technical_data:
            volume_ratio = technical_data['volume_ratio']
            if volume_ratio < 0.5:
                risk_info['high_risk_factors'].append(f"成交量低迷 ({volume_ratio:.2f}倍)")
                risk_info['score'] += 30
        
        # 换手率
        if 'turnover_ratio' in technical_data:
            turnover_ratio = technical_data['turnover_ratio']
            if turnover_ratio < 0.5:
                risk_info['high_risk_factors'].append(f"换手率偏低 ({turnover_ratio:.2f}倍)")
                risk_info['score'] += 20
        
        risk_info['score'] = min(100, risk_info['score'])
        
    except Exception as e:
        risk_info['error'] = str(e)
    
    return risk_info
```

### 综合风险分析报告

```python
def comprehensive_risk_analysis(code, df, fundamental_data=None, market_data=None):
    """综合风险分析报告"""
    report = {
        '股票代码': code,
        '风险总评': {},
        '详细风险分析': {},
        '风险等级': '中性',
        '风险控制建议': '',
        '压力测试结果': {}
    }
    
    try:
        # 波动率分析
        vol_analysis = analyze_volatility(df)
        report['详细风险分析'].update({'波动率分析': vol_analysis})
        
        # VaR计算
        var_analysis = calculate_var(df)
        report['详细风险分析'].update({'VaR分析': var_analysis})
        
        # 流动性分析
        liquidity_analysis = analyze_liquidity_risk(df)
        report['详细风险分析'].update({'流动性分析': liquidity_analysis})
        
        # 个股风险分析
        stock_risk = analyze_stock_risk(
            fundamental_data or {}, 
            {'trend_direction': '上涨', 'RSI': 50, 'volatility': 2.0},
            market_data or {}
        )
        report['详细风险分析'].update({'个股风险': stock_risk})
        
        # 综合风险评分
        overall_risk = stock_risk.get('overall_risk', 50)
        report['风险总评'] = {
            '综合风险评分': overall_risk,
            '风险等级': stock_risk.get('risk_level', '中性'),
            '推荐评级': stock_risk.get('recommendation', '中性')
        }
        
        # 风险控制建议
        report['风险控制建议'] = generate_risk_control_advice(report)
        
        # 压力测试
        report['压力测试结果'] = perform_stress_test(df, overall_risk)
        
    except Exception as e:
        report['错误信息'] = str(e)
    
    return report

def generate_risk_control_advice(report):
    """生成风险控制建议"""
    advice_parts = []
    
    overall_risk = report['风险总评'].get('综合风险评分', 50)
    
    if overall_risk >= 70:
        advice_parts.append("⚠️ 高风险股票，建议严格控制仓位")
        advice_parts.append("🎯 设置严格止损位（建议-5%~-8%）")
        advice_parts.append("📊 分批建仓，避免一次性重仓")
    elif overall_risk >= 50:
        advice_parts.append("🟡 中风险股票，适度参与")
        advice_parts.append("🎯 止损位可设在-8%~-12%")
        advice_parts.append("📈 可结合趋势跟踪策略")
    else:
        advice_parts.append("🟢 低风险股票，可适当配置")
        advice_parts.append("🎯 止损位可设在-10%~-15%")
        advice_parts.append("📊 可考虑定投策略")
    
    # 具体风险因素建议
    detailed_risks = report['详细风险分析']
    
    if '波动率分析' in detailed_risks:
        vol_info = detailed_risks['波动率分析']
        if vol_info.get('current_vol_state') == '高波动':
            advice_parts.append("💡 高波动环境下，减少杠杆使用")
    
    if '个股风险' in detailed_risks:
        stock_risk = detailed_risks['个股风险']
        if '财务风险' in stock_risk['risk_categories']:
            fin_risk = stock_risk['risk_categories']['财务风险']
            if fin_risk.get('high_risk_factors'):
                advice_parts.append(f"🔍 关注财务风险: {', '.join(fin_risk['high_risk_factors'])}")
    
    return ' '.join(advice_parts)

def perform_stress_test(df, overall_risk):
    """压力测试"""
    stress_results = {}
    
    try:
        # 历史最大回撤
        max_drawdown = calculate_max_drawdown(df)
        stress_results['历史最大回撤'] = f"{max_drawdown}%"
        
        # 模拟极端情况
        returns = df['close'].pct_change().dropna()
        if len(returns) > 10:
            # 99%分位数的极端损失
            extreme_loss = np.percentile(returns, 1)
            stress_results['极端损失(99%)'] = f"{extreme_loss*100:.2f}%"
            
            # 市场暴跌情景（-5%到-10%）
            scenarios = [-5, -10, -15]
            for scenario in scenarios:
                simulated_price = df['close'].iloc[-1] * (1 + scenario/100)
                stress_results[f'市场下跌{scenario}%'] = f"{simulated_price:.2f}"
        
        # 风险等级对应的压力测试
        if overall_risk >= 70:
            stress_results['高风险应对'] = "建议最大仓位不超过10%"
        elif overall_risk >= 50:
            stress_results['中风险应对'] = "建议最大仓位不超过20%"
        else:
            stress_results['低风险应对'] = "可考虑30%以内仓位"
        
    except Exception as e:
        stress_results['错误'] = str(e)
    
    return stress_results
```

## 安装依赖

```bash
pip install pandas numpy scipy
```

## 使用示例

```python
# 综合风险分析示例
code = "000001"
df = get_stock_data(code, "2024-01-01", "2024-12-31")

risk_report = comprehensive_risk_analysis(code, df)

print("="*60)
print(f"{code} 风险分析报告")
print("="*60)

print(f"\n📊 综合风险评分: {risk_report['风险总评']['综合风险评分']}/100")
print(f"Risk Level: {risk_report['风险总评']['风险等级']}")
print(f"Recommendation: {risk_report['风险总评']['推荐评级']}")

print(f"\n⚠️ 主要风险因素:")
for factor in risk_report.get('详细风险分析', {}).get('个股风险', {}).get('risk_factors', []):
    print(f"   • {factor}")

print(f"\n📉 波动率分析:")
vol_info = risk_report['详细风险分析']['波动率分析']
print(f"   年化波动率: {vol_info.get('annual_volatility', 'N/A')}%")
print(f"   当前波动状态: {vol_info.get('current_vol_state', 'N/A')}")
print(f"   最大回撤: {vol_info.get('max_drawdown', 'N/A')}%")

print(f"\n💰 VaR分析 (95%置信度):")
var_info = risk_report['详细风险分析']['VaR分析']
print(f"   历史模拟VaR: {var_info.get('historical_var', 'N/A')}%")
print(f"   参数法VaR: {var_info.get('parametric_var', 'N/A')}%")
print(f"   期望短缺: {var_info.get('expected_shortfall', 'N/A')}%")

print(f"\n🛡️ 风险控制建议: {risk_report['风险控制建议']}")

print(f"\n💥 压力测试结果:")
stress_results = risk_report['压力测试结果']
for scenario, result in stress_results.items():
    print(f"   {scenario}: {result}")

print("="*60)
```

## 输出格式

完整的风险分析报告应包括：
1. 风险评分仪表盘
2. 波动率热力图
3. VaR分布图
4. 风险因素雷达图
5. 压力测试情景表
6. 风险控制建议清单

## 注意事项

1. **风险量化局限性**：所有风险指标都是历史数据的反映
2. **黑天鹅事件**：无法预测极端突发事件
3. **模型假设**：VaR计算基于正态分布假设
4. **数据时效性**：风险分析需要最新数据
5. **个体差异**：不同投资者风险承受能力不同

## 风险等级标准

- **低风险 (<50)**: 稳健型投资者可配置
- **中风险 (50-70)**: 平衡型投资者适合
- **高风险 (>70)**: 积极型投资者谨慎参与
- **极高风险 (>85)**: 专业投资者可考虑
