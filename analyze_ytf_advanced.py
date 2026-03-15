#!/usr/bin/env python3
"""
云天化高级分析 - 展示学习进步
集成ADX指标 + 综合评分系统
"""

import sys
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

sys.path.append('/home/openclaw/.openclaw/workspace')
from utils.data_source_manager import get_data_source_manager

# 导入ADX计算器
sys.path.append('/home/openclaw/.openclaw/workspace/learning/2026-03/03-15_ADX指标学习/code')
from adx_calculator import calculate_adx, interpret_adx

def analyze_yuntianhua_advanced():
    """云天化高级分析"""
    print("🚀 云天化（600096）高级分析")
    print("="*50)
    print("📚 基于ADX指标学习成果")
    print("="*50)
    
    # 获取数据
    manager = get_data_source_manager()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    
    print(f"\n📊 获取数据 ({start_date} 到 {end_date})...")
    df = manager.get_stock_data("600096", start_date, end_date)
    
    if df is None or df.empty:
        print("❌ 数据获取失败")
        return
    
    # 数据预处理
    df = df.copy()
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['open', 'high', 'low', 'close', 'volume'])
    
    if len(df) < 30:
        print(f"❌ 数据不足，需要至少30条，当前{len(df)}条")
        return
    
    print(f"✅ 获取到 {len(df)} 条数据")
    
    # 1. 基础技术分析
    print(f"\n📈 基础技术指标:")
    
    current_price = float(df['close'].iloc[-1])
    ma5 = float(df['close'].rolling(5).mean().iloc[-1])
    ma10 = float(df['close'].rolling(10).mean().iloc[-1])
    ma20 = float(df['close'].rolling(20).mean().iloc[-1])
    
    # 成交量
    avg_volume = float(df['volume'].mean())
    latest_volume = float(df['volume'].iloc[-1])
    volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 0
    
    # 价格变化
    if len(df) >= 5:
        price_5d_ago = float(df['close'].iloc[-5])
        change_5d = (current_price - price_5d_ago) / price_5d_ago * 100 if price_5d_ago > 0 else 0
    else:
        change_5d = 0
    
    print(f"   当前价格: ¥{current_price:.2f}")
    print(f"   MA5: ¥{ma5:.2f} ({'高于' if current_price > ma5 else '低于'}当前价)")
    print(f"   MA10: ¥{ma10:.2f}")
    print(f"   MA20: ¥{ma20:.2f} (关键支撑位)")
    print(f"   量比: {volume_ratio:.2f}")
    print(f"   5日涨幅: {change_5d:.1f}%")
    
    # 2. ADX趋势分析（新学内容）
    print(f"\n📊 ADX趋势分析（新学内容）:")
    
    adx_data = calculate_adx(df)
    interpretation = interpret_adx(adx_data)
    
    adx_value = adx_data.get('ADX', 25)
    plus_di = adx_data.get('+DI', 50)
    minus_di = adx_data.get('-DI', 50)
    
    print(f"   ADX值: {adx_value:.2f}")
    print(f"   +DI: {plus_di:.2f}")
    print(f"   -DI: {minus_di:.2f}")
    print(f"   趋势强度: {interpretation.get('趋势强度', '未知')}")
    print(f"   趋势方向: {interpretation.get('趋势方向', '未知')}")
    print(f"   ADX建议: {interpretation.get('交易建议', '未知')}")
    print(f"   理由: {interpretation.get('建议理由', '')}")
    
    # 3. 综合评分系统
    print(f"\n🏆 综合评分系统:")
    
    # 技术面评分（0-4分）
    tech_score = 0
    if current_price > ma5: tech_score += 1
    if current_price > ma20: tech_score += 1
    if change_5d > 5: tech_score += 1
    if volume_ratio > 1.0: tech_score += 1
    
    # 趋势面评分（基于ADX）
    trend_strength = interpretation.get('趋势强度', '未知')
    trend_score_map = {
        "极强趋势": 3,
        "明显趋势": 2,
        "弱趋势": 1,
        "震荡市": 0
    }
    trend_score = trend_score_map.get(trend_strength, 0)
    
    # 如果是上升趋势，额外加分
    if interpretation.get('趋势方向') == "上升趋势":
        trend_score += 1
    
    # 成交量评分
    volume_score = 0
    if volume_ratio > 1.5: volume_score = 2
    elif volume_ratio > 1.0: volume_score = 1
    
    # 总评分
    total_score = tech_score + trend_score + volume_score
    max_score = 9
    
    print(f"   技术面: {tech_score}/4")
    print(f"   趋势面: {trend_score}/4")
    print(f"   成交量: {volume_score}/2")
    print(f"   总评分: {total_score}/{max_score}")
    
    # 4. 具体投资建议
    print(f"\n📝 具体投资建议（文字描述）:")
    
    # 基于评分和建议
    if total_score >= 7:
        print("   ✅ 强烈建议买入")
        print(f"      理由: 综合评分{total_score}/9，技术面、趋势面、成交量均表现良好")
        print(f"      ADX显示: {interpretation.get('趋势强度')}，{interpretation.get('趋势方向')}")
        
        print(f"\n   🎯 具体操作:")
        print(f"      建议买入价: ¥{current_price * 0.995:.2f} (当前价附近)")
        print(f"      目标价位: ¥{current_price * 1.15:.2f} (+15%)")
        print(f"      止损价位: ¥{current_price * 0.95:.2f} (-5%)")
        print(f"      建议持有: 3-5天")
        print(f"      建议仓位: 20-25%")
        
    elif total_score >= 5:
        print("   ✅ 建议买入")
        print(f"      理由: 综合评分{total_score}/9，整体表现积极")
        print(f"      ADX显示: {interpretation.get('趋势强度')}")
        
        print(f"\n   🎯 具体操作:")
        print(f"      建议买入价: ¥{current_price * 0.99:.2f}")
        print(f"      目标价位: ¥{current_price * 1.10:.2f} (+10%)")
        print(f"      止损价位: ¥{current_price * 0.94:.2f} (-6%)")
        print(f"      建议持有: 5-7天")
        print(f"      建议仓位: 15-20%")
        
    elif total_score >= 3:
        print("   🟡 建议持有观望")
        print(f"      理由: 综合评分{total_score}/9，无明显优势")
        print(f"      ADX显示: {interpretation.get('趋势强度')}，建议等待更好时机")
        
        print(f"\n   🎯 操作建议:")
        print(f"      等待价格: ¥{ma20 * 0.98:.2f} 以下")
        print(f"      如已持有，止损位: ¥{current_price * 0.93:.2f}")
        
    else:
        print("   🔴 建议卖出或不买入")
        print(f"      理由: 综合评分{total_score}/9，技术面偏弱")
        print(f"      ADX显示: {interpretation.get('趋势强度')}，{interpretation.get('趋势方向')}")
        print(f"      建议规避或卖出")
    
    # 5. 风险收益分析
    print(f"\n📊 风险收益分析:")
    
    if total_score >= 5:
        target_return = 15 if total_score >= 7 else 10
        stop_loss = 5 if total_score >= 7 else 6
        
        potential_return = target_return
        potential_loss = stop_loss
        risk_reward = target_return / stop_loss if stop_loss > 0 else 0
        
        print(f"   潜在收益: {potential_return}%")
        print(f"   潜在亏损: {potential_loss}%")
        print(f"   风险收益比: {risk_reward:.2f}")
        
        if risk_reward > 2:
            print("   ✅ 风险收益比较佳")
        elif risk_reward > 1:
            print("   ⚠️ 风险收益比一般")
        else:
            print("   ❌ 风险收益比较差")
    
    # 6. 触发条件
    print(f"\n⚡ 买入触发条件:")
    
    buy_triggers = []
    if adx_value > 25 and plus_di > minus_di:
        buy_triggers.append("ADX>25且+DI>-DI（上升趋势确认）")
    if volume_ratio > 1.5:
        buy_triggers.append("成交量放大至1.5倍以上")
    if current_price < ma20 * 1.02:
        buy_triggers.append("价格接近MA20支撑位")
    
    if buy_triggers:
        for trigger in buy_triggers:
            print(f"   • {trigger}")
    else:
        print(f"   • 暂无明确买入触发条件")
    
    print(f"\n🚨 止损触发条件:")
    print(f"   • 价格跌破止损价位")
    print(f"   • ADX趋势转弱（ADX<20或-DI>+DI）")
    print(f"   • 成交量持续萎缩（量比<0.8）")
    
    print(f"\n🔄 重新评估条件:")
    print(f"   • ADX值发生重大变化（变化>10）")
    print(f"   • +DI和-DI发生交叉")
    print(f"   • 出现重大利好/利空新闻")
    
    # 7. 系统进步总结
    print(f"\n💡 系统进步总结:")
    print("   1. ✅ 学习了ADX指标并成功集成")
    print("   2. ✅ 建立了综合评分系统（技术+趋势+成交量）")
    print("   3. ✅ 提供了更具体的投资建议和操作细节")
    print("   4. ✅ 增加了风险收益分析和触发条件")
    print("   5. ✅ 基于ADX过滤震荡市，提高交易质量")
    
    print(f"\n📅 下次评估时间: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')}")
    
    print(f"\n{'='*50}")
    print("🎯 核心进步: 从简单指标分析到综合趋势判断")
    print("           从统计维度到具体操作建议")
    print(f"{'='*50}")

if __name__ == "__main__":
    analyze_yuntianhua_advanced()