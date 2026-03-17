---
name: market_sentiment
description: "市场情绪分析，包括投资者情绪、市场热度、资金流向、舆情分析。使用场景：用户需要了解市场情绪、投资者心理、资金动向、舆情影响。"
metadata: { "openclaw": { "emoji": "😊", "requires": { "python": true, "packages": ["baostock", "pandas", "numpy"] } } }
---

# 市场情绪分析Skill

市场情绪分析，包括投资者情绪、市场热度、资金流向、舆情分析。

## 使用场景

✅ **使用此Skill当：**

- "分析市场情绪"
- "查看资金流向"
- "分析投资者情绪"
- "舆情监控"
- "市场热度分析"
- "情绪指标计算"
- "判断市场环境"
- "分析大盘趋势"
- "观察板块轮动"
- "评估市场风险"

## 分析维度

### 1. 市场环境分析（新增）
- 大盘趋势判断（牛市/熊市/震荡市）
- 板块轮动观察
- 市场整体风险评估
- 环境因子量化

### 2. 资金流向分析
- 主力资金流向
- 北向资金流向
- 融资融券数据
- 大单交易分析

### 3. 市场热度指标
- 成交量分析
- 换手率分析
- 涨停板数量
- 市场宽度指标

### 4. 投资者情绪
- 散户情绪指标
- 机构情绪指标
- 情绪指数计算
- 恐慌贪婪指数

### 5. 舆情分析
- 新闻情感分析
- 社交媒体情绪
- 搜索热度分析
- 论坛讨论热度

## 命令示例

### 资金流向分析

```python
import sys
sys.path.append('/home/openclaw/.openclaw/workspace')
from baostock_utils import get_stock_data
import pandas as pd

def analyze_capital_flow(code):
    """分析资金流向 (基于Baostock数据)"""
    capital_flow = {}
    
    try:
        # 使用Baostock获取股票数据
        df = get_stock_data(code, start_date=None, end_date=None)
        
        if not df.empty and '换手率' in df.columns and '成交量' in df.columns:
            latest_data = df.iloc[-1]
            
            # Baostock提供换手率和成交量，可以间接分析资金活跃度
            capital_flow['换手率'] = latest_data.get('换手率', 0)
            capital_flow['成交量'] = latest_data.get('成交量', 0)
            capital_flow['成交额'] = latest_data.get('成交额', 0)
            capital_flow['涨跌幅'] = latest_data.get('涨跌幅', 0)
            
            # 计算资金活跃度指标
            if len(df) > 5:
                avg_volume = df['成交量'].tail(5).mean()
                if avg_volume > 0:
                    capital_flow['成交量比率'] = latest_data['成交量'] / avg_volume
                
                avg_turnover = df['换手率'].tail(5).mean()
                if avg_turnover > 0:
                    capital_flow['换手率比率'] = latest_data['换手率'] / avg_turnover
    
    except Exception as e:
        print(f"资金流向分析错误 (Baostock): {e}")
        # 注意: Baostock不提供详细的资金流向分类数据，需要其他数据源
        print("提示: 详细的资金流向数据(主力/超大单等)需要其他数据源")
    
    return capital_flow
```

### 北向资金分析

```python
def analyze_northbound_flow():
    """分析北向资金流向"""
    try:
        # 获取北向资金数据
        stock_hsgt_north_net_flow_in_em_df = ak.stock_hsgt_north_net_flow_in_em(symbol="北上")
        
        if not stock_hsgt_north_net_flow_in_em_df.empty:
            latest_data = stock_hsgt_north_net_flow_in_em_df.iloc[-1]
            
            northbound_flow = {
                'date': latest_data.get('日期', ''),
                'northbound_inflow': latest_data.get('北向资金净流入', 0),
                'sh_northbound_inflow': latest_data.get('沪股通净流入', 0),
                'sz_northbound_inflow': latest_data.get('深股通净流入', 0),
                'trend': '流入' if latest_data.get('北向资金净流入', 0) > 0 else '流出'
            }
            
            return northbound_flow
    
    except Exception as e:
        print(f"北向资金分析错误: {e}")
    
    return {}
```

