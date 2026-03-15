#!/usr/bin/env python3
"""
ATR（平均真实波幅）技术指标模块
集成到technical-analysis skill中

功能:
1. ATR指标计算
2. 基于ATR的动态止损
3. 波动性分析
4. 仓位管理建议
"""

import sys
import os
sys.path.append('/home/openclaw/.openclaw/workspace')

from learning.2026-03.03-15_ATR指标学习.code.atr_calculator import (
    calculate_atr,
    calculate_atr_stop_loss,
    calculate_position_size,
    analyze_atr_trend
)

def atr_analysis(df, period=14, method='wilder'):
    """
    完整的ATR分析
    
    Args:
        df: 价格数据DataFrame
        period: ATR计算周期
        method: 计算方法
    
    Returns:
        dict: 分析结果
    """
    results = {}
    
    # 1. 计算ATR
    atr_values = calculate_atr(df, period=period, method=method)
    results['atr_values'] = atr_values
    results['current_atr'] = atr_values.iloc[-1] if not atr_values.empty else 0
    
    # 2. 计算止损位
    if not df.empty:
        stop_loss_long = calculate_atr_stop_loss(df, position_type='long')
        stop_loss_short = calculate_atr_stop_loss(df, position_type='short')
        results['stop_loss_long'] = stop_loss_long.iloc[-1] if not stop_loss_long.empty else 0
        results['stop_loss_short'] = stop_loss_short.iloc[-1] if not stop_loss_short.empty else 0
    
    # 3. 趋势分析
    if len(atr_values) >= 20:
        trend = analyze_atr_trend(atr_values)
        results['trend_analysis'] = trend
    
    # 4. 生成交易建议
    if not df.empty and 'close' in df.columns:
        current_price = df['close'].iloc[-1]
        results['trading_suggestions'] = _generate_atr_suggestions(
            results['current_atr'], current_price, trend if 'trend_analysis' in results else None
        )
    
    return results

def _generate_atr_suggestions(current_atr, current_price, trend_analysis=None):
    """
    基于ATR生成交易建议
    
    Args:
        current_atr: 当前ATR值
        current_price: 当前价格
        trend_analysis: ATR趋势分析结果
    
    Returns:
        list: 交易建议列表
    """
    suggestions = []
    
    # 波动性建议
    if trend_analysis:
        volatility = trend_analysis.get('volatility_level', '中等')
        if volatility == '高':
            suggestions.append("⚠️ 市场波动性高，建议减小仓位或设置更宽止损")
        elif volatility == '低':
            suggestions.append("📉 市场波动性低，可能即将突破，关注突破信号")
    
    # 止损建议
    if current_atr > 0:
        stop_distance = current_atr * 2
        stop_percentage = (stop_distance / current_price) * 100 if current_price > 0 else 0
        
        suggestions.append(f"📊 建议止损距离: {stop_distance:.2f} ({stop_percentage:.1f}%)")
        
        if stop_percentage > 5:
            suggestions.append("⚠️ 止损距离较大，考虑使用更小的ATR乘数")
        elif stop_percentage < 1:
            suggestions.append("✅ 止损距离合理，适合短线交易")
    
    # 趋势建议
    if trend_analysis:
        trend = trend_analysis.get('atr_trend', '未知')
        if trend == '上升':
            suggestions.append("📈 ATR上升，市场波动性增加，可能趋势开始")
        elif trend == '下降':
            suggestions.append("📉 ATR下降，市场波动性减少，可能趋势结束")
    
    return suggestions

def atr_command_example():
    """
    ATR分析命令示例
    """
    example_code = '''
# ATR分析示例
import sys
sys.path.append('/home/openclaw/.openclaw/workspace')
from skills.technical-analysis.atr_module import atr_analysis
from utils.data_source_manager import get_data_source_manager

# 获取数据
manager = get_data_source_manager()
df = manager.get_stock_data('000001', start_date='2025-01-01', end_date='2025-03-01')

if df is not None:
    # 进行ATR分析
    results = atr_analysis(df, period=14, method='wilder')
    
    print("📊 ATR分析结果:")
    print(f"当前ATR值: {results.get('current_atr', 0):.4f}")
    
    if 'stop_loss_long' in results:
        print(f"多头止损位: {results['stop_loss_long']:.2f}")
        print(f"空头止损位: {results['stop_loss_short']:.2f}")
    
    if 'trend_analysis' in results:
        trend = results['trend_analysis']
        print(f"ATR趋势: {trend.get('atr_trend', '未知')}")
        print(f"波动性水平: {trend.get('volatility_level', '未知')}")
    
    if 'trading_suggestions' in results:
        print("\\n💡 交易建议:")
        for suggestion in results['trading_suggestions']:
            print(f"  • {suggestion}")
else:
    print("❌ 无法获取数据")
'''
    
    return example_code

# 测试函数
if __name__ == "__main__":
    print("🧪 ATR模块集成测试")
    print("=" * 50)
    
    # 创建测试数据
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    dates = pd.date_range('2025-01-01', periods=50, freq='D')
    data = {
        'date': dates,
        'open': np.random.normal(100, 5, 50),
        'high': np.random.normal(105, 5, 50),
        'low': np.random.normal(95, 5, 50),
        'close': np.random.normal(100, 5, 50),
    }
    
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    
    print("测试ATR分析...")
    results = atr_analysis(df)
    
    print(f"当前ATR: {results.get('current_atr', 0):.4f}")
    
    if 'stop_loss_long' in results:
        print(f"多头止损: {results['stop_loss_long']:.2f}")
        print(f"空头止损: {results['stop_loss_short']:.2f}")
    
    if 'trend_analysis' in results:
        print(f"ATR趋势: {results['trend_analysis'].get('atr_trend', '未知')}")
    
    if 'trading_suggestions' in results:
        print("\\n交易建议:")
        for suggestion in results['trading_suggestions']:
            print(f"  • {suggestion}")
    
    print("\n✅ ATR模块集成测试通过！")