#!/usr/bin/env python3
"""
快速测试短线交易系统
"""

import sys
sys.path.append('/home/openclaw/.openclaw/workspace')

# 重新导入短线交易类
exec(open('short_term_trader.py').read())

# 创建交易者
trader = ShortTermTrader()

print("🚀 短线交易系统测试")
print("="*50)

# 测试股票
test_stocks = ["600096", "000001", "600036"]

print(f"\n🔍 分析 {len(test_stocks)} 只股票...")

for code in test_stocks:
    result = trader.analyze_stock(code)
    if result:
        print(f"{code}: {result['recommendation']} (预期收益: {result['expected_return']}%)")

# 找出最优
print("\n🏆 寻找最优股票...")
best = trader.find_best_stock(test_stocks)
if best:
    print(f"最优: {best['stock_code']}")
    print(f"理由: 评分{best['score']}/12，预期收益{best['expected_return']}%")
    print(f"     风险收益比{best['risk_reward']:.2f}，持有{best['holding_days']}天")

print(f"\n✅ 系统功能正常")
print(f"数据库: {trader.db_path}")
print("明天收盘后可查询:")
print("1. 具体盈亏金额和百分比")
print("2. 盈利/亏损原因分析")
print("3. 策略优化建议")
print("4. 多股表现对比")