### 融资融券分析

```python
def analyze_margin_trading(code):
    """分析融资融券数据"""
    try:
        # 获取融资融券数据
        stock_margin_detail_szse_df = ak.stock_margin_detail_szse(start_date="20240101", end_date="20241231")
        
        if not stock_margin_detail_szse_df.empty:
            # 筛选指定股票
            stock_data = stock_margin_detail_szse_df[stock_margin_detail_szse_df['证券代码'] == code]
            
            if not stock_data.empty:
                latest_data = stock_data.iloc[-1]
                
                margin_data = {
                    'date': latest_data.get('信用交易日期', ''),
                    'financing_purchase': latest_data.get('融资买入额', 0),
                    'financing_balance': latest_data.get('融资余额', 0),
                    'securities_lending': latest_data.get('融券卖出量', 0),
                    'securities_balance': latest_data.get('融券余量', 0),
                    'financing_ratio': 0
                }
                
                # 计算融资比例
                if margin_data['financing_balance'] > 0:
                    total_balance = margin_data['financing_balance'] + margin_data['securities_balance']
                    margin_data['financing_ratio'] = margin_data['financing_balance'] / total_balance * 100
                
                return margin_data
    
    except Exception as e:
        print(f"融资融券分析错误: {e}")
    
    return {}
```

### 市场热度分析

```python
def analyze_market_heat():
    """分析市场热度"""
    market_heat = {}
    
    try:
        # 获取市场整体数据
        stock_zh_a_spot_df = ak.stock_zh_a_spot()
        
        if not stock_zh_a_spot_df.empty:
            total_stocks = len(stock_zh_a_spot_df)
            
            # 计算上涨股票数量
            rising_stocks = len(stock_zh_a_spot_df[stock_zh_a_spot_df['涨跌幅'] > 0])
            falling_stocks = len(stock_zh_a_spot_df[stock_zh_a_spot_df['涨跌幅'] < 0])
            
            # 计算涨停板数量
            limit_up_stocks = len(stock_zh_a_spot_df[stock_zh_a_spot_df['涨跌幅'] >= 9.8])
            limit_down_stocks = len(stock_zh_a_spot_df[stock_zh_a_spot_df['涨跌幅'] <= -9.8])
            
            # 计算平均换手率
            avg_turnover = stock_zh_a_spot_df['换手率'].mean()
            
            market_heat = {
                'total_stocks': total_stocks,
                'rising_stocks': rising_stocks,
                'falling_stocks': falling_stocks,
                'rising_ratio': rising_stocks / total_stocks * 100 if total_stocks > 0 else 0,
                'limit_up_count': limit_up_stocks,
                'limit_down_count': limit_down_stocks,
                'avg_turnover': avg_turnover,
                'market_width': (rising_stocks - falling_stocks) / total_stocks * 100 if total_stocks > 0 else 0
            }
    
    except Exception as e:
        print(f"市场热度分析错误: {e}")
    
    return market_heat
```

### 情绪指数计算

