#!/usr/bin/env python3
"""
真实新闻监控脚本
只监控真实、重大的利好消息
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class RealNewsMonitor:
    def __init__(self):
        self.news_sources = {
            '财联社': 'https://www.cls.cn/api/sw?app=CailianpressWeb&os=web&sv=7.7.5',
            '证券时报': 'https://news.stcn.com/ajax/loadmore.html',
            '上海证券报': 'https://news.cnstock.com/newslist'
        }
        
        # 重大利好关键词
        self.major_positive_keywords = [
            # 业绩相关
            '业绩预增', '净利润增长', '营收大增', '扭亏为盈', '超预期',
            # 合同订单
            '签订合同', '中标', '获得订单', '大单', '战略合作',
            # 政策支持
            '政策利好', '补贴', '扶持', '试点', '国家级',
            # 技术突破
            '突破', '专利', '研发成功', '创新', '首款',
            # 资本运作
            '增持', '回购', '并购', '重组', '收购',
            # 行业认证
            '认证', '资质', '许可', '批准', '通过'
        ]
        
        # 排除虚假或普通消息
        self.exclude_keywords = [
            '传闻', '网传', '或', '可能', '预计', '分析称',
            '小幅', '微增', '略有', '普通', '常规'
        ]
    
    def fetch_cls_news(self) -> List[Dict]:
        """从财联社获取新闻"""
        try:
            url = "https://www.cls.cn/api/sw"
            params = {
                'app': 'CailianpressWeb',
                'os': 'web',
                'sv': '7.7.5'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.cls.cn/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # 解析财联社数据结构
                news_list = []
                # 这里需要根据实际API响应结构解析
                return news_list
            return []
        except Exception as e:
            print(f"财联社新闻获取失败: {e}")
            return []
    
    def fetch_stcn_news(self) -> List[Dict]:
        """从证券时报获取新闻"""
        try:
            url = "https://news.stcn.com/ajax/loadmore.html"
            params = {
                'type': 'getmore',
                'page': '1',
                'cateid': '176'  # 财经新闻分类
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://news.stcn.com/'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                # 解析HTML响应
                return self.parse_stcn_html(response.text)
            return []
        except Exception as e:
            print(f"证券时报新闻获取失败: {e}")
            return []
    
    def parse_stcn_html(self, html: str) -> List[Dict]:
        """解析证券时报HTML"""
        news_list = []
        try:
            # 简单的HTML解析
            import re
            pattern = r'<a href="([^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html)
            
            for match in matches:
                url, title = match
                if 'http' not in url:
                    url = f"https://news.stcn.com{url}"
                
                news_list.append({
                    'title': title.strip(),
                    'url': url,
                    'source': '证券时报',
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        except Exception as e:
            print(f"HTML解析失败: {e}")
        
        return news_list
    
    def is_major_positive(self, title: str, content: str = "") -> bool:
        """判断是否为重大利好"""
        title_lower = title.lower()
        
        # 排除虚假或普通消息
        for exclude in self.exclude_keywords:
            if exclude in title:
                return False
        
        # 检查是否包含重大利好关键词
        positive_count = 0
        for keyword in self.major_positive_keywords:
            if keyword in title:
                positive_count += 1
        
        # 至少包含一个重大利好关键词
        if positive_count >= 1:
            # 进一步检查具体内容（如果有）
            if content:
                # 检查具体数字或比例
                number_patterns = [
                    r'增长(\d+)%', r'增长(\d+)倍', r'(\d+)亿元',
                    r'增长超过(\d+)%', r'预增(\d+)%', r'中标(\d+)亿'
                ]
                for pattern in number_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        for match in matches:
                            try:
                                num = float(match)
                                # 如果是百分比，检查是否大于50%
                                if '%' in pattern and num >= 50:
                                    return True
                                # 如果是金额，检查是否大于10亿
                                elif '亿' in pattern and num >= 10:
                                    return True
                            except:
                                pass
            
            return True
        
        return False
    
    def get_news_content(self, url: str) -> str:
        """获取新闻详细内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # 简单的正文提取
                text = response.text
                # 移除HTML标签
                text = re.sub(r'<[^>]+>', ' ', text)
                # 移除多余空格
                text = re.sub(r'\s+', ' ', text)
                return text[:500]  # 只返回前500字符
        except Exception as e:
            print(f"获取新闻内容失败 {url}: {e}")
        
        return ""
    
    def analyze_impact(self, title: str, content: str) -> Dict:
        """分析新闻影响"""
        impact = {
            'level': '中等',  # 默认中等
            'sectors': [],
            'stocks': [],
            'analysis': '',
            'suggestion': ''
        }
        
        # 根据关键词判断影响级别
        if any(word in title for word in ['重大', '突破', '首款', '国家级', '战略']):
            impact['level'] = '重大'
        elif any(word in title for word in ['预增', '中标', '订单', '合作']):
            impact['level'] = '中等'
        else:
            impact['level'] = '一般'
        
        # 分析受益板块（简化版）
        sector_keywords = {
            '新能源': ['电池', '光伏', '风电', '新能源', '锂电'],
            '科技': ['芯片', '半导体', '人工智能', 'AI', '5G'],
            '医药': ['医药', '医疗', '生物', '疫苗', '创新药'],
            '消费': ['消费', '白酒', '食品', '零售', '电商'],
            '金融': ['银行', '保险', '证券', '金融'],
            '周期': ['化工', '钢铁', '有色', '煤炭', '建材']
        }
        
        for sector, keywords in sector_keywords.items():
            for keyword in keywords:
                if keyword in title or keyword in content:
                    if sector not in impact['sectors']:
                        impact['sectors'].append(sector)
        
        # 提取可能受益的股票（简化版）
        stock_pattern = r'([0-9]{6})\.(SH|SZ|HK)'
        stock_matches = re.findall(stock_pattern, content)
        for code, market in stock_matches:
            impact['stocks'].append(f"{code}.{market}")
        
        # 生成分析和建议
        impact['analysis'] = f"该消息属于{impact['level']}级别利好"
        if impact['sectors']:
            impact['analysis'] += f"，主要利好{','.join(impact['sectors'])}板块"
        
        impact['suggestion'] = f"建议关注{impact['level']}利好相关的投资机会"
        
        return impact
    
    def format_report(self, news: Dict, impact: Dict) -> str:
        """格式化监控报告"""
        report = f"""📈 真实重大利好监控报告
════════════════════════════════════════
🕐 监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📰 新闻标题: {news['title']}
🔗 新闻来源: {news['source']}
🌐 新闻链接: {news['url']}
⏰ 发布时间: {news.get('time', '未知')}
────────────────────────────────────────
📊 影响分析:
• 影响级别: {impact['level']}
• 利好板块: {', '.join(impact['sectors']) if impact['sectors'] else '待分析'}
• 关注个股: {', '.join(impact['stocks']) if impact['stocks'] else '待分析'}
• 具体分析: {impact['analysis']}

💡 操作建议:
{impact['suggestion']}
════════════════════════════════════════
"""
        return report
    
    def run_monitor(self) -> List[str]:
        """运行监控"""
        print(f"开始真实新闻监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_reports = []
        
        # 从各个新闻源获取新闻
        news_sources = [
            self.fetch_stcn_news,  # 先试证券时报
            # self.fetch_cls_news,  # 财联社API需要更复杂处理
        ]
        
        for fetch_func in news_sources:
            try:
                news_list = fetch_func()
                print(f"从{fetch_func.__name__}获取到{len(news_list)}条新闻")
                
                for news in news_list:
                    # 获取新闻内容
                    content = self.get_news_content(news['url'])
                    
                    # 判断是否为重大利好
                    if self.is_major_positive(news['title'], content):
                        print(f"发现重大利好: {news['title']}")
                        
                        # 分析影响
                        impact = self.analyze_impact(news['title'], content)
                        
                        # 只报告重大和中等级别
                        if impact['level'] in ['重大', '中等']:
                            report = self.format_report(news, impact)
                            all_reports.append(report)
                            
            except Exception as e:
                print(f"{fetch_func.__name__}监控失败: {e}")
                continue
        
        return all_reports

def main():
    """主函数"""
    monitor = RealNewsMonitor()
    reports = monitor.run_monitor()
    
    if reports:
        print(f"\n🎯 发现 {len(reports)} 条重大利好消息:")
        for i, report in enumerate(reports, 1):
            print(f"\n{'='*60}")
            print(f"报告 #{i}:")
            print(report)
    else:
        print("本次监控未发现重大利好消息")
    
    return reports

if __name__ == "__main__":
    main()