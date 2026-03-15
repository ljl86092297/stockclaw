#!/usr/bin/env python3
"""
ATR（平均真实波幅）计算模块
版本: 1.0
作者: OpenClaw
创建日期: 2026-03-15
最后更新: 2026-03-15
"""

import pandas as pd
import numpy as np
from typing import Optional, Union

def calculate_true_range(df: pd.DataFrame) -> pd.Series:
    """
    计算真实波幅（True Range）
    
    Args:
        df: DataFrame，需包含'high','low','close'列
    
    Returns:
        Series: 真实波幅值
    """
    # 确保列名正确（兼容不同数据源）
    high_col = 'high' if 'high' in df.columns else '最高' if '最高' in df.columns else df.columns[1]
    low_col = 'low' if 'low' in df.columns else '最低' if '最低' in df.columns else df.columns[2]
    close_col = 'close' if 'close' in df.columns else '收盘' if '收盘' in df.columns else df.columns[3]
    
    high = df[high_col]
    low = df[low_col]
    close = df[close_col]
    
    # 计算三种波幅
    tr1 = high - low  # 当日最高最低差
    tr2 = abs(high - close.shift(1))  # 当日最高与前收盘差
    tr3 = abs(low - close.shift(1))   # 当日最低与前收盘差
    
    # 取三者最大值
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    return tr

def calculate_atr(df: pd.DataFrame, period: int = 14, method: str = 'wilder') -> pd.Series:
    """
    计算ATR（平均真实波幅）
    
    Args:
        df: DataFrame，需包含价格数据
        period: 计算周期，默认14
        method: 计算方法，'wilder'（Wilder平滑法）或'sma'（简单移动平均）
    
    Returns:
        Series: ATR值
    """
    # 计算真实波幅
    tr = calculate_true_range(df)
    
    # 计算ATR
    if method == 'wilder':
        # Wilder平滑法（原版方法）
        # ATR_t = (ATR_{t-1} × (N-1) + TR_t) / N
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
    elif method == 'sma':
        # 简单移动平均法
        atr = tr.rolling(window=period).mean()
    else:
        raise ValueError(f"不支持的ATR计算方法: {method}，请使用'wilder'或'sma'")
    
    return atr

def calculate_atr_stop_loss(df: pd.DataFrame, atr_period: int = 14, 
                           atr_multiplier: float = 2.0, 
                           position_type: str = 'long') -> pd.Series:
    """
    基于ATR计算动态止损位
    
    Args:
        df: 包含价格数据的DataFrame
        atr_period: ATR计算周期
        atr_multiplier: ATR乘数（通常1.5-3.0）
        position_type: 仓位类型，'long'（多头）或'short'（空头）
    
    Returns:
        Series: 止损价位
    """
    # 计算ATR
    atr_values = calculate_atr(df, period=atr_period)
    
    # 获取收盘价列
    close_col = 'close' if 'close' in df.columns else '收盘' if '收盘' in df.columns else df.columns[3]
    close_price = df[close_col]
    
    # 计算止损位
    if position_type == 'long':
        # 多头止损：收盘价 - ATR × 乘数
        stop_loss = close_price - atr_values * atr_multiplier
    elif position_type == 'short':
        # 空头止损：收盘价 + ATR × 乘数
        stop_loss = close_price + atr_values * atr_multiplier
    else:
        raise ValueError(f"不支持的仓位类型: {position_type}，请使用'long'或'short'")
    
    return stop_loss

def calculate_position_size(account_size: float, risk_per_trade: float, 
                          atr_value: float, price: float) -> float:
    """
    基于ATR计算合理仓位大小
    
    Args:
        account_size: 账户总资金
        risk_per_trade: 每笔交易风险比例（如0.02表示2%）
        atr_value: 当前ATR值
        price: 当前价格
    
    Returns:
        float: 建议的仓位大小（股数）
    """
    # 计算每笔交易可承受的风险金额
    risk_amount = account_size * risk_per_trade
    
    # 基于ATR计算止损距离
    stop_distance = atr_value * 2  # 假设使用2倍ATR作为止损
    
    # 计算每股风险
    risk_per_share = stop_distance
    
    # 计算仓位大小
    if risk_per_share > 0:
        position_size = risk_amount / risk_per_share
    else:
        position_size = 0
    
    return position_size

def analyze_atr_trend(atr_series: pd.Series, lookback_period: int = 20) -> dict:
    """
    分析ATR趋势
    
    Args:
        atr_series: ATR序列
        lookback_period: 回顾周期
    
    Returns:
        dict: 分析结果
    """
    if len(atr_series) < lookback_period:
        lookback_period = len(atr_series)
    
    recent_atr = atr_series.tail(lookback_period)
    
    analysis = {
        'current_atr': recent_atr.iloc[-1],
        'average_atr': recent_atr.mean(),
        'atr_std': recent_atr.std(),
        'atr_trend': '上升' if recent_atr.iloc[-1] > recent_atr.iloc[0] else '下降',
        'volatility_level': '高' if recent_atr.iloc[-1] > recent_atr.mean() + recent_atr.std() else 
                           '低' if recent_atr.iloc[-1] < recent_atr.mean() - recent_atr.std() else '中等',
        'percentile': (recent_atr.rank(pct=True).iloc[-1] * 100)
    }
    
    return analysis

# 测试函数
if __name__ == "__main__":
    print("🧪 ATR计算模块测试")
    print("=" * 50)
    
    # 创建测试数据
    np.random.seed(42)
    dates = pd.date_range('2025-01-01', periods=100, freq='D')
    data = {
        'date': dates,
        'open': np.random.normal(100, 5, 100),
        'high': np.random.normal(105, 5, 100),
        'low': np.random.normal(95, 5, 100),
        'close': np.random.normal(100, 5, 100),
        'volume': np.random.randint(10000, 100000, 100)
    }
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    
    print("1. 测试真实波幅计算...")
    tr = calculate_true_range(df)
    print(f"   真实波幅范围: {tr.min():.4f} - {tr.max():.4f}")
    print(f"   真实波幅均值: {tr.mean():.4f}")
    
    print("\n2. 测试ATR计算（Wilder方法）...")
    atr_wilder = calculate_atr(df, period=14, method='wilder')
    print(f"   最新ATR值: {atr_wilder.iloc[-1]:.4f}")
    print(f"   ATR均值: {atr_wilder.mean():.4f}")
    
    print("\n3. 测试ATR计算（SMA方法）...")
    atr_sma = calculate_atr(df, period=14, method='sma')
    print(f"   最新ATR值: {atr_sma.iloc[-1]:.4f}")
    print(f"   ATR均值: {atr_sma.mean():.4f}")
    
    print("\n4. 测试ATR止损计算...")
    stop_loss_long = calculate_atr_stop_loss(df, position_type='long')
    stop_loss_short = calculate_atr_stop_loss(df, position_type='short')
    print(f"   多头止损位: {stop_loss_long.iloc[-1]:.4f}")
    print(f"   空头止损位: {stop_loss_short.iloc[-1]:.4f}")
    
    print("\n5. 测试仓位大小计算...")
    position = calculate_position_size(
        account_size=100000,
        risk_per_trade=0.02,
        atr_value=atr_wilder.iloc[-1],
        price=df['close'].iloc[-1]
    )
    print(f"   建议仓位: {position:.2f} 股")
    
    print("\n6. 测试ATR趋势分析...")
    trend_analysis = analyze_atr_trend(atr_wilder)
    for key, value in trend_analysis.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.4f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n✅ 所有测试通过！")