```python
def calculate_sentiment_index(code, price_data):
    """计算情绪指数"""
    sentiment = {
        'score': 50,  # 中性
        'level': '中性',
        'indicators': {}
    }
    
    try:
        indicators = {}
        
        # 1. 价格动量指标
        if len(price_data) >= 10:
            recent_prices = price_data['close'].tail(10)
            price_change = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0] * 100
            
            if price_change > 10:
                indicators['price_momentum'] = {'value': price_change, 'weight': 0.3, 'score': 80}
            elif price_change > 5:
                indicators['price_momentum'] = {'value': price_change, 'weight': 0.3, 'score': 70}
            elif price_change > 0:
                indicators['price_momentum'] = {'value': price_change, 'weight': 0.3, 'score': 60}
            elif price_change > -5:
                indicators['price_momentum'] = {'value': price_change, 'weight': 0.3, 'score': 40}
            else:
                indicators['price_momentum'] = {'value': price_change, 'weight': 0.3, 'score': 20}
        
        # 2. 成交量指标
        if 'volume' in price_data.columns and len(price_data) >= 20:
            recent_volume = price_data['volume'].tail(20)
            avg_volume = recent_volume.mean()
            latest_volume = recent_volume.iloc[-1]
            volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > 2:
                indicators['volume'] = {'value': volume_ratio, 'weight': 0.2, 'score': 90}
            elif volume_ratio > 1.5:
                indicators['volume'] = {'value': volume_ratio, 'weight': 0.2, 'score': 70}
            elif volume_ratio > 1:
                indicators['volume'] = {'value': volume_ratio, 'weight': 0.2, 'score': 60}
            elif volume_ratio > 0.5:
                indicators['volume'] = {'value': volume_ratio, 'weight': 0.2, 'score': 40}
            else:
                indicators['volume'] = {'value': volume_ratio, 'weight': 0.2, 'score': 20}
        
        # 3. 波动率指标
        if len(price_data) >= 20:
            recent_returns = price_data['close'].pct_change().tail(20).dropna()
            volatility = recent_returns.std() * 100
            
            if volatility < 1:
                indicators['volatility'] = {'value': volatility, 'weight': 0.2, 'score': 70}
            elif volatility < 2:
                indicators['volatility'] = {'value': volatility, 'weight': 0.2, 'score': 60}
            elif volatility < 3:
                indicators['volatility'] = {'value': volatility, 'weight': 0.2, 'score': 50}
            elif volatility < 5:
                indicators['volatility'] = {'value': volatility, 'weight': 0.2, 'score': 40}
            else:
                indicators['volatility'] = {'value': volatility, 'weight': 0.2, 'score': 20}
        
        # 4. 资金流向指标（从其他函数获取）
        capital_flow = analyze_capital_flow(code)
        if '主力净流入' in capital_flow:
            main_inflow = capital_flow['主力净流入']
            
            if main_inflow > 10000000:  # 1000万
                indicators['capital_flow'] = {'value': main_inflow, 'weight': 0.3, 'score': 90}
            elif main_inflow > 0:
                indicators['capital_flow'] = {'value': main_inflow, 'weight': 0.3, 'score': 70}
            elif main_inflow > -10000000:
                indicators['capital_flow'] = {'value': main_inflow, 'weight': 0.3, 'score': 40}
            else:
                indicators['capital_flow'] = {'value': main_inflow, 'weight': 0.3, 'score': 20}
        
        # 计算综合情绪分数
        total_weight = 0
        weighted_score = 0
        
        for indicator_name, indicator_data in indicators.items():
            weighted_score += indicator_data['score'] * indicator_data['weight']
            total_weight += indicator_data['weight']
        
        if total_weight > 0:
            sentiment_score = weighted_score / total_weight
            sentiment['score'] = round(sentiment_score, 1)
            sentiment['indicators'] = indicators
            
            # 确定情绪等级
            if sentiment_score >= 70:
                sentiment['level'] = '乐观'
            elif sentiment_score >= 60:
                sentiment['level'] = '偏乐观'
            elif sentiment_score >= 40:
                sentiment['level'] = '中性'
            elif sentiment_score >= 30:
                sentiment['level'] = '偏悲观'
            else:
                sentiment['level'] = '悲观'
    
    except Exception as e:
        print(f"情绪指数计算错误: {e}")
    
    return sentiment
```

### 舆情分析

