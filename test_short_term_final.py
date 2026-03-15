#!/usr/bin/env python3
"""
测试短线交易系统 - 最终版
"""

import sys
sys.path.append('/home/openclaw/.openclaw/workspace')

# 创建短线交易器
from short_term_trader_fixed import ShortTermTrader

trader = ShortTermTrader()

print("🚀 测试短线交易系统")
print("="*50)

# 测试股票列表
test_stocks = ["600096", "000001", "000002", "600036"]

print("\n1. 📊 分析单只股票（云天化）")
print("-"*40)
result = trader.analyze_stock("600096")
if result:
    print(f"   股票: {result['stock_code']}")
    print(f"   当前价: ¥{result['current_price']:.2f}")
    print(f"   建议: {result['recommendation']}")
    print(f"   预期收益: {result['expected_return']}%")
    print(f"   持有天数: {result['holding_days']} 天")

print("\n2. 🔍 多股分析并找出最优")
print("-"*40)
best = trader.find_best_stock(test_stocks)
if best:
    print(f"   最优股票: {best['stock_code']}")
    print(f"   理由: 评分{best['score']}/12最高")
    print(f"         预期收益{best['expected_return']}%")
    print(f"         风险收益比{best['risk_reward']:.2f}")

print("\n3. 💾 模拟记录交易")
print("-"*40)
if result and 'suggestion_id' in result:
    # 模拟买入价：比建议买入价低1%
    buy_price = result['buy_price'] * 0.99
    # 模拟卖出价：达到目标价
    sell_price = result['target_price']
    position = result['position']
    
    trader.record_trade(result['suggestion_id'], buy_price, sell_price, position)
    
    print(f"   模拟交易记录完成")
    print(f"   买入价: ¥{buy_price:.2f}")
    print(f"   卖出价: ¥{sell_price:.2f}")
    print(f"   预期盈亏: +{result['expected_return']}%")

print("\n4. 📈 获取绩效总结")
print("-"*40)
summary = trader.get_performance_summary(7)
if summary:
    for key, value in summary.items():
        print(f"   {key}: {value}")

print("\n5. 🔄 策略优化")
print("-"*40)
trader.optimize_strategy()

print("\n✅ 系统测试完成")
print("\n📋 明天收盘后你可以问我：")
print("   1. '今天交易的盈亏情况'")
print("   2. '分析一下为什么盈利/亏损'")
print("   3. '看看最近的交易表现'")
print("   4. '给我优化建议'")
print("   5. '分析这几只股票，找出最好的'")

print("\n💾 数据库文件: short_term_trades.db")
print("📁 本地存储，不上传Git")
print("🔧 所有分析、建议、交易记录都会保存")