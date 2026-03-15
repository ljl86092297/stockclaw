---
name: fundamental_analysis
description: "股票基本面分析，包括财务指标、估值分析、行业对比、公司基本面。使用场景：用户需要分析公司基本面、财务健康状况、估值水平、行业地位。"
metadata: { "openclaw": { "emoji": "💰", "requires": { "python": true, "packages": ["baostock", "pandas", "numpy"] } } }
---

# 基本面分析Skill

股票基本面分析，包括财务指标、估值分析、行业对比、公司基本面。

## 使用场景

✅ **使用此Skill当：**

- "分析公司基本面"
- "查看财务指标"
- "估值分析"
- "行业对比"
- "盈利能力分析"
- "财务健康状况"

## 分析维度

### 1. 财务指标分析
- 盈利能力指标
- 偿债能力指标  
- 运营效率指标
- 成长性指标

### 2. 估值分析
- PE、PB、PS比率
- PEG估值
- 股息率分析
- 相对估值

### 3. 行业对比
- 行业地位分析
- 竞争对手对比
- 行业平均估值

### 4. 公司治理
- 股东结构
- 管理层分析
- 公司治理评分

## 命令示例

### 获取财务数据

```python
import sys
sys.path.append('/home/openclaw/.openclaw/workspace')
from baostock_utils import get_financial_data as bs_get_financial_data
import pandas as pd

def get_financial_data(code):
    """获取公司财务数据 (使用Baostock)"""
    try:
        # 使用Baostock获取财务数据
        financials = bs_get_financial_data(code, year=2024, quarter=4)
        
        # 整理数据格式
        result = {}
        
        if 'profit' in financials and not financials['profit'].empty:
            result['income_statement'] = financials['profit']
        
        if 'balance' in financials and not financials['balance'].empty:
            result['balance_sheet'] = financials['balance']
        
        if 'cashflow' in financials and not financials['cashflow'].empty:
            result['cash_flow'] = financials['cashflow']
        
        return result
        
    except Exception as e:
        print(f"Baostock获取财务数据失败: {e}")
        # 保留原有akshare代码结构，但标记为需要其他数据源
        print("注意: Baostock财务数据获取可能需要调整参数或使用其他数据源")
        return {
            'balance_sheet': pd.DataFrame(),
            'income_statement': pd.DataFrame(),
            'cash_flow': pd.DataFrame()
        }
```

### 计算财务比率

```python
def calculate_financial_ratios(balance_sheet, income_statement):
    """计算关键财务比率"""
    ratios = {}
    
    # 盈利能力指标
    if '净利润' in income_statement.columns and '营业收入' in income_statement.columns:
        latest_net_profit = income_statement['净利润'].iloc[-1]
        latest_revenue = income_statement['营业收入'].iloc[-1]
        
        # 净利率
        if latest_revenue != 0:
            ratios['净利率'] = latest_net_profit / latest_revenue * 100
    
    # ROE（净资产收益率）
    if '净利润' in income_statement.columns and '所有者权益合计' in balance_sheet.columns:
        latest_net_profit = income_statement['净利润'].iloc[-1]
        latest_equity = balance_sheet['所有者权益合计'].iloc[-1]
        
        if latest_equity != 0:
            ratios['ROE'] = latest_net_profit / latest_equity * 100
    
    # 资产负债率
    if '负债合计' in balance_sheet.columns and '资产总计' in balance_sheet.columns:
        latest_liabilities = balance_sheet['负债合计'].iloc[-1]
        latest_assets = balance_sheet['资产总计'].iloc[-1]
        
        if latest_assets != 0:
            ratios['资产负债率'] = latest_liabilities / latest_assets * 100
    
    # 流动比率
    if '流动资产合计' in balance_sheet.columns and '流动负债合计' in balance_sheet.columns:
        latest_current_assets = balance_sheet['流动资产合计'].iloc[-1]
        latest_current_liabilities = balance_sheet['流动负债合计'].iloc[-1]
        
        if latest_current_liabilities != 0:
            ratios['流动比率'] = latest_current_assets / latest_current_liabilities
    
    return ratios
```

### 估值分析

```python
def valuation_analysis(code, current_price):
    """估值分析"""
    valuation = {}
    
    try:
        # 获取市盈率PE
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20240101", end_date="20241231", adjust="")
        if not stock_zh_a_hist_df.empty:
            # 计算每股收益（简化）
            eps = 1.0  # 这里需要实际EPS数据
            
            # PE比率
            if eps > 0:
                valuation['PE'] = current_price / eps
            
            # PB比率（需要每股净资产）
            bps = 5.0  # 这里需要实际每股净资产
            if bps > 0:
                valuation['PB'] = current_price / bps
            
            # PS比率（需要每股营收）
            sps = 10.0  # 这里需要实际每股营收
            if sps > 0:
                valuation['PS'] = current_price / sps
    
    except Exception as e:
        print(f"估值分析错误: {e}")
    
    return valuation
```