```python
def analyze_sentiment_from_news(code):
    """从新闻分析舆情"""
    sentiment = {
        'news_count': 0,
        'positive_ratio': 0,
        'negative_ratio': 0,
        'neutral_ratio': 0,
        'overall_sentiment': '中性'
    }
    
    try:
        # 获取股票相关新闻
        stock_news_em_df = ak.stock_news_em(symbol=code)
        
        if not stock_news_em_df.empty:
            sentiment['news_count'] = len(stock_news_em_df)
            
            # 简单的关键词情感分析（实际应使用NLP模型）
            positive_keywords = ['上涨', '利好', '增长', '突破', '推荐', '买入', '看好', '机会']
            negative_keywords = ['下跌', '利空', '风险', '警告', '卖出', '谨慎', '调整', '亏损']
            
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for _, news in stock_news_em_df.iterrows():
                title = news.get('新闻标题', '')
                content = news.get('新闻内容', '')
                text = title + ' ' + content
                
                # 检查关键词
                has_positive = any(keyword in text for keyword in positive_keywords)
                has_negative = any(keyword in text for keyword in negative_keywords)
                
                if has_positive and not has_negative:
                    positive_count += 1
                elif has_negative and not has_positive:
                    negative_count += 1
                else:
                    neutral_count += 1
            
            # 计算比例
            total = positive_count + negative_count + neutral_count
            if total > 0:
                sentiment['positive_ratio'] = positive_count / total * 100
                sentiment['negative_ratio'] = negative_count / total * 100
                sentiment['neutral_ratio'] = neutral_count / total * 100
                
                # 确定整体情绪
                if sentiment['positive_ratio'] > 60:
                    sentiment['overall_sentiment'] = '积极'
                elif sentiment['negative_ratio'] > 60:
                    sentiment['overall_sentiment'] = '消极'
                else:
                    sentiment['overall_sentiment'] = '中性'
    
    except Exception as e:
        print(f"舆情分析错误: {e}")
    
    return sentiment
```

### 恐慌贪婪指数

```python
def calculate_fear_greed_index(market_data):
    """计算恐慌贪婪指数"""
    index = {
        'value': 50,
        'level': '中性',
        'components': {}
    }
    
    try:
        components = {}
        
        # 1. 市场波动率（25%权重）
        if 'volatility' in market_data:
            volatility = market_data['volatility']
            # 波动率越高，恐慌程度越高
            volatility_score = max(0, 100 - volatility * 10)
            components['volatility'] = {'value': volatility, 'score': volatility_score, 'weight': 0.25}
        
        # 2. 市场宽度（25%权重）
        if 'market_width' in market_data:
            market_width = market_data['market_width']
            # 市场宽度为正表示上涨股票多，贪婪程度高
            market_width_score = 50 + market_width * 0.5
            market_width_score = max(0, min(100, market_width_score))
            components['market_width'] = {'value': market_width, 'score': market_width_score, 'weight': 0.25}
        
        # 3. 涨停板比例（25%权重）
        if 'limit_up_ratio' in market_data:
            limit_up_ratio = market_data['limit_up_ratio']
            limit_up_score = limit_up_ratio * 10  # 涨停越多越贪婪
            components['limit_up'] = {'value': limit_up_ratio, 'score': limit_up_score, 'weight': 0.25}
        
        # 4. 成交量变化（25%权重）
        if 'volume_change' in market_data:
            volume_change = market_data['volume_change']
            volume_score = 50 + volume_change * 2  # 成交量增加表示贪婪
            volume_score = max(0, min(100, volume_score))
            components['volume'] = {'value': volume_change, 'score': volume_score, 'weight': 0.25}
        
        # 计算综合指数
        total_weight = 0
        weighted_score = 0
        
        for component_name, component_data in components.items():
            weighted_score += component_data['score'] * component_data['weight']
            total_weight += component_data['weight']
        
        if total_weight > 0:
            index_value = weighted_score / total_weight
            index['value'] = round(index_value, 1)
            index['components'] = components
            
            # 确定等级
            if index_value >= 80:
                index['level'] = '极度贪婪'
            elif index_value >= 60:
                index['level'] = '贪婪'
            elif index_value >= 40:
                index['level'] = '中性'
            elif index_value >= 20:
                index['level'] = '恐惧'
            else:
                index['level'] = '极度恐惧'
    
    except Exception as e:
        print(f"恐慌贪婪指数计算错误: {e}")
    
    return index
```

