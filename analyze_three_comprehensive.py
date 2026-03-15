            suggestions.append("建议：可考虑买入，控制仓位")
    elif recommendation in ["减持", "卖出"]:
        suggestions.append("建议：规避或减仓")
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")
    
    # 关键结论
    print(f"\n{'='*80}")
    print("🎯 关键结论:")
    
    if recommendation in ["强烈买入", "买入"]:
        print("   1. 虽有上涨潜力，但需注意风险控制")
        print("   2. 建议分批买入，严格止损")
        print("   3. 关注成交量变化和RSI指标")
    elif recommendation in ["持有观望"]:
        print("   1. 无明显优势，建议等待更好时机")
        print("   2. 如已持有，可继续观察")
        print("   3. 关注基本面改善信号")
    else:
        print("   1. 风险较高，建议规避")
        print("   2. 如已持有，考虑减仓")
        print("   3. 等待风险释放后再考虑")
    
    print(f"\n📅 下次评估: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*80}")

def main():
    """主函数"""
    print("🚀 三只股票全面分析系统")
    print("="*80)
    print("📚 包含：基本面 + 技术面 + 风险分析")
    print("="*80)
    
    stocks = [
        ("华胜天成", "600410"),
        ("拓维信息", "002261"),
        ("航锦科技", "000818")
    ]
    
    for name, code in stocks:
        analyze_stock_comprehensive(name, code)
    
    print("\n✅ 分析完成")
    print("💡 记住：投资有风险，决策需谨慎")
    print("📊 本分析基于多维度评估，但仍需结合市场环境和个人风险承受能力")

if __name__ == "__main__":
    main()