### 行业对比分析

```python
def industry_comparison(code):
    """行业对比分析"""
    try:
        # 获取行业信息
        stock_industry_df = ak.stock_board_industry_name_em()
        
        # 获取公司所属行业
        # 这里需要根据code查找行业
        
        comparison = {
            'industry': '未知行业',
            'pe_industry_avg': 15.0,  # 行业平均PE
            'pb_industry_avg': 2.0,   # 行业平均PB
            'rank': '中等'
        }
        
        return comparison
    
    except Exception as e:
        print(f"行业对比错误: {e}")
        return {}
```

### 综合基本面分析

```python
def comprehensive_fundamental_analysis(code, current_price):
    """综合基本面分析"""
    analysis = {}
    
    try:
        # 获取财务数据
        financial_data = get_financial_data(code)
        
        # 计算财务比率
        ratios = calculate_financial_ratios(
            financial_data['balance_sheet'],
            financial_data['income_statement']
        )
        
        # 估值分析
        valuation = valuation_analysis(code, current_price)
        
        # 行业对比
        industry = industry_comparison(code)
        
        # 综合评估
        analysis['财务健康度'] = assess_financial_health(ratios)
        analysis['估值水平'] = assess_valuation(valuation, industry)
        analysis['成长性'] = assess_growth(financial_data['income_statement'])
        analysis['风险提示'] = identify_risks(ratios, financial_data)
        
        # 评分系统
        analysis['综合评分'] = calculate_composite_score(analysis)
        
        return analysis
    
    except Exception as e:
        print(f"基本面分析错误: {e}")
        return {}
```

### 财务健康度评估

```python
def assess_financial_health(ratios):
    """评估财务健康度"""
    health = {
        'status': '良好',
        'details': [],
        'score': 80  # 满分100
    }
    
    # 检查资产负债率
    if '资产负债率' in ratios:
        debt_ratio = ratios['资产负债率']
        if debt_ratio > 70:
            health['details'].append(f"资产负债率偏高: {debt_ratio:.1f}%")
            health['score'] -= 20
        elif debt_ratio < 30:
            health['details'].append(f"资产负债率偏低: {debt_ratio:.1f}%")
            health['score'] -= 5
    
    # 检查流动比率
    if '流动比率' in ratios:
        current_ratio = ratios['流动比率']
        if current_ratio < 1:
            health['details'].append(f"流动比率偏低: {current_ratio:.2f}")
            health['score'] -= 30
        elif current_ratio < 1.5:
            health['details'].append(f"流动比率一般: {current_ratio:.2f}")
            health['score'] -= 10
    
    # 检查ROE
    if 'ROE' in ratios:
        roe = ratios['ROE']
        if roe > 15:
            health['details'].append(f"ROE优秀: {roe:.1f}%")
            health['score'] += 10
        elif roe < 5:
            health['details'].append(f"ROE偏低: {roe:.1f}%")
            health['score'] -= 15
    
    # 更新状态
    if health['score'] >= 80:
        health['status'] = '优秀'
    elif health['score'] >= 60:
        health['status'] = '良好'
    elif health['score'] >= 40:
        health['status'] = '一般'
    else:
        health['status'] = '较差'
    
    return health
```

### 估值评估

```python
def assess_valuation(valuation, industry):
    """评估估值水平"""
    assessment = {
        'level': '合理',
        'details': [],
        'score': 70
    }
    
    # PE评估
    if 'PE' in valuation and 'pe_industry_avg' in industry:
        pe = valuation['PE']
        industry_avg = industry['pe_industry_avg']
        
        if pe > industry_avg * 1.5:
            assessment['details'].append(f"PE偏高: {pe:.1f} (行业平均: {industry_avg:.1f})")
            assessment['score'] -= 20
            assessment['level'] = '偏高'
        elif pe < industry_avg * 0.7:
            assessment['details'].append(f"PE偏低: {pe:.1f} (行业平均: {industry_avg:.1f})")
            assessment['score'] += 10
            assessment['level'] = '偏低'
        else:
            assessment['details'].append(f"PE合理: {pe:.1f} (行业平均: {industry_avg:.1f})")
    
    # PB评估
    if 'PB' in valuation and 'pb_industry_avg' in industry:
        pb = valuation['PB']
        industry_avg = industry['pb_industry_avg']
        
        if pb > industry_avg * 1.5:
            assessment['details'].append(f"PB偏高: {pb:.2f} (行业平均: {industry_avg:.2f})")
            assessment['score'] -= 15
        elif pb < industry_avg * 0.7:
            assessment['details'].append(f"PB偏低: {pb:.2f} (行业平均: {industry_avg:.2f})")
            assessment['score'] += 5
    
    return assessment
```

### 成长性评估