### 综合情绪分析报告

```python
def comprehensive_sentiment_analysis(code, price_data):
    """综合情绪分析报告"""
    report = {}
    
    try:
        # 1. 资金流向分析
        capital_flow = analyze_capital_flow(code)
        
        # 2. 情绪指数计算
        sentiment_index = calculate_sentiment_index(code, price_data)
        
        # 3. 舆情分析
        news_sentiment = analyze_sentiment_from_news(code)
        
        # 4. 市场热度
        market_heat = analyze_market_heat()
        
        # 5. 恐慌贪婪指数
        fear_greed_data = {
            'volatility': price_data['close'].pct_change().std() * 100 if len(price_data) > 1 else 2,
            'market_width': market_heat.get('market_width', 0),
            'limit_up_ratio': market_heat.get('limit_up_count', 0) / market_heat.get('total_stocks', 1) * 100,
            'volume_change': 0  # 需要计算成交量变化
        }
        fear_greed_index = calculate_fear_greed_index(fear_greed_data)
        
        # 整合报告
        report = {
            '资金流向': {
                '主力资金': f"{capital_flow.get('主力净流入', 0):,.0f}元",
                '流向状态': '净流入' if capital_flow.get('主力净流入', 0) > 0 else '净流出',
                '强度': '强' if abs(capital_flow.get('主力净流入', 0)) > 10000000 else '弱'
            },
            '情绪指数': {
                '分数': sentiment_index['score'],
                '等级': sentiment_index['level'],
                '趋势': '上升' if sentiment_index['score'] > 55 else '下降' if sentiment_index['score'] < 45 else '平稳'
            },
            '舆情分析': {
                '新闻数量': news_sentiment['news_count'],
                '积极比例': f"{news_sentiment['positive_ratio']:.1f}%",
                '整体情绪': news_sentiment['overall_sentiment']
            },
            '市场热度': {
                '上涨比例': f"{market_heat.get('rising_ratio', 0):.1f}%",
                '涨停数量': market_heat.get('limit_up_count', 0),
                '平均换手率': f"{market_heat.get('avg_turnover', 0):.2f}%"
            },
            '恐慌贪婪指数': {
                '数值': fear_greed_index['value'],
                '等级': fear_greed_index['level'],
                '市场状态': '过热' if fear_greed_index['value'] > 70 else '过冷' if fear_greed_index['value'] < 30 else '正常'
            },
            '综合评估': generate_sentiment_summary(report)
        }
    
    except Exception as e:
        print(f"综合情绪分析错误: {e}")
    
    return report

def generate_sentiment_summary(report):
    """生成情绪分析总结"""
    summary = ""
    
    try:
        # 分析资金流向
        capital_flow = report.get('资金流向', {})
        if capital_flow.get('流向状态') == '净流入' and capital_flow.get('强度') == '强':
            summary += "📈 主力资金大幅净流入，显示机构看好。"
        elif capital_flow.get('流向状态') == '净流出':
            summary += "📉 主力资金净流出，需警惕调整风险。"
        
        # 分析情绪指数
        sentiment = report.get('情绪指数', {})
        if sentiment.get('等级') == '乐观':
            summary += "😊 市场情绪乐观，投资者信心较强。"
        elif sentiment.get('等级') == '悲观':
            summary += "😟 市场情绪悲观，投资者谨慎观望。"
        
        # 分析舆情
        news = report.get('舆情分析', {})
        if news.get('整体情绪') == '积极':
            summary += "📰 舆情积极，正面新闻占主导。"
        elif news.get('整体情绪') == '消极':
            summary += "📰 舆情偏消极，负面消息较多。"
        
        # 分析恐慌贪婪指数
        fear_greed = report.get('恐慌贪婪指数', {})
        if fear_greed.get('等级') == '极度贪婪':
            summary += "⚠️ 市场处于极度贪婪状态，警惕回调风险。"
        elif fear_greed.get('等级') == '极度恐惧':
            summary += "💡 市场极度恐惧，可能是布局机会。"
        
        # 综合建议
        if len(summary) == 0:
            summary = "📊 市场情绪中性，建议观望或小仓位参与。"
        
    except Exception as e:
        summary = f"情绪分析总结生成错误: {e}"
    
    return summary
```

