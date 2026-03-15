---
name: news_analysis
description: "股票新闻资讯分析，包括新闻收集、情感分析、事件影响评估、资讯整合。使用场景：用户需要了解股票相关新闻、分析新闻影响、跟踪重大事件、资讯汇总。"
metadata: { "openclaw": { "emoji": "📰", "requires": { "python": true, "packages": ["pandas", "jieba"] }, "notes": "Baostock不支持新闻数据，需要其他数据源" } }
---

# 新闻资讯分析Skill

股票新闻资讯分析，包括新闻收集、情感分析、事件影响评估、资讯整合。

## 使用场景

✅ **使用此Skill当：**

- "查看股票新闻"
- "分析新闻影响"
- "跟踪重大事件"
- "资讯汇总报告"
- "新闻情感分析"
- "事件驱动分析"

## 分析维度

### 1. 新闻收集
- 实时新闻抓取
- 历史新闻回溯
- 多渠道新闻整合
- 新闻分类整理

### 2. 情感分析
- 新闻情感判断
- 情感强度分析
- 情感趋势跟踪
- 多维度情感评估

### 3. 事件分析
- 重大事件识别
- 事件影响评估
- 事件时间线分析
- 事件关联性分析

### 4. 资讯整合
- 多源资讯汇总
- 资讯优先级排序
- 关键信息提取
- 资讯报告生成

## 命令示例

### 新闻收集

```python
import sys
sys.path.append('/home/openclaw/.openclaw/workspace')
from utils.data_source_manager import get_data_source_manager
import pandas as pd
from datetime import datetime, timedelta

def collect_stock_news(code, days=7):
    """收集股票相关新闻 (使用数据源管理器)"""
    
    try:
        # 获取数据源管理器
        manager = get_data_source_manager()
        
        # 获取新闻数据
        news_list = manager.get_news_data(code, days)
        
        if news_list:
            print(f"✅ 成功获取 {len(news_list)} 条新闻")
            return news_list
        else:
            print("⚠️ 未获取到新闻数据")
            return []
        
    except Exception as e:
        print(f"新闻收集错误: {e}")
        print("提示: 确保已安装akshare (pip install akshare)")
        return []
```

### 新闻情感分析

```python
import jieba
import jieba.analyse

def analyze_news_sentiment(news_list):
    """分析新闻情感"""
    sentiment_results = []
    
    # 情感词典（简化版）
    positive_words = {
        '上涨', '增长', '利好', '突破', '创新高', '推荐', '买入', '看好',
        '机会', '潜力', '优秀', '强劲', '复苏', '改善', '提升', '扩张'
    }
    
    negative_words = {
        '下跌', '下滑', '利空', '风险', '警告', '卖出', '谨慎', '调整',
        '亏损', '问题', '挑战', '压力', '下降', '减少', '收缩', '困难'
    }
    
    for news in news_list:
        text = news['title'] + ' ' + news['content']
        
        # 分词
        words = jieba.lcut(text)
        
        # 计算情感分数
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        if total_words > 0:
            positive_ratio = positive_count / total_words
            negative_ratio = negative_count / total_words
        else:
            positive_ratio = 0
            negative_ratio = 0
        
        # 确定情感倾向
        if positive_ratio > negative_ratio:
            sentiment = '积极'
            score = positive_ratio * 100
        elif negative_ratio > positive_ratio:
            sentiment = '消极'
            score = -negative_ratio * 100
        else:
            sentiment = '中性'
            score = 0
        
        # 计算重要性（基于关键词提取）
        keywords = jieba.analyse.extract_tags(text, topK=5)
        importance = len([kw for kw in keywords if kw in ['业绩', '财报', '收购', '重组', '政策']])
        
        sentiment_results.append({
            'title': news['title'],
            'sentiment': sentiment,
            'score': round(score, 1),
            'importance': importance,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'keywords': keywords
        })
    
    return sentiment_results
```

### 事件影响评估

