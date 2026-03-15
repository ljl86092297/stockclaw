#!/usr/bin/env python3
"""
港股实时数据分析脚本
用于分析狮滕股份突然拉升原因
"""

import requests
import re
import json
from datetime import datetime

class HKStockAnalyzer:
    def __init__(self, stock_code):
        self.stock_code = stock_code
        self.base_url = "https://hq.sinajs.cn"
        
    def get_realtime_data(self):
        """获取港股实时数据"""
        try:
            url = f"{self.base_url}/list=rt_hk{self.stock_code}"
            headers = {
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.text
                
                # 解析数据格式: var hq_str_rt_hk00700="腾讯控股,335.200,336.000,...";
                if 'hq_str_rt_hk' in data:
                    content = data.split('"')[1]
                    parts = content.split(',')
                    
                    if len(parts) >= 10:
                        return {
                            'name': parts[0],  # 股票名称
                            'current': parts[1],  # 当前价
                            'last_close': parts[2],  # 昨收
                            'open': parts[3],  # 今开
                            'high': parts[4],  # 最高
                            'low': parts[5],  # 最低
                            'volume': parts[6],  # 成交量(股)
                            'turnover': parts[7],  # 成交额(港元)
                            'buy_price': parts[8],  # 买一价
                            'sell_price': parts[9],  # 卖一价
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
            return None
        except Exception as e:
            print(f"获取实时数据失败: {e}")
            return None
    
    def search_hkex_announcements(self, company_name):
        """搜索港交所公告（模拟，实际需要API）"""
        print(f"\n🔍 建议手动搜索港交所公告:")
        print(f"   网址: https://www1.hkexnews.hk/search/titlesearch.xhtml")
        print(f"   搜索词: {company_name}")
        print(f"   时间范围: 最近3天")
        
        return {
            'suggestion': f"请访问港交所披露易搜索 {company_name} 的最新公告",
            'url': 'https://www1.hkexnews.hk/search/titlesearch.xhtml'
        }
    
    def analyze_price_action(self, data, user_input):
        """分析价格行为"""
        if not data:
            return None
        
        try:
            current_price = float(data['current'])
            open_price = float(data['open'])
            last_close = float(data['last_close'])
            high_price = float(data['high'])
            low_price = float(data['low'])
            volume = int(data['volume'])
            
            # 计算涨跌幅
            change_from_open = ((current_price - open_price) / open_price) * 100
            change_from_close = ((current_price - last_close) / last_close) * 100
            
            # 分析成交量
            volume_analysis = "正常"
            if volume > 100000000:  # 超过1亿股
                volume_analysis = "异常放大"
            elif volume > 50000000:  # 超过5千万股
                volume_analysis = "明显放量"
            elif volume < 1000000:  # 少于100万股
                volume_analysis = "成交清淡"
            
            # 分析价格位置
            price_position = ""
            range_high_low = high_price - low_price
            if current_price > (high_price - range_high_low * 0.2):
                price_position = "接近日内高点"
            elif current_price < (low_price + range_high_low * 0.2):
                price_position = "接近日内低点"
            else:
                price_position = "处于日内中间位置"
            
            return {
                'current_price': current_price,
                'change_from_open_pct': change_from_open,
                'change_from_close_pct': change_from_close,
                'volume_analysis': volume_analysis,
                'volume': volume,
                'price_position': price_position,
                'day_range': f"{low_price:.3f} - {high_price:.3f}",
                'range_pct': ((high_price - low_price) / last_close) * 100
            }
        except Exception as e:
            print(f"价格分析失败: {e}")
            return None
    
    def assess_risk_level(self, analysis, user_context):
        """评估风险等级"""
        if not analysis:
            return "未知"
        
        risk_score = 0
        reasons = []
        
        # 涨幅过大风险
        if analysis['change_from_open_pct'] > 15:
            risk_score += 3
            reasons.append(f"涨幅过大({analysis['change_from_open_pct']:.1f}%)")
        elif analysis['change_from_open_pct'] > 8:
            risk_score += 2
            reasons.append(f"涨幅较大({analysis['change_from_open_pct']:.1f}%)")
        elif analysis['change_from_open_pct'] > 3:
            risk_score += 1
        
        # 成交量风险
        if analysis['volume_analysis'] == "异常放大":
            risk_score += 2
            reasons.append("成交量异常放大")
        elif analysis['volume_analysis'] == "明显放量":
            risk_score += 1
        
        # 价格位置风险
        if "接近日内高点" in analysis['price_position']:
            risk_score += 2
            reasons.append("价格接近日内高点")
        
        # 波动性风险
        if analysis['range_pct'] > 10:
            risk_score += 2
            reasons.append(f"日内波动较大({analysis['range_pct']:.1f}%)")
        
        # 确定风险等级
        if risk_score >= 5:
            risk_level = "高风险"
        elif risk_score >= 3:
            risk_level = "中高风险"
        elif risk_score >= 2:
            risk_level = "中等风险"
        elif risk_score >= 1:
            risk_level = "中低风险"
        else:
            risk_level = "低风险"
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'reasons': reasons,
            'assessment': f"综合风险: {risk_level} (评分: {risk_score}/10)"
        }
    
    def generate_trading_plan(self, analysis, risk_assessment, user_context):
        """生成交易计划"""
        if not analysis:
            return None
        
        current_price = analysis['current_price']
        risk_level = risk_assessment['risk_level']
        
        # 根据风险等级制定计划
        if risk_level in ["高风险", "中高风险"]:
            return {
                'recommendation': "不建议追高",
                'reason': f"风险等级过高({risk_level})",
                'if_participate': {
                    'buy_price': f"{current_price * 0.97:.3f} HKD (等待3%回调)",
                    'stop_loss': f"{current_price * 0.92:.3f} HKD (-8%)",
                    'target_price': f"{current_price * 1.08:.3f} HKD (+8%)",
                    'position': "不超过3%",
                    'holding_period': "不超过1个交易日"
                }
            }
        elif risk_level == "中等风险":
            return {
                'recommendation': "谨慎考虑，小仓位参与",
                'reason': "中等风险，需要严格控制仓位",
                'buy_price': f"{current_price * 0.98:.3f} HKD (等待2%回调)",
                'stop_loss': f"{current_price * 0.95:.3f} HKD (-5%)",
                'target_price': f"{current_price * 1.10:.3f} HKD (+10%)",
                'position': "不超过5%",
                'holding_period': "1-2个交易日"
            }
        else:  # 低风险或中低风险
            return {
                'recommendation': "可考虑参与，但仍需谨慎",
                'reason': "风险相对可控",
                'buy_price': f"{current_price * 0.99:.3f} HKD (等待1%回调或现价)",
                'stop_loss': f"{current_price * 0.96:.3f} HKD (-4%)",
                'target_price': f"{current_price * 1.12:.3f} HKD (+12%)",
                'position': "不超过8%",
                'holding_period': "1-3个交易日"
            }
    
    def format_report(self, stock_data, price_analysis, risk_assessment, trading_plan):
        """生成分析报告"""
        report = f"""📈 港股狮滕股份实时分析报告
════════════════════════════════════════
🕐 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 股票信息: {stock_data.get('name', '未知')} ({self.stock_code}.HK)
💰 当前价格: {stock_data.get('current', '未知')} HKD
📈 今日开盘: {stock_data.get('open', '未知')} HKD
📉 昨日收盘: {stock_data.get('last_close', '未知')} HKD
────────────────────────────────────────
📊 价格行为分析:
• 相对开盘涨跌: {price_analysis.get('change_from_open_pct', 0):.2f}%
• 相对昨收涨跌: {price_analysis.get('change_from_close_pct', 0):.2f}%
• 成交量分析: {price_analysis.get('volume_analysis', '未知')}
• 成交量: {price_analysis.get('volume', 0):,} 股
• 价格位置: {price_analysis.get('price_position', '未知')}
• 日内区间: {price_analysis.get('day_range', '未知')}
• 日内波幅: {price_analysis.get('range_pct', 0):.1f}%
────────────────────────────────────────
⚠️ 风险评估:
• 风险等级: {risk_assessment.get('risk_level', '未知')}
• 风险评分: {risk_assessment.get('risk_score', 0)}/10
• 风险因素: {', '.join(risk_assessment.get('reasons', ['无']))}
• 综合评估: {risk_assessment.get('assessment', '未知')}
────────────────────────────────────────
💡 操作建议:
• 建议: {trading_plan.get('recommendation', '未知')}
• 理由: {trading_plan.get('reason', '未知')}

📋 如果决定参与:
• 建议买入价: {trading_plan.get('buy_price', '未知')}
• 建议止损价: {trading_plan.get('stop_loss', '未知')}
• 建议目标价: {trading_plan.get('target_price', '未知')}
• 建议仓位: {trading_plan.get('position', '未知')}
• 建议持有期: {trading_plan.get('holding_period', '未知')}
════════════════════════════════════════
🔍 信息验证建议:
1. 立即访问港交所披露易查看最新公告
2. 搜索公司名称: {stock_data.get('name', '狮滕')}
3. 网址: https://www1.hkexnews.hk/search/titlesearch.xhtml
4. 关注: 业绩公告、重大合同、股东变动等
════════════════════════════════════════
⚠️ 港股特别风险提示:
1. 无涨跌幅限制，波动可能很大
2. T+0交易，可当日买卖但需谨慎
3. 注意港元兑人民币汇率波动
4. 部分港股流动性较差，买卖价差大
════════════════════════════════════════
"""
        return report

def main():
    """主函数"""
    print("港股实时分析系统")
    print("=" * 60)
    
    # 等待用户输入股票代码
    stock_code = input("请输入港股代码 (5位数字): ").strip()
    
    if not stock_code.isdigit() or len(stock_code) != 5:
        print("错误: 请输入5位数字的港股代码")
        return
    
    analyzer = HKStockAnalyzer(stock_code)
    
    print(f"\n正在获取 {stock_code}.HK 实时数据...")
    
    # 获取实时数据
    stock_data = analyzer.get_realtime_data()
    if not stock_data:
        print("无法获取股票数据，请检查代码是否正确")
        return
    
    print(f"✅ 获取成功: {stock_data['name']}")
    
    # 获取用户输入的拉升信息
    print("\n📝 请输入拉升相关信息:")
    user_context = {
        'start_price': input("拉升起点价格 (HKD): "),
        'current_price': stock_data['current'],
        'volume_change': input("成交量变化 (正常/放量/异常): "),
        'pull_time': input("拉升开始时间 (如: 13:20): ")
    }
    
    # 分析价格行为
    price_analysis = analyzer.analyze_price_action(stock_data, user_context)
    
    # 评估风险
    risk_assessment = analyzer.assess_risk_level(price_analysis, user_context)
    
    # 搜索公告信息
    announcement_info = analyzer.search_hkex_announcements(stock_data['name'])
    
    # 生成交易计划
    trading_plan = analyzer.generate_trading_plan(price_analysis, risk_assessment, user_context)
    
    # 生成报告
    report = analyzer.format_report(stock_data, price_analysis, risk_assessment, trading_plan)
    
    print("\n" + "=" * 60)
    print("分析报告生成完成:")
    print("=" * 60)
    print(report)
    
    # 保存报告
    filename = f"hk_analysis_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存到: {filename}")

if __name__ == "__main__":
    main()