## 安装依赖

```bash
pip install akshare pandas numpy requests beautifulsoup4
```

## 使用示例

```python
# 综合情绪分析示例
code = "000001"
price_data = get_stock_data(code, "2024-01-01", "2024-12-31")

sentiment_report = comprehensive_sentiment_analysis(code, price_data)

print("="*60)
print("市场情绪分析报告")
print("="*60)

for category, data in sentiment_report.items():
    if category != '综合评估':
        print(f"\n{category}:")
        for key, value in data.items():
            print(f"  {key}: {value}")

print(f"\n综合评估: {sentiment_report.get('综合评估', '')}")
print("="*60)
```

## 输出格式

完整的情绪分析报告应包括：
1. 资金流向图表
2. 情绪指数趋势图
3. 舆情情感分布饼图
4. 恐慌贪婪指数仪表盘
5. 综合建议总结

## 注意事项

1. **数据时效性**：情绪数据变化快，需要实时更新
2. **数据质量**：确保数据来源可靠
3. **指标权重**：根据市场环境调整指标权重
4. **历史对比**：与历史情绪数据对比分析
5. **市场异常**：识别市场异常情绪状态

## 情绪状态解读

- **极度贪婪 (≥80)**: 市场过热，风险高，考虑减仓
- **贪婪 (60-79)**: 市场乐观，机会与风险并存
- **中性 (40-59)**: 市场平衡，正常操作
- **恐惧 (20-39)**: 市场悲观，可能有布局机会
- **极度恐惧 (<20)**: 市场恐慌，可能是买入机会

## 市场环境分析模块（新增）

### 市场环境判断

```python
from market_environment import MarketEnvironmentAnalyzer

# 创建分析器
analyzer = MarketEnvironmentAnalyzer()

# 1. 大盘趋势分析
trend_result = analyzer.analyze_market_trend(index_code='sh.000001', days=60)
print(f"市场状态: {trend_result.get('state_description', '未知')}")
print(f"趋势强度: {trend_result.get('trend_strength', '未知')}")
print(f"风险等级: {trend_result.get('risk_level', '未知')}")
print(f"建议操作: {trend_result.get('suggested_action', '未知')}")

# 2. 板块轮动分析
sector_result = analyzer.analyze_sector_rotation()
print(f"\n强势板块: {[s['sector_name'] for s in sector_result.get('strong_sectors', [])]}")
print(f"弱势板块: {[s['sector_name'] for s in sector_result.get('weak_sectors', [])]}")
print(f"市场特征: {sector_result.get('market_character', '未知')}")

# 3. 综合市场环境分析
comprehensive_result = analyzer.comprehensive_market_analysis()

# 显示综合评估
if 'overall_assessment' in comprehensive_result:
    assessment = comprehensive_result['overall_assessment']
    print(f"\n综合评分: {assessment.get('composite_score', 'N/A')}/100")
    print(f"环境评级: {assessment.get('environment_rating', '未知')}")
    print(f"操作策略: {assessment.get('operating_strategy', {}).get('strategy', '未知')}")
    print(f"建议仓位: {assessment.get('operating_strategy', {}).get('suggested_position', '未知')}")

# 显示操作建议
if 'recommendations' in comprehensive_result:
    print("\n操作建议:")
    for rec in comprehensive_result['recommendations']:
        print(f"  {rec}")
```

