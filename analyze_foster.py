#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
福斯特（603806）快速分析脚本
使用Baostock API获取数据并分析
"""

import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("="*60)
print("福斯特（603806）快速分析")
print("="*60)

# 登录Baostock
try:
    lg = bs.login()
    if lg.error_code != '0':
        print(f"❌ Baostock登录失败: {lg.error_msg}")
        exit(1)
    print("✅ Baostock登录成功")
except Exception as e:
    print(f"❌ Baostock登录异常: {e}")
    exit(1)

try:
    # 获取福斯特日线数据（最近1年）
    print("\n📥 获取数据...")
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    rs = bs.query_history_k_data_plus(
        "sh.603806",
        "date,open,high,low,close,volume,turnover_rate",
        start_date=start_date,
        end_date=end_date,
        frequency="d",
        adjustflag="2"
    )
    
    if rs.error_code != '0':
        print(f"❌ 查询失败: {rs.error_msg}")
        bs.logout()
        exit(1)
    
    # 处理数据
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    
    if not data_list:
        print("❌ 无数据")
        bs.logout()
        exit(1)
    
    df = pd.DataFrame(data_list, columns=rs.fields)
    
    # 转换数据类型
    df['date'] = pd.to_datetime(df['date'])
    df['close'] = pd.to_numeric(df['close'])
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['volume'] = pd.to_numeric(df['volume'])
    df['turnover_rate'] = pd.to_numeric(df['turnover_rate'])
    
    df = df.sort_values('date').reset_index(drop=True)
    
    print(f"✅ 获取到 {len(df)} 条数据")
    print(f"   期间: {df['date'].min().strftime('%Y-%m-%d')} 到 {df['date'].max().strftime('%Y-%m-%d')}")
    
    # 计算基本指标
    print("\n📊 计算技术指标...")
    
    # 当前价格信息
    current_price = df['close'].iloc[-1]
    prev_price = df['close'].iloc[-2] if len(df) > 1 else current_price
    price_change = ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
    
    # 移动平均线
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 简单ATR计算
    high_low = df['high'] - df['low']
    high_close = abs(df['high'] - df['close'].shift())
    low_close = abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=14).mean()
    
    # 获取最新值
    latest = df.iloc[-1]
    
    print("\n" + "="*60)
    print("📈 福斯特（603806）分析结果")
    print("="*60)
    
    print(f"\n💰 价格信息:")
    print(f"   当前价格: {current_price:.2f}")
    print(f"   涨跌幅: {price_change:+.2f}%")
    print(f"   成交量: {latest['volume']:,.0f}")
    print(f"   换手率: {latest['turnover_rate']:.2f}%")
    
    print(f"\n📊 技术指标:")
    
    # RSI分析
    rsi = latest['RSI']
    if pd.notna(rsi):
        rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "正常"
        print(f"   RSI(14): {rsi:.1f} ({rsi_status})")
    
    # 移动平均线分析
    ma5 = latest['MA5']
    ma20 = latest['MA20']
    if pd.notna(ma5) and pd.notna(ma20):
        trend = "上涨趋势" if ma5 > ma20 else "下跌趋势"
        position = "均线上方" if current_price > ma20 else "均线下方"
        print(f"   均线: MA5={ma5:.2f}, MA20={ma20:.2f}")
        print(f"   趋势: {trend}，价格在{position}")
    
    # ATR分析
    atr = latest['ATR']
    if pd.notna(atr):
        volatility = atr / current_price * 100
        print(f"   ATR(14): {atr:.3f} (波动率: {volatility:.2f}%)")
        print(f"   建议止损: ±{atr*2:.2f}")
    
    print(f"\n🎯 关键价位:")
    support = df['low'].tail(20).min()
    resistance = df['high'].tail(20).max()
    print(f"   支撑位: {support:.2f}")
    print(f"   阻力位: {resistance:.2f}")
    
    print(f"\n💡 操作建议:")
    
    suggestions = []
    
    # RSI建议
    if pd.notna(rsi):
        if rsi > 70:
            suggestions.append("RSI超买，警惕回调风险")
        elif rsi < 30:
            suggestions.append("RSI超卖，关注反弹机会")
    
    # 趋势建议
    if pd.notna(ma5) and pd.notna(ma20):
        if ma5 > ma20 and current_price > ma20:
            suggestions.append("上涨趋势中，可考虑逢低布局")
        elif ma5 < ma20 and current_price < ma20:
            suggestions.append("下跌趋势中，建议谨慎观望")
    
    # ATR建议
    if pd.notna(atr):
        if volatility > 3:
            suggestions.append("波动率较高，建议减小仓位")
        else:
            suggestions.append("波动率正常，可按计划操作")
    
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
    else:
        print("   建议结合其他因素综合判断")
    
    print(f"\n📅 短期展望:")
    recent_trend = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100 if len(df) >= 5 else 0
    if recent_trend > 3:
        print("   短期趋势偏强，可能继续上涨")
    elif recent_trend < -3:
        print("   短期趋势偏弱，可能继续调整")
    else:
        print("   短期震荡整理，等待方向选择")
    
    print(f"\n⚠️ 风险提示:")
    print("   1. 股市有风险，投资需谨慎")
    print("   2. 以上分析仅供参考，不构成投资建议")
    print("   3. 请结合自身风险承受能力决策")
    
    print("\n" + "="*60)
    print("✅ 分析完成！")
    print("="*60)
    
except Exception as e:
    print(f"❌ 分析过程中出现错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    # 退出Baostock
    bs.logout()
    print("\n✅ Baostock已退出")