```python
def assess_event_impact(news_list):
    """评估事件影响"""
    events = []
    
    # 事件类型和影响程度
    event_types = {
        '财报发布': {'impact': 8, 'keywords': ['财报', '业绩', '净利润', '营收']},
        '重大收购': {'impact': 9, 'keywords': ['收购', '并购', '重组', '合并']},
        '政策利好': {'impact': 7, 'keywords': ['政策', '扶持', '补贴', '利好']},
        '产品发布': {'impact': 6, 'keywords': ['新品', '发布', '上市', '推出']},
        '高管变动': {'impact': 5, 'keywords': ['辞职', '任命', '变更', '高管']},
        '诉讼纠纷': {'impact': 7, 'keywords': ['诉讼', '纠纷', '仲裁', '起诉']},
        '监管处罚': {'impact': 8, 'keywords': ['处罚', '监管', '警告', '整改']},
        '合作签约': {'impact': 6, 'keywords': ['合作', '签约', '协议', '战略']}
    }
    
    for news in news_list:
        text = news['title'].lower() + ' ' + news['content'].lower()
        
        detected_events = []
        
        for event_type, event_info in event_types.items():
            for keyword in event_info['keywords']:
                if keyword in text:
                    detected_events.append({
                        'type': event_type,
                        'impact': event_info['impact'],
                        'keyword': keyword
                    })
                    break  # 每个事件类型只匹配一次
        
        if detected_events:
            # 取影响最大的事件
            main_event = max(detected_events, key=lambda x: x['impact'])
            
            events.append({
                'title': news['title'],
                'event_type': main_event['type'],
                'impact_level': main_event['impact'],
                'impact_description': get_impact_description(main_event['impact']),
                'publish_time': news['publish_time']
            })
    
    return events

def get_impact_description(impact_score):
    """获取影响描述"""
    if impact_score >= 9:
        return '重大影响'
    elif impact_score >= 7:
        return '较大影响'
    elif impact_score >= 5:
        return '一般影响'
    else:
        return '轻微影响'
```

### 新闻热度分析

```python
def analyze_news_heat(news_list):
    """分析新闻热度"""
    heat_analysis = {
        'total_news': len(news_list),
        'daily_distribution': {},
        'source_distribution': {},
        'topic_distribution': {},
        'heat_score': 0
    }
    
    if not news_list:
        return heat_analysis
    
    # 按日期分布
    date_counts = {}
    for news in news_list:
        date_str = news['publish_time'].strftime('%Y-%m-%d')
        date_counts[date_str] = date_counts.get(date_str, 0) + 1
    
    heat_analysis['daily_distribution'] = date_counts
    
    # 按来源分布
    source_counts = {}
    for news in news_list:
        source = news.get('source', '未知')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    heat_analysis['source_distribution'] = source_counts
    
    # 热点话题识别
    all_titles = ' '.join([news['title'] for news in news_list])
    keywords = jieba.analyse.extract_tags(all_titles, topK=10)
    
    topic_counts = {}
    for keyword in keywords:
        count = sum(1 for news in news_list if keyword in news['title'])
        topic_counts[keyword] = count
    
    heat_analysis['topic_distribution'] = topic_counts
    
    # 计算热度分数
    # 基于新闻数量、时间集中度、来源多样性
    news_count_score = min(len(news_list) * 10, 100)
    
    # 时间集中度（最近3天新闻占比）
    recent_days = 3
    recent_count = sum(1 for news in news_list if 
                      (datetime.now() - news['publish_time']).days <= recent_days)
    time_concentration = recent_count / len(news_list) if news_list else 0
    time_score = time_concentration * 100
    
    # 来源多样性
    source_diversity = len(source_counts) / len(news_list) * 10 if news_list else 0
    source_score = min(source_diversity * 100, 100)
    
    # 综合热度分数
    heat_score = (news_count_score * 0.4 + time_score * 0.3 + source_score * 0.3)
    heat_analysis['heat_score'] = round(heat_score, 1)
    
    return heat_analysis
```

### 资讯整合报告