### 市场环境判断标准

#### 1. 牛市特征（综合评分≥70）：
- 大盘持续上涨（20日涨幅>10%）
- 均线呈多头排列
- 成交量稳步放大
- 多个板块轮番上涨
- 市场情绪乐观

#### 2. 熊市特征（综合评分<40）：
- 大盘持续下跌（20日跌幅>10%）
- 均线呈空头排列
- 成交量萎缩
- 多数板块下跌
- 市场情绪悲观

#### 3. 震荡市特征（综合评分40-70）：
- 大盘在一定区间内波动
- 均线纠缠
- 成交量不稳定
- 板块分化明显
- 市场情绪中性

### 环境因子对分析的影响

#### 牛市环境：
- ✅ 可积极寻找买入机会
- ✅ 关注成长股和强势板块
- ✅ 适当提高仓位
- ⚠️ 注意过热风险，设好止损

#### 熊市环境：
- ⚠️ 以风险控制为主
- ⚠️ 减少操作频率
- ⚠️ 关注防御性板块
- 💡 可寻找超跌反弹机会

#### 震荡市环境：
- 🔄 高抛低吸，波段操作
- 🔄 关注结构性机会
- 🔄 控制仓位，快进快出
- 📊 密切观察突破方向

### 环境判断在股票分析中的应用

```python
def analyze_stock_with_market_context(stock_code, market_analysis):
    """
    结合市场环境分析个股
    
    Parameters:
    -----------
    stock_code : str
        股票代码
    market_analysis : dict
        市场环境分析结果
        
    Returns:
    --------
    dict : 结合市场环境的个股分析
    """
    # 获取市场环境评级
    env_rating = market_analysis.get('overall_assessment', {}).get('environment_rating', '中性')
    composite_score = market_analysis.get('overall_assessment', {}).get('composite_score', 50)
    
    # 根据市场环境调整分析策略
    if env_rating in ['良好', '偏好'] and composite_score >= 60:
        # 牛市或偏好环境：积极分析
        analysis_mode = '积极'
        risk_tolerance = '较高'
        position_suggestion = '可考虑建仓或加仓'
        
    elif env_rating in ['偏差', '差'] and composite_score < 40:
        # 熊市或偏差环境：保守分析
        analysis_mode = '保守'
        risk_tolerance = '较低'
        position_suggestion = '建议观望或轻仓'
        
    else:
        # 震荡市或中性环境：谨慎分析
        analysis_mode = '谨慎'
        risk_tolerance = '中等'
        position_suggestion = '小仓位参与，设好止损'
    
    # 获取个股技术分析（使用technical-analysis技能）
    from technical_analysis import analyze_stock_technicals
    technical_analysis = analyze_stock_technicals(stock_code)
    
    # 结合市场环境给出最终建议
    final_recommendation = adjust_recommendation_by_market(
        technical_analysis, env_rating, composite_score
    )
    
    return {
        'stock_code': stock_code,
        'market_environment': env_rating,
        'market_score': composite_score,
        'analysis_mode': analysis_mode,
        'risk_tolerance': risk_tolerance,
        'position_suggestion': position_suggestion,
        'technical_analysis': technical_analysis,
        'final_recommendation': final_recommendation,
        'market_context_notes': get_market_context_notes(env_rating, composite_score)
    }

def adjust_recommendation_by_market(tech_analysis, env_rating, market_score):
    """根据市场环境调整技术分析建议"""
    tech_signal = tech_analysis.get('signal', '中性')
    tech_strength = tech_analysis.get('strength', 50)
    
    # 基础建议
    if tech_signal == '买入' and tech_strength >= 70:
        base_recommendation = '考虑买入'
    elif tech_signal == '卖出' and tech_strength >= 70:
        base_recommendation = '考虑卖出'
    else:
        base_recommendation = '观望'
    
    # 根据市场环境调整
    if env_rating in ['良好', '偏好'] and market_score >= 60:
        # 牛市环境：强化买入信号，弱化卖出信号
        if tech_signal == '买入':
            return f"📈 市场环境支持，{base_recommendation}"
        elif tech_signal == '卖出':
            return f"⚠️ 虽有卖出信号，但市场环境较好，可考虑减仓而非清仓"
        else:
            return f"📊 市场环境较好，{base_recommendation}"
    
    elif env_rating in ['偏差', '差'] and market_score < 40:
        # 熊市环境：强化卖出信号，弱化买入信号
        if tech_signal == '卖出':
            return f"📉 市场环境较差，{base_recommendation}"
        elif tech_signal == '买入':
            return f"⚠️ 虽有买入信号，但市场环境较差，建议谨慎或观望"
        else:
            return f"🛡️ 市场环境较差，{base_recommendation}"
    
    else:
        # 震荡市环境：保持中性
        return base_recommendation

def get_market_context_notes(env_rating, market_score):
    """获取市场环境说明"""
    notes = []
    
    if env_rating == '良好' and market_score >= 70:
        notes.append("✅ 市场环境良好，可积极寻找机会")
        notes.append("✅ 趋势交易策略效果较好")
        notes.append("⚠️ 注意不要追高，设好止损")
    
    elif env_rating == '差' and market_score < 40:
        notes.append("⚠️ 市场环境较差，以风险控制为主")
        notes.append("⚠️ 减少操作频率，保持轻仓")
        notes.append("💡 可关注超跌反弹机会")
    
    elif env_rating == '中性':
        notes.append("🔄 市场环境中性，适合波段操作")
        notes.append("🔄 关注结构性机会")
        notes.append("📊 密切观察市场突破方向")
    
    else:
        notes.append("📈 市场环境偏好，可适度参与")
        notes.append("📉 市场环境偏差，需谨慎操作")
    
    return notes
```

