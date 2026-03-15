#!/usr/bin/env python3
"""
ADX指标计算器
学习时间：2026-03-15
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple

def calculate_adx(df: pd.DataFrame, period: int = 14) -> Dict[str, float]:
    """
    计算ADX指标
    
    参数:
        df: 包含high, low, close的DataFrame
        period: 计算周期，默认14
        
    返回:
        dict: 包含+DI, -DI, ADX值的字典
    """
    if df.empty or len(df) < period * 2:
        return {"+DI": 50, "-DI": 50, "ADX": 25}
    
    # 确保数据类型正确
    df = df.copy()
    for col in ['high', 'low', 'close']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 计算真实波幅(TR)
    df['high_low'] = df['high'] - df['low']
    df['high_close'] = abs(df['high'] - df['close'].shift(1))
    df['low_close'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    
    # 计算方向运动(DM)
    df['up_move'] = df['high'] - df['high'].shift(1)
    df['down_move'] = df['low'].shift(1) - df['low']
    
    # +DM和-DM
    df['+DM'] = np.where(
        (df['up_move'] > df['down_move']) & (df['up_move'] > 0), 
        df['up_move'], 
        0
    )
    df['-DM'] = np.where(
        (df['down_move'] > df['up_move']) & (df['down_move'] > 0), 
        df['down_move'], 
        0
    )
    
    # 使用Wilder的平滑方法（EMA）
    def wilder_smoothing(series, period):
        """Wilder平滑方法"""
        smoothed = series.copy()
        smoothed.iloc[period-1] = series.iloc[:period].mean()
        for i in range(period, len(series)):
            smoothed.iloc[i] = (smoothed.iloc[i-1] * (period - 1) + series.iloc[i]) / period
        return smoothed
    
    # 计算平滑值
    df['TR_smooth'] = wilder_smoothing(df['TR'], period)
    df['+DM_smooth'] = wilder_smoothing(df['+DM'], period)
    df['-DM_smooth'] = wilder_smoothing(df['-DM'], period)
    
    # 计算方向指标(DI)
    df['+DI'] = 100 * df['+DM_smooth'] / df['TR_smooth']
    df['-DI'] = 100 * df['-DM_smooth'] / df['TR_smooth']
    
    # 计算方向指数(DX)
    df['DX'] = 100 * abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI']).replace(0, 0.001)
    
    # 计算ADX（DX的平滑）
    df['ADX'] = wilder_smoothing(df['DX'], period)
    
    # 返回最新值
    latest = df.iloc[-1]
    return {
        "+DI": float(latest['+DI']),
        "-DI": float(latest['-DI']),
        "ADX": float(latest['ADX'])
    }

def interpret_adx(adx_data: Dict[str, float]) -> Dict[str, str]:
    """
    解读ADX指标
    
    返回:
        dict: 包含趋势强度、方向、建议
    """
    adx = adx_data.get('ADX', 25)
    plus_di = adx_data.get('+DI', 50)
    minus_di = adx_data.get('-DI', 50)
    
    # 趋势强度
    if adx > 40:
        strength = "极强趋势"
        strength_score = 3
    elif adx > 25:
        strength = "明显趋势"
        strength_score = 2
    elif adx > 20:
        strength = "弱趋势"
        strength_score = 1
    else:
        strength = "震荡市"
        strength_score = 0
    
    # 趋势方向
    if plus_di > minus_di + 5:
        direction = "上升趋势"
        direction_score = 1
    elif minus_di > plus_di + 5:
        direction = "下降趋势"
        direction_score = -1
    else:
        direction = "方向不明"
        direction_score = 0
    
    # 交易建议
    if strength_score >= 2 and direction_score == 1:
        recommendation = "买入"
        reason = f"趋势明显({strength})且方向向上"
    elif strength_score >= 2 and direction_score == -1:
        recommendation = "卖出"
        reason = f"趋势明显({strength})且方向向下"
    elif strength_score == 0:
        recommendation = "观望"
        reason = "震荡市，趋势不明显"
    else:
        recommendation = "持有"
        reason = f"趋势{strength}，方向{direction}"
    
    return {
        "趋势强度": strength,
        "趋势方向": direction,
        "交易建议": recommendation,
        "建议理由": reason,
        "ADX值": f"{adx:.2f}",
        "+DI值": f"{plus_di:.2f}",
        "-DI值": f"{minus_di:.2f}",
        "强度评分": strength_score,
        "方向评分": direction_score
    }

def adx_trading_signal(df: pd.DataFrame) -> Dict[str, any]:
    """
    生成ADX交易信号
    
    返回完整的ADX分析结果
    """
    # 计算ADX
    adx_data = calculate_adx(df)
    
    # 解读ADX
    interpretation = interpret_adx(adx_data)
    
    # 结合价格分析
    current_price = float(df['close'].iloc[-1]) if 'close' in df.columns else 0
    ma20 = float(df['close'].rolling(20).mean().iloc[-1]) if len(df) >= 20 else current_price
    
    # 综合信号
    strength_score = interpretation['强度评分']
    direction_score = interpretation['方向评分']
    
    if strength_score >= 2 and direction_score == 1 and current_price > ma20:
        final_signal = "强烈买入"
        confidence = 0.8
    elif strength_score >= 2 and direction_score == -1 and current_price < ma20:
        final_signal = "强烈卖出"
        confidence = 0.7
    elif strength_score == 0:
        final_signal = "观望"
        confidence = 0.9
    else:
        final_signal = "持有"
        confidence = 0.6
    
    return {
        **adx_data,
        **interpretation,
        "综合信号": final_signal,
        "信号置信度": confidence,
        "当前价格": current_price,
        "MA20": ma20,
        "价格位置": "高于MA20" if current_price > ma20 else "低于MA20"
    }

# 测试函数
def test_adx_calculator():
    """测试ADX计算器"""
    print("🧪 测试ADX计算器...")
    
    # 创建测试数据
    dates = pd.date_range('2026-02-01', periods=50, freq='D')
    np.random.seed(42)
    
    # 模拟上升趋势
    base = 40
    trend = np.linspace(0, 10, 50)
    noise = np.random.normal(0, 2, 50)
    
    df = pd.DataFrame({
        'date': dates,
        'open': base + trend + noise,
        'high': base + trend + noise + np.random.uniform(1, 3, 50),
        'low': base + trend + noise - np.random.uniform(1, 3, 50),
        'close': base + trend + noise,
        'volume': np.random.randint(100000, 500000, 50)
    })
    
    # 计算ADX
    adx_data = calculate_adx(df)
    interpretation = interpret_adx(adx_data)
    
    print(f"ADX: {adx_data['ADX']:.2f}")
    print(f"+DI: {adx_data['+DI']:.2f}")
    print(f"-DI: {adx_data['-DI']:.2f}")
    print(f"趋势强度: {interpretation['趋势强度']}")
    print(f"趋势方向: {interpretation['趋势方向']}")
    print(f"交易建议: {interpretation['交易建议']}")
    
    # 生成完整信号
    signal = adx_trading_signal(df)
    print(f"\n综合信号: {signal['综合信号']}")
    print(f"信号置信度: {signal['信号置信度']:.2f}")
    
    return signal

if __name__ == "__main__":
    test_result = test_adx_calculator()
    print("\n✅ ADX计算器测试完成")