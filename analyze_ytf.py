#!/usr/bin/env python3
"""
云天化短线分析 - 展示系统长进
"""

import sys
sys.path.append('/home/openclaw/.openclaw/workspace')

# 导入修复后的短线交易系统
exec(open('fast_trader_fixed.py').read())

# 创建交易者
trader = FastTrader()

print("🚀 云天化（600096）短线分析")
print("="*50)

# 分析云天化
result = trader.analyze("600096")

if result:
    print(f"\n📊 具体指标数值:")
    print(f"   当前价格: ¥{result['price']:.2f}")
    print(f"   MA5: ¥{result['ma5']:.2f}")
    print(f"   量比: {result['vol_ratio']:.2f}")
    print(f"   5日涨幅: {result['change_5d']:.1f}%")
    print(f"   短线评分: {result['score']}/10")
    
    print(f"\n📝 投资建议（文字描述）:")
    
    if result['rec'] == "强烈买入":
        print("   ✅ 强烈建议买入")
        print(f"      建议买入价: ¥{result['buy']:.2f}")
        print(f"      目标价位: ¥{result['target']:.2f} (预期收益: {result['exp_return']}%)")
        print(f"      止损价位: ¥{result['stop']:.2f}")
        print(f"      建议持有: {result['days']}天")
        print(f"      建议仓位: {result['pos']*100:.0f}%")
        print(f"      风险收益比: {result['risk_reward']:.2f}")
        
        print(f"\n   ⚡ 买入理由:")
        print(f"      1. 短线评分{result['score']}/10，技术面强势")
        print(f"      2. 量比{result['vol_ratio']:.2f}，成交量活跃")
        if result['change_5d'] > 5:
            print(f"      3. 5日涨幅{result['change_5d']:.1f}%，趋势向上")
        print(f"      4. 风险收益比{result['risk_reward']:.2f}，性价比高")
        
    elif result['rec'] == "买入":
        print("   ✅ 建议买入")
        print(f"      建议买入价: ¥{result['buy']:.2f}")
        print(f"      目标价位: ¥{result['target']:.2f} (预期收益: {result['exp_return']}%)")
        print(f"      止损价位: ¥{result['stop']:.2f}")
        print(f"      建议持有: {result['days']}天")
        
        print(f"\n   ⚡ 操作要点:")
        print(f"      1. 在{result['buy']:.2f}以下分批买入")
        print(f"      2. 达到{result['target']:.2f}时考虑卖出")
        print(f"      3. 跌破{result['stop']:.2f}立即止损")
        
    elif result['rec'] == "持有":
        print("   🟡 建议持有观望")
        print(f"      等待更好价格: ¥{result['buy']:.2f}以下")
        print(f"      如已持有，止损位: ¥{result['stop']:.2f}")
        
    elif result['rec'] == "卖出":
        print("   🔴 建议卖出或不买入")
        print("      当前技术面偏弱，建议规避")
    
    print(f"\n🚨 风险提示:")
    print(f"   1. 短线交易风险较高，严格止损")
    print(f"   2. 建议仓位控制在{result['pos']*100 if result['pos']>0 else 20:.0f}%以内")
    print(f"   3. 持有时间不超过{result['days'] if result['days']>0 else 7}天")
    
    print(f"\n💡 系统改进:")
    print("   1. 数据库记录所有建议和交易")
    print("   2. 明天可查询具体盈亏和分析原因")
    print("   3. 支持多股对比和策略优化")
    print("   4. 自动分析盈利/亏损原因")
    
    # 保存建议ID供明天查询
    print(f"\n📋 记录信息:")
    print(f"   建议ID: {result['sug_id']}")
    print(f"   数据库: {trader.db}")
    print(f"   明天可查询此建议的实际表现")

else:
    print("❌ 分析失败，系统需要进一步优化")

print(f"\n✅ 分析完成")
print("明天收盘后你可以问我:")
print("1. '今天云天化的表现如何？'")
print("2. '具体盈亏是多少？'")
print("3. '为什么盈利/亏损了？'")
print("4. '有什么优化建议？'")