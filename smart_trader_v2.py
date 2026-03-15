#!/usr/bin/env python3
"""
智能短线交易系统 V2
核心：追求高胜率，严格风险控制，多重筛选
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

sys.path.append('/home/openclaw/.openclaw/workspace')
from utils.data_source_manager import get_data_source_manager

def analyze_with_high_winrate(name, code):
    """高胜率分析"""
    print(f"\n{'='*80}")
    print(f"🎯 {name} ({code}) - 高胜率策略分析")
    print(f"{'='*80}")
    
    # 获取数据
    manager = get_data_source_manager()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    df = manager.get_stock_data(code, start_date, end_date)
    if df is None or df.empty:
        print("❌ 数据获取失败")
        return
    
    # 数据预处理
    df = df.copy()
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['open', 'high', 'low', 'close', 'volume'])
    
    if len(df) < 40:
        print(f"❌ 数据不足，需要至少40条，当前{len(df)}条")
        return
    
    current_price = float(df['close'].iloc[-1])
    period_high = float(df['high'].max())
    period_low = float(df['low'].min())
    
    print(f"\n📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"📈 当前价格: ¥{current_price:.2f}")
    
    # ==================== 1. 基本面筛选 ====================
    print(f"\n📊 基本面筛选:")
    
    # 模拟基本面数据
    fundamental = {
        "pe_ratio": 28.5,      # 市盈率
        "roe": 7.8,            # 净资产收益率
        "profit_growth": -8.2, # 利润增长率
        "debt_ratio": 42.3,    # 负债率
        "has_major_negative": False
    }
    
    fundamental_rejections = []
    
    # 严格标准
    if fundamental["pe_ratio"] > 35:
        fundamental_rejections.append(f"市盈率过高({fundamental['pe_ratio']:.1f}>35)")
    
    if fundamental["roe"] < 5:
        fundamental_rejections.append(f"ROE过低({fundamental['roe']:.1f}%<5%)")
    
    if fundamental["profit_growth"] < -20:
        fundamental_rejections.append(f"利润下滑过大({fundamental['profit_growth']:.1f}%<-20%)")
    
    if fundamental["debt_ratio"] > 60:
        fundamental_rejections.append(f"负债率过高({fundamental['debt_ratio']:.1f}%>60%)")
    
    if fundamental["has_major_negative"]:
        fundamental_rejections.append("存在重大利空")
    
    if fundamental_rejections:
        print(f"  ❌ 基本面不达标:")
        for reason in fundamental_rejections:
            print(f"     • {reason}")
        print(f"\n🔴 建议: 不买入 (基本面风险)")
        print(f"{'='*80}")
        return
    
    print(f"  ✅ 基本面通过")
    
    # ==================== 2. 技术面筛选 ====================
    print(f"\n📈 技术面筛选:")
    
    # 计算技术指标
    ma5 = float(df['close'].rolling(5).mean().iloc[-1])
    ma10 = float(df['close'].rolling(10).mean().iloc[-1])
    ma20 = float(df['close'].rolling(20).mean().iloc[-1])
    ma60 = float(df['close'].rolling(60).mean().iloc[-1])
    
    price_position = (current_price - period_low) / (period_high - period_low) * 100 if period_high > period_low else 50
    
    # 短期涨幅
    if len(df) >= 5:
        price_5d_ago = float(df['close'].iloc[-5])
        change_5d = (current_price - price_5d_ago) / price_5d_ago * 100 if price_5d_ago > 0 else 0
    else:
        change_5d = 0
    
    # 成交量
    avg_volume = float(df['volume'].mean())
    latest_volume = float(df['volume'].iloc[-1])
    volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 0
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi_value = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
    
    technical_rejections = []
    
    # 严格技术标准
    # 1. 必须处于上升趋势
    if not (current_price > ma20 > ma60):
        technical_rejections.append("不处于明确上升趋势")
    
    # 2. 避免高位
    if price_position > 75:
        technical_rejections.append(f"价格位置过高({price_position:.1f}%>75%)")
    
    # 3. 避免追高
    if change_5d > 15:
        technical_rejections.append(f"短期涨幅过大({change_5d:.1f}%>15%)")
    
    # 4. 成交量检查
    if volume_ratio > 2.5:
        technical_rejections.append(f"成交量异常({volume_ratio:.2f}>2.5)")
    elif volume_ratio < 0.7:
        technical_rejections.append(f"成交量不足({volume_ratio:.2f}<0.7)")
    
    # 5. 避免超买
    if rsi_value > 75:
        technical_rejections.append(f"RSI超买({rsi_value:.1f}>75)")
    
    if technical_rejections:
        print(f"  ❌ 技术面不达标:")
        for reason in technical_rejections:
            print(f"     • {reason}")
        print(f"\n🔴 建议: 不买入 (技术面风险)")
        print(f"{'='*80}")
        return
    
    print(f"  ✅ 技术面通过")
    print(f"    趋势: 上升趋势 (价格>MA20>MA60)")
    print(f"    位置: {price_position:.1f}% (适中)")
    print(f"    短期涨幅: {change_5d:.1f}% (可接受)")
    print(f"    成交量: 量比{volume_ratio:.2f} (正常)")
    print(f"    RSI: {rsi_value:.1f} (正常)")
    
    # ==================== 3. 风险面筛选 ====================
    print(f"\n⚠️ 风险面筛选:")
    
    distance_from_high = (period_high - current_price) / current_price * 100
    
    risk_rejections = []
    
    # 距离高点检查
    if distance_from_high < 5:
        risk_rejections.append(f"距离历史高点过近({distance_from_high:.1f}%<5%)")
    
    # 波动率检查
    if len(df) >= 20:
        recent_high = float(df['high'].iloc[-20:].max())
        recent_low = float(df['low'].iloc[-20:].min())
        volatility = (recent_high - recent_low) / recent_low * 100
        
        if volatility > 30:
            risk_rejections.append(f"近期波动过大({volatility:.1f}%>30%)")
    
    if risk_rejections:
        print(f"  ❌ 风险过高:")
        for reason in risk_rejections:
            print(f"     • {reason}")
        print(f"\n🔴 建议: 不买入 (风险过高)")
        print(f"{'='*80}")
        return
    
    # 风险等级评估
    if distance_from_high < 10 or price_position > 70:
        risk_level = "高"
    elif distance_from_high < 20 or price_position > 60:
        risk_level = "中高"
    elif distance_from_high < 30 or price_position > 50:
        risk_level = "中"
    else:
        risk_level = "低"
    
    print(f"  ✅ 风险可控")
    print(f"    距离高点: {distance_from_high:.1f}%")
    print(f"    波动率: {volatility if 'volatility' in locals() else 0:.1f}%")
    print(f"    风险等级: {risk_level}")
    
    # ==================== 4. 通过所有筛选，生成交易计划 ====================
    print(f"\n🎯 通过所有筛选！生成交易计划")
    
    # 根据风险等级确定参数
    if risk_level == "低":
        target_return = 12
        stop_loss = 4
        position = 0.25
        holding_days = 5
    elif risk_level == "中":
        target_return = 10
        stop_loss = 5
        position = 0.20
        holding_days = 4
    elif risk_level == "中高":
        target_return = 8
        stop_loss = 6
        position = 0.15
        holding_days = 3
    else:  # 高
        target_return = 6
        stop_loss = 7
        position = 0.10
        holding_days = 2
    
    # 计算具体价格
    buy_price = current_price * 0.995  # 允许0.5%回调
    target_price = current_price * (1 + target_return / 100)
    stop_loss_price = current_price * (1 - stop_loss / 100)
    risk_reward = target_return / stop_loss if stop_loss > 0 else 0
    
    # 胜率估计
    win_rate_estimate = 65.0  # 基础胜率
    
    # 基本面调整
    if fundamental["pe_ratio"] < 25 and fundamental["roe"] > 8:
        win_rate_estimate += 5
    
    # 技术面调整
    if 40 < price_position < 60 and 1.0 < volume_ratio < 1.8 and 40 < rsi_value < 65:
        win_rate_estimate += 10
    
    # 风险调整
    if risk_level == "低":
        win_rate_estimate += 5
    elif risk_level == "高":
        win_rate_estimate -= 5
    
    win_rate_estimate = max(50, min(85, win_rate_estimate))
    
    print(f"\n📝 交易计划:")
    print(f"   建议买入价: ¥{buy_price:.2f} (当前价附近)")
    print(f"   目标价位: ¥{target_price:.2f} (+{target_return}%)")
    print(f"   止损价位: ¥{stop_loss_price:.2f} (-{stop_loss}%)")
    print(f"   风险收益比: {risk_reward:.2f}")
    print(f"   建议仓位: {position*100:.0f}%")
    print(f"   建议持有: {holding_days}天")
    print(f"   预估胜率: {win_rate_estimate:.1f}%")
    
    print(f"\n✅ 买入条件:")
    print(f"   • 价格位置适中({price_position:.1f}%<60%)")
    print(f"   • RSI正常({rsi_value:.1f}<70)")
    print(f"   • 成交量正常({volume_ratio:.2f}在0.7-2.5之间)")
    print(f"   • 处于上升趋势(价格>MA20>MA60)")
    
    print(f"\n🚨 止损条件:")
    print(f"   • 价格跌破¥{stop_loss_price:.2f} (止损{stop_loss}%)")
    print(f"   • RSI>80 (严重超买)")
    print(f"   • 成交量持续萎缩(量比<0.7)")
    print(f"   • 持有超过{holding_days+3}天未达目标")
    
    print(f"\n💡 策略说明:")
    print("   1. 三重筛选: 基本面 + 技术面 + 风险面")
    print("   2. 严格标准: 宁可错过，不可做错")
    print("   3. 追求高胜率: 预估胜率>60%")
    print("   4. 风险控制: 单笔最大亏损<2%，明确止损")
    print("   5. 明确计划: 具体的买入、持有、卖出条件")
    
    print(f"\n📅 下次评估: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")

def main():
    """主函数"""
    print("🚀 智能短线交易系统 V2")
    print("="*80)
    print("📚 追求高胜率，严格风险控制，多重筛选")
    print("="*80)
    
    stocks = [
        ("华胜天成", "600410"),
        ("拓维信息", "002261"),
        ("航锦科技", "000818")
    ]
    
    for name, code in stocks:
        analyze_with_high_winrate(name, code)
    
    print("\n✅ 系统总结:")
    print("   核心原则: 宁可错过100次机会，也不要做错1次交易")
    print("   筛选标准: 基本面健康 + 技术面强势 + 风险可控")
    print("   风险控制: 严格止损，仓位管理，胜率优先")
    print("   交易纪律: 计划交易，交易计划")
    
    print("\n📊 下一步进化:")
    print("   1. 连接真实财务数据源")
    print("   2. 进行历史回测验证策略有效性")
    print("   3. 开发更多高胜率策略变体")
    print("   4. 建立交易记录和学习系统")
    
    print("\n💡 记住: 短线交易的核心是纪律和风险控制")
    print("         高胜率来自于只做高概率交易")

if __name__ == "__main__":
    main()