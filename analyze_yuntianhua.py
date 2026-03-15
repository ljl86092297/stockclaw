#!/usr/bin/env python3
"""
云天化短线分析 - 改进版
"""

import sys
sys.path.append('/home/openclaw/.openclaw/workspace')

from utils.data_source_manager import get_data_source_manager
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def analyze_yuntianhua():
    """分析云天化（改进版）"""
    print("🚀 云天化（600096）短线分析")
    print("="*50)
    
    # 获取数据
    manager = get_data_source_manager()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    
    df = manager.get_stock_data("600096", start_date, end_date)
    if df is None or df.empty:
        print("❌ 无法获取数据")
        return
    
    # 数据清洗
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 计算指标
    current_price = float(df['close'].iloc[-1])
    
    # 移动平均线
    ma5 = float(df['close'].rolling(5).mean().iloc[-1])
    ma10 = float(df['close'].rolling(10).mean().iloc[-1])
    ma20 = float(df['close'].rolling(20).mean().iloc[-1])
    
    # 成交量
    avg_volume = float(df['volume'].mean())
    latest_volume = float(df['volume'].iloc[-1])
    volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 0
    
    # 5日涨幅
    if len(df) >= 5:
        price_5d_ago = float(df['close'].iloc[-5])
        change_5d = (current_price - price_5d_ago) / price_5d_ago * 100 if price_5d_ago > 0 else 0
    else:
        change_5d = 0
    
    # 价格区间
    period_high = float(df['high'].max())
    period_low = float(df['low'].min())
    price_position = (current_price - period_low) / (period_high - period_low) * 100 if period_high > period_low else 50
    
    # ATR（波动率）
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = float(tr.rolling(14).mean().iloc[-1])
    
    # 获取基本面
    try:
        import baostock as bs
        lg = bs.login()
        pe = pb = 0
        
        rs = bs.query_history_k_data_plus(
            "sh.600096",
            'peTTM,pbMRQ',
            start_date='2025-03-01',
            end_date='2025-03-15'
        )
        
        if rs.error_code == '0':
            data = []
            while rs.next():
                data.append(rs.get_row_data())
            if data:
                pe = float(data[-1][0]) if data[-1][0] != '' else 0
                pb = float(data[-1][1]) if data[-1][1] != '' else 0
        
        bs.logout()
    except:
        pe = pb = 0
    
    # 短线评分（改进版）
    score = 0
    
    # 1. 趋势得分（0-3分）
    if current_price > ma5: score += 1
    if current_price > ma10: score += 1
    if change_5d > 5: score += 1
    
    # 2. 量能得分（0-2分）
    if volume_ratio > 1.5: score += 2
    elif volume_ratio > 1.0: score += 1
    
    # 3. 位置得分（0-2分）
    if 30 < price_position < 70: score += 1  # 中间位置较好
    if price_position < 40: score += 1  # 低位有潜力
    
    # 4. 波动得分（0-1分）
    if atr / current_price < 0.05: score += 1  # 波动适中
    
    # 5. 估值得分（0-2分）
    if 0 < pe < 15: score += 2
    elif 0 < pe < 25: score += 1
    
    print(f"\n📊 具体指标数值:")
    print(f"   当前价格: ¥{current_price:.2f}")
    print(f"   MA5: ¥{ma5:.2f} ({'高于' if current_price > ma5 else '低于'}当前价)")
    print(f"   MA10: ¥{ma10:.2f}")
    print(f"   MA20: ¥{ma20:.2f}")
    print(f"   量比: {volume_ratio:.2f}")
    print(f"   5日涨幅: {change_5d:.1f}%")
    print(f"   价格位置: {price_position:.1f}% (近期区间)")
    print(f"   ATR波动: {atr:.4f}")
    print(f"   市盈率PE: {pe:.2f}")
    print(f"   市净率PB: {pb:.2f}")
    print(f"   短线评分: {score}/10")
    
    # 短线建议
    print(f"\n📝 短线投资建议（文字描述）:")
    
    if score >= 8:
        print("✅ 强烈买入")
        print(f"   理由: 评分{score}/10显示短期强势，量价配合良好，估值有优势")
        print(f"   买入价格: ¥{current_price*0.995:.2f} (现价附近)")
        print(f"   目标价格: ¥{current_price*1.12:.2f} (+12%)")
        print(f"   止损价格: ¥{current_price*0.95:.2f} (-5%)")
        print(f"   建议持有: 3-5天")
        print(f"   建议仓位: 20-25%")
        
    elif score >= 6:
        print("✅ 买入")
        print(f"   理由: 评分{score}/10显示趋势向上，但量能或位置一般")
        print(f"   买入价格: ¥{ma10*0.98:.2f} (MA10附近)")
        print(f"   目标价格: ¥{current_price*1.08:.2f} (+8%)")
        print(f"   止损价格: ¥{current_price*0.94:.2f} (-6%)")
        print(f"   建议持有: 5-7天")
        print(f"   建议仓位: 15-20%")
        
    elif score >= 4:
        print("🟡 持有/观望")
        print(f"   理由: 评分{score}/10显示无明显优势，建议等待更好时机")
        print(f"   如已持有，止损位: ¥{current_price*0.93:.2f}")
        print(f"   如未持有，等待价格: ¥{ma20*0.97:.2f} 以下")
        
    else:
        print("🔴 卖出/不买入")
        print(f"   理由: 评分{score}/10显示短期弱势，风险较大")
        print(f"   如持有，建议卖出")
        print(f"   不建议买入")
    
    # 具体操作要点
    print(f"\n⚡ 具体操作要点:")
    print(f"   1. 买入时机: 价格在支撑位{ma10:.2f}附近时考虑")
    print(f"   2. 加仓条件: 放量突破{period_high*0.98:.2f}可加仓")
    print(f"   3. 止损纪律: 严格按止损价执行")
    print(f"   4. 持有时间: 不超过7天，快进快出")
    
    # 风险提示
    print(f"\n🚨 风险提示:")
    print(f"   1. 当前位置: {price_position:.1f}%，{('偏高' if price_position > 70 else '适中' if price_position > 30 else '偏低')}")
    print(f"   2. 波动风险: ATR显示日均波动{atr/current_price*100:.1f}%")
    print(f"   3. 量能风险: 量比{volume_ratio:.2f}，{('活跃' if volume_ratio > 1.2 else '一般' if volume_ratio > 0.8 else '低迷')}")
    
    # 重新评估条件
    print(f"\n🔄 需要重新评估的情况:")
    print(f"   1. 出现重大利好/利空新闻")
    print(f"   2. 成交量异常放大(量比>2)或萎缩(量比<0.5)")
    print(f"   3. 价格突破关键位({period_high:.2f}或{ma20:.2f})")
    print(f"   4. 技术指标发出矛盾信号")
    
    print(f"\n📅 下次评估时间: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}")
    print(f"\n💎 核心观点: ", end="")
    
    if score >= 6:
        print("短期趋势向上，量价配合，建议轻仓参与，严格止损")
    elif score >= 4:
        print("无明显优势，建议观望或等待更好价格")
    else:
        print("短期弱势，建议规避风险")
    
    print(f"\n{'='*50}")
    print("📈 短线交易核心: 快进快出，严格止损，追求5-12%收益")
    print(f"{'='*50}")

if __name__ == "__main__":
    analyze_yuntianhua()