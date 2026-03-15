#!/usr/bin/env python3
"""
简化版真实新闻监控
确保基础功能可靠
"""

import requests
import json
import re
from datetime import datetime

class SimpleNewsMonitor:
    def __init__(self):
        # 使用可靠的新闻源API
        self.sources = {
            '新浪财经': 'https://interface.sina.cn/news/wap/fymap2020_data.d.json',
            '东方财富快讯': 'https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_50_1_.html'
        }
        
        # 重大利好关键词（更严格）
        self.major_keywords = [
            # 业绩大幅增长
            '业绩预增超过50%', '净利润翻倍', '营收增长100%',
            # 重大合同
            '签订重大合同', '中标超10亿元', '获得大额订单',
            # 政策重大支持
            '国家级政策', '获得重大补贴', '入选国家级项目',
            # 技术重大突破
            '技术突破', '首款产品', '重大专利获批',
            # 资本重大运作
            '大股东增持超5%', '重大资产重组', '并购重组获批'
        ]
    
    def fetch_sina_news(self):
        """从新浪财经获取新闻"""
        try:
            url = "https://interface.sina.cn/news/wap/fymap2020_data.d.json"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                news_list = []
                
                # 解析新浪数据结构
                if 'data' in data and 'list' in data['data']:
                    for item in data['data']['list']:
                        title = item.get('title', '')
                        url = item.get('url', '')
                        time = item.get('ctime', '')
                        
                        if title and url:
                            news_list.append({
                                'title': title,
                                'url': f"https:{url}" if url.startswith('//') else url,
                                'source': '新浪财经',
                                'time': time
                            })
                
                return news_list
            return []
        except Exception as e:
            print(f"新浪财经新闻获取失败: {e}")
            return []
    
    def fetch_eastmoney_news(self):
        """从东方财富获取快讯"""
        try:
            url = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_50_1_.html"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://kuaixun.eastmoney.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # 东方财富返回的是JSONP格式
                content = response.text
                if 'var ajaxResult=' in content:
                    json_str = content.split('var ajaxResult=')[1].split(';')[0]
                    data = json.loads(json_str)
                    
                    news_list = []
                    for item in data.get('LivesList', []):
                        title = item.get('title', '')
                        content = item.get('digest', '')
                        time = item.get('showtime', '')
                        
                        if title:
                            news_list.append({
                                'title': title,
                                'content': content,
                                'source': '东方财富快讯',
                                'time': time,
                                'url': f"https://kuaixun.eastmoney.com/"
                            })
                    
                    return news_list
            return []
        except Exception as e:
            print(f"东方财富新闻获取失败: {e}")
            return []
    
    def is_truly_major_positive(self, title, content=''):
        """严格判断是否为真正重大利好"""
        # 排除普通消息
        exclude_words = ['或', '可能', '预计', '传闻', '网传', '分析', '认为']
        for word in exclude_words:
            if word in title:
                return False
        
        # 必须包含具体数字或明确表述
        number_patterns = [
            r'(\d+)%', r'(\d+)倍', r'(\d+)亿元', r'(\d+)亿',
            r'翻倍', r'翻番', r'大幅', r'显著', r'明显'
        ]
        
        has_number = False
        for pattern in number_patterns:
            if re.search(pattern, title) or (content and re.search(pattern, content)):
                has_number = True
                break
        
        if not has_number:
            return False
        
        # 检查是否包含重大利好关键词
        positive_count = 0
        for keyword in self.major_keywords:
            if keyword in title or (content and keyword in content):
                positive_count += 1
        
        return positive_count >= 1
    
    def analyze_news(self, news):
        """分析新闻影响"""
        title = news['title']
        content = news.get('content', '')
        
        # 提取关键信息
        impact = {
            'level': '待定',
            'sectors': [],
            'stocks': [],
            'analysis': '',
            'suggestion': ''
        }
        
        # 判断影响级别
        if any(word in title for word in ['重大', '突破', '首款', '国家级', '战略', '翻倍', '翻番']):
            impact['level'] = '重大'
        elif any(word in title for word in ['预增', '中标', '订单', '合作', '增长', '提升']):
            impact['level'] = '中等'
        else:
            impact['level'] = '一般'
        
        # 提取股票代码
        stock_pattern = r'([0-9]{6})\.?(SH|SZ|HK)?'
        matches = re.findall(stock_pattern, title + ' ' + content)
        for match in matches:
            code = match[0]
            market = match[1] if match[1] else 'SZ' if code.startswith('00') or code.startswith('30') else 'SH'
            impact['stocks'].append(f"{code}.{market}")
        
        # 分析板块
        sector_map = {
            '新能源': ['电池', '光伏', '风电', '新能源', '锂电', '储能'],
            '科技': ['芯片', '半导体', '人工智能', 'AI', '5G', '云计算'],
            '医药': ['医药', '医疗', '生物', '疫苗', '创新药'],
            '消费': ['消费', '白酒', '食品', '零售', '电商', '家电'],
            '金融': ['银行', '保险', '证券', '金融', '信托'],
            '周期': ['化工', '钢铁', '有色', '煤炭', '建材', '房地产']
        }
        
        for sector, keywords in sector_map.items():
            for keyword in keywords:
                if keyword in title or keyword in content:
                    if sector not in impact['sectors']:
                        impact['sectors'].append(sector)
                    break
        
        # 生成分析
        if impact['level'] == '重大':
            impact['analysis'] = f"该消息属于重大级别利好，可能对市场产生显著影响"
            impact['suggestion'] = f"建议重点关注，可考虑适当布局"
        elif impact['level'] == '中等':
            impact['analysis'] = f"该消息属于中等级别利好，对相关板块有积极影响"
            impact['suggestion'] = f"建议关注，可选择性参与"
        else:
            impact['analysis'] = f"该消息影响有限，建议保持关注"
            impact['suggestion'] = f"建议观察，谨慎参与"
        
        return impact
    
    def format_report(self, news, impact):
        """生成格式化报告"""
        report = f"""📈 真实重大利好监控报告
════════════════════════════════════════
🕐 监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📰 新闻标题: {news['title']}
🔗 新闻来源: {news['source']}
🌐 信息来源: {news.get('url', '暂无直接链接')}
⏰ 发布时间: {news.get('time', '未知')}
────────────────────────────────────────
📊 影响分析:
• 影响级别: {impact['level']}
• 利好板块: {', '.join(impact['sectors']) if impact['sectors'] else '待进一步分析'}
• 关注个股: {', '.join(impact['stocks']) if impact['stocks'] else '待进一步分析'}
• 具体分析: {impact['analysis']}

💡 操作建议:
{impact['suggestion']}
════════════════════════════════════════
"""
        return report
    
    def run(self):
        """运行监控"""
        print(f"开始真实新闻监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        all_reports = []
        
        # 从新浪财经获取
        print("1. 从新浪财经获取新闻...")
        sina_news = self.fetch_sina_news()
        print(f"   获取到 {len(sina_news)} 条新闻")
        
        for news in sina_news[:10]:  # 只检查前10条
            if self.is_truly_major_positive(news['title']):
                impact = self.analyze_news(news)
                if impact['level'] in ['重大', '中等']:
                    report = self.format_report(news, impact)
                    all_reports.append(report)
        
        # 从东方财富获取
        print("2. 从东方财富获取快讯...")
        em_news = self.fetch_eastmoney_news()
        print(f"   获取到 {len(em_news)} 条快讯")
        
        for news in em_news[:10]:  # 只检查前10条
            if self.is_truly_major_positive(news['title'], news.get('content', '')):
                impact = self.analyze_news(news)
                if impact['level'] in ['重大', '中等']:
                    report = self.format_report(news, impact)
                    all_reports.append(report)
        
        return all_reports

def main():
    monitor = SimpleNewsMonitor()
    reports = monitor.run()
    
    if reports:
        print(f"\n🎯 发现 {len(reports)} 条真实重大利好消息:")
        for i, report in enumerate(reports, 1):
            print(f"\n{'='*60}")
            print(f"报告 #{i}:")
            print(report)
        
        # 保存报告
        with open('monitoring_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'monitor_time': datetime.now().isoformat(),
                'report_count': len(reports),
                'reports': reports
            }, f, ensure_ascii=False, indent=2)
        print(f"\n报告已保存到: monitoring_results.json")
    else:
        print("\n📭 本次监控未发现真实重大利好消息")
        print("说明: 监控系统运行正常，但当前时段无符合标准的重大利好")
    
    return reports

if __name__ == "__main__":
    main()