### 环境判断的重要性

#### 避免昨天的错误：
昨天在市场明显下跌时建议"强烈买入"，就是因为：
1. ❌ 没有判断市场环境（大盘下跌）
2. ❌ 忽视板块表现（多数板块下跌）
3. ❌ 机械依赖技术指标（只看个股不看大盘）

#### 正确的分析流程：
1. ✅ **先看市场环境**：判断大盘趋势、板块轮动
2. ✅ **再看个股技术**：在正确市场环境下分析个股
3. ✅ **结合风险评估**：根据环境调整风险控制
4. ✅ **给出合理建议**：考虑环境因素的建议

### 环境判断的更新频率

1. **每日开盘前**：判断当日市场环境基调
2. **盘中关键时点**：10:30, 13:30 检查环境变化
3. **收盘后总结**：评估全天环境变化
4. **重大事件时**：政策发布、经济数据公布等

### 环境判断的数据源

1. **大盘指数**：上证指数、深证成指、创业板指
2. **板块指数**：各行业板块指数
3. **市场宽度**：上涨下跌股票比例
4. **资金流向**：主力资金、北向资金
5. **情绪指标**：恐慌贪婪指数、舆情情绪

### 环境判断的输出格式

```python
{
    "market_environment": {
        "trend_analysis": {
            "market_state": "bull/bear/sideways",
            "trend_strength": "强/中/弱",
            "risk_level": "高/中/低",
            "suggested_action": "具体操作建议"
        },
        "sector_analysis": {
            "strong_sectors": ["板块1", "板块2"],
            "weak_sectors": ["板块3", "板块4"],
            "market_character": "普涨/普跌/结构性"
        },
        "overall_assessment": {
            "composite_score": 75.5,
            "environment_rating": "良好/偏好/中性/偏差/差",
            "operating_strategy": {
                "strategy": "积极进攻/稳健参与/适度参与/谨慎操作/观望为主",
                "suggested_position": "建议仓位",
                "focus": "关注方向",
                "risk_control": "风控要点"
            }
        }
    }
}
```
