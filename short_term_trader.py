    for i, result in enumerate(results[:3], 1):
        print(f"{i}. {result['stock_code']}: {result['recommendation']} (预期收益: {result['expected_return']}%)")
    
    # 3. 找出最优
    best = trader.find_best_stock(test_stocks)
    if best:
        print(f"\n🏆 最优选择: {best['stock_code']}")
        print(f"   理由: 评分最高({best['score']}/12)，预期收益{best['expected_return']}%")
        print(f"         风险收益比{best['risk_reward']:.2f}，持有{best['holding_days']}天")
    
    # 4. 策略优化
    trader.optimize_strategy()
    
    print(f"\n✅ 系统功能总结:")
    print(f"   1. 短线分析: 1-14天持有，5-20%目标收益")
    print(f"   2. 多股对比: 自动找出最优股票")
    print(f"   3. 绩效追踪: 记录盈亏，分析原因")
    print(f"   4. 策略优化: 基于历史表现自动调整")
    print(f"   5. 数据库: {trader.db_path} (本地存储)")
    
    print(f"\n📅 明天收盘后:")
    print(f"   1. 可查询具体盈亏")
    print(f"   2. 可分析盈利/亏损原因")
    print(f"   3. 可查看策略优化建议")
    print(f"   4. 可对比多股表现")