```python
def generate_news_report(code, days=7):
    """生成资讯整合报告"""
    report = {
        '股票代码': code,
        '分析期间': f'最近{days}天',
        '新闻摘要': [],
        '情感分析': {},
        '事件分析': [],
        '热度分析': {},
        '投资建议': ''
    }
    
    try:
        # 收集新闻
        news_list = collect_stock_news(code, days)
        
        if not news_list:
            report['新闻摘要'] = [{'title': '暂无相关新闻', 'content': ''}]
            return report
        
        # 新闻摘要（取最重要的5条）
        sorted_news = sorted(news_list, key=lambda x: x.get('importance', 0), reverse=True)
        top_news = sorted_news[:5]
        
        report['新闻摘要'] = [
            {
                'title': news['title'],
                'source': news['source'],
                'time': news['publish_time'].strftime('%Y-%m-%d %H:%M'),
                'summary': extract_summary(news['content'])
            }
            for news in top_news
        ]
        
        # 情感分析
        sentiment_results = analyze_news_sentiment(news_list)
        
        sentiment_summary = {
            '积极新闻数': sum(1 for s in sentiment_results if s['sentiment'] == '积极'),
            '消极新闻数': sum(1 for s in sentiment_results if s['sentiment'] == '消极'),
            '中性新闻数': sum(1 for s in sentiment_results if s['sentiment'] == '中性'),
            '平均情感分数': sum(s['score'] for s in sentiment_results) / len(sentiment_results) if sentiment_results else 0,
            '主要关键词': get_top_keywords(sentiment_results)
        }
        
        report['情感分析'] = sentiment_summary
        
        # 事件分析
        events = assess_event_impact(news_list)
        report['事件分析'] = events
        
        # 热度分析
        heat_analysis = analyze_news_heat(news_list)
        report['热度分析'] = heat_analysis
        
        # 生成投资建议
        report['投资建议'] = generate_investment_advice(sentiment_summary, events, heat_analysis)
        
    except Exception as e:
        report['错误信息'] = str(e)
    
    return report

def extract_summary(content, max_length=100):
    """提取新闻摘要"""
    if len(content) <= max_length:
        return content
    
    # 简单截取
    summary = content[:max_length] + '...'
    
    # 尝试在句号处截断
    last_period = summary.rfind('。')
    if last_period > max_length * 0.5:
        summary = summary[:last_period + 1]
    
    return summary

def get_top_keywords(sentiment_results, top_n=5):
    """获取主要关键词"""
    all_keywords = []
    for result in sentiment_results:
        all_keywords.extend(result['keywords'])
    
    # 统计词频
    from collections import Counter
    keyword_counts = Counter(all_keywords)
    
    return [keyword for keyword, _ in keyword_counts.most_common(top_n)]

def generate_investment_advice(sentiment_summary, events, heat_analysis):
    """生成投资建议"""
    advice_parts = []
    
    # 基于情感分析
    positive_ratio = sentiment_summary['积极新闻数'] / max(sum([
        sentiment_summary['积极新闻数'],
        sentiment_summary['消极新闻数'],
        sentiment_summary['中性新闻数']
    ]), 1)
    
    if positive_ratio > 0.6:
        advice_parts.append("📰 舆情积极，正面新闻占主导")
    elif positive_ratio < 0.3:
        advice_parts.append("📰 舆情偏消极，负面消息较多")
    else:
        advice_parts.append("📰 舆情中性，正负面消息平衡")
    
    # 基于事件分析
    if events:
        high_impact_events = [e for e in events if e['impact_level'] >= 7]
        if high_impact_events:
            event_types = ', '.join(set(e['event_type'] for e in high_impact_events))
            advice_parts.append(f"⚠️ 近期有重大事件: {event_types}")
    
    # 基于热度分析
    heat_score = heat_analysis.get('heat_score', 0)
    if heat_score > 70:
        advice_parts.append("🔥 新闻热度高，市场关注度提升")
    elif heat_score < 30:
        advice_parts.append("❄️ 新闻热度低，市场关注度一般")
    
    # 综合建议
    if not advice_parts:
        advice = "建议关注后续新闻动态"
    else:
        advice = ' '.join(advice_parts)
    
    return advice
```

### 实时新闻监控

```python
def monitor_real_time_news(code, check_interval=300):
    """实时新闻监控"""
    import time
    from datetime import datetime
    
    print(f"开始监控 {code} 的实时新闻...")
    print("按Ctrl+C停止监控")
    
    last_news_count = 0
    
    try:
        while True:
            # 获取最新新闻
            news_list = collect_stock_news(code, days=1)
            current_count = len(news_list)
            
            if current_count > last_news_count:
                new_news = news_list[last_news_count:]
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 发现 {len(new_news)} 条新新闻:")
                
                for news in new_news:
                    sentiment = analyze_news_sentiment([news])[0]
                    
                    print(f"  📰 {news['title']}")
                    print(f"     情感: {sentiment['sentiment']} ({sentiment['score']})")
                    print(f"     来源: {news['source']}")
                    print(f"     时间: {news['publish_time'].strftime('%H:%M')}")
                    print()
                
                last_news_count = current_count
            
            # 等待指定时间
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n监控已停止")
```

## 安装依赖

```bash
pip install akshare pandas requests beautifulsoup4 jieba
```

## 使用示例

```python
# 生成新闻分析报告
code = "000001"
report = generate_news_report(code, days=7)

print("="*60)
print(f"{code} 新闻资讯分析报告")
print(f"分析期间: {report['分析期间']}")
print("="*60)

print("\n📰 重要新闻摘要:")
for i, news in enumerate(report['新闻摘要'], 1):
    print(f"{i}. {news['title']}")
    print(f"   来源: {news['source']} | 时间: {news['time']}")
    print(f"   摘要: {news['summary']}")
    print()

print("\n😊 情感分析:")
sentiment = report['情感分析']
print(f"   积极新闻: {sentiment['积极新闻数']}条")
print(f"   消极新闻: {sentiment['消极新闻数']}条")
print(f"   中性新闻: {sentiment['中性新闻数']}条")
print(f"   平均情感分数: {sentiment['平均情感分数']:.1f}")
print(f"   主要关键词: {', '.join(sentiment['主要关键词'])}")

print("\n⚡ 重大事件:")
events = report['事件分析']
if events:
    for event in events[:3]:  # 显示最重要的3个事件
        print(f"   • {event['title']}")
        print(f"     类型: {event['event_type']} | 影响: {event['impact_description']}")
else:
    print("   近期无重大事件")

print(f"\n💡 投资建议: {report['投资建议']}")
print("="*60)
```

## 输出格式