```python
def assess_growth(income_statement):
    """评估成长性"""
    growth = {
        'revenue_growth': 0,
        'profit_growth': 0,
        'trend': '稳定',
        'score': 60
    }
    
    try:
        # 计算营收增长率
        if '营业收入' in income_statement.columns and len(income_statement) >= 2:
            recent_revenue = income_statement['营业收入'].iloc[-1]
            previous_revenue = income_statement['营业收入'].iloc[-2]
            
            if previous_revenue != 0:
                revenue_growth = (recent_revenue - previous_revenue) / previous_revenue * 100
                growth['revenue_growth'] = revenue_growth
                
                if revenue_growth > 20:
                    growth['trend'] = '高速增长'
                    growth['score'] += 20
                elif revenue_growth > 10:
                    growth['trend'] = '稳定增长'
                    growth['score'] += 10
                elif revenue_growth < 0:
                    growth['trend'] = '负增长'
                    growth['score'] -= 20
        
        # 计算净利润增长率
        if '净利润' in income_statement.columns and len(income_statement) >= 2:
            recent_profit = income_statement['净利润'].iloc[-1]
            previous_profit = income_statement['净利润'].iloc[-2]
            
            if previous_profit != 0:
                profit_growth = (recent_profit - previous_profit) / previous_profit * 100
                growth['profit_growth'] = profit_growth
    
    except Exception as e:
        print(f"成长性评估错误: {e}")
    
    return growth
```

### 风险识别

```python
def identify_risks(ratios, financial_data):
    """识别风险因素"""
    risks = []
    
    # 高负债风险
    if '资产负债率' in ratios and ratios['资产负债率'] > 70:
        risks.append({
            'type': '财务风险',
            'level': '高',
            'description': f"资产负债率偏高 ({ratios['资产负债率']:.1f}%)，偿债压力较大"
        })
    
    # 流动性风险
    if '流动比率' in ratios and ratios['流动比率'] < 1:
        risks.append({
            'type': '流动性风险',
            'level': '高',
            'description': f"流动比率偏低 ({ratios['流动比率']:.2f})，短期偿债能力不足"
        })
    
    # 盈利能力风险
    if '净利率' in ratios and ratios['净利率'] < 5:
        risks.append({
            'type': '盈利风险',
            'level': '中',
            'description': f"净利率偏低 ({ratios['净利率']:.1f}%)，盈利能力较弱"
        })
    
    # 成长性风险
    income_statement = financial_data['income_statement']
    if '营业收入' in income_statement.columns and len(income_statement) >= 2:
        recent = income_statement['营业收入'].iloc[-1]
        previous = income_statement['营业收入'].iloc[-2]
        if previous != 0 and (recent - previous) / previous < -0.1:
            risks.append({
                'type': '成长风险',
                'level': '中',
                'description': "营收出现明显下滑"
            })
    
    return risks
```

### 综合评分计算

```python
def calculate_composite_score(analysis):
    """计算综合评分"""
    score = 50  # 基础分
    
    # 财务健康度加分
    if '财务健康度' in analysis:
        score += analysis['财务健康度']['score'] * 0.3
    
    # 估值水平加分
    if '估值水平' in analysis:
        score += analysis['估值水平']['score'] * 0.3
    
    # 成长性加分
    if '成长性' in analysis:
        score += analysis['成长性']['score'] * 0.2
    
    # 风险扣分
    if '风险提示' in analysis:
        risk_count = len(analysis['风险提示'])
        score -= risk_count * 5
    
    # 确保分数在0-100之间
    score = max(0, min(100, score))
    
    return round(score, 1)
```

## 安装依赖

```bash
pip install akshare pandas numpy
```

## 使用示例

```python
# 综合基本面分析示例
code = "000001"  # 平安银行
current_price = 15.50  # 当前价格

analysis = comprehensive_fundamental_analysis(code, current_price)

print(f"股票代码: {code}")
print(f"财务健康度: {analysis['财务健康度']['status']} ({analysis['财务健康度']['score']}分)")
print(f"估值水平: {analysis['估值水平']['level']} ({analysis['估值水平']['score']}分)")
print(f"成长性: {analysis['成长性']['trend']} ({analysis['成长性']['score']}分)")
print(f"综合评分: {analysis['综合评分']}/100")

if analysis['风险提示']:
    print("\n风险提示:")
    for risk in analysis['风险提示']:
        print(f"  - [{risk['level']}] {risk['type']}: {risk['description']}")
```

## 注意事项

1. **数据准确性**：财务数据需要从可靠来源获取
2. **行业对比**：需要准确的行业分类数据
3. **估值方法**：不同行业适用不同的估值方法
4. **历史数据**：需要足够的历史数据进行趋势分析
5. **季节性因素**：考虑财务数据的季节性影响

## 输出格式

完整的分析报告应包括：
1. 财务指标表格
2. 估值对比图表
3. 行业位置雷达图
4. 风险提示列表
5. 投资建议总结
