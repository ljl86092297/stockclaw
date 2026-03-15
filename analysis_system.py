        print(f"成交量状态: {tech_details.get('volume_status', '未知')}")
        
        print(f"\n{'─'*40}")
        print("🏢 基本面指标")
        print(f"{'─'*40}")
        print(f"市盈率(PE): {fundamental.get('pe_ratio', 'N/A')}")
        print(f"市净率(PB): {fundamental.get('pb_ratio', 'N/A')}")
        print(f"市销率(PS): {fundamental.get('ps_ratio', 'N/A')}")
        print(f"营业收入: ¥{fundamental.get('revenue', 0):,.0f} 万元")
        print(f"净利润: ¥{fundamental.get('net_profit', 0):,.0f} 万元")
        print(f"每股收益: {fundamental.get('eps', 'N/A')}")
        print(f"基本面评分: {fundamental.get('fundamental_score', 0)}/10")
        
        print(f"\n{'─'*40}")
        print("📰 新闻与情绪")
        print(f"{'─'*40}")
        print(f"新闻数量: {news.get('news_count', 0)} 条")
        print(f"正面新闻: {news.get('positive_news', 0)} 条")
        print(f"负面新闻: {news.get('negative_news', 0)} 条")
        print(f"情绪得分: {news.get('sentiment_score', 0):.2f} (-1到1)")
        print(f"热点主题: {', '.join(news.get('hot_themes', []))}")
        
        print(f"\n{'═'*80}")
        print("💡 具体投资建议")
        print(f"{'═'*80}")
        
        print(f"\n🏆 综合评分: {recommendation.get('overall_score', 0):.1f}/10")
        print(f"📊 投资评级: {recommendation.get('investment_rating', '未知')}")
        print(f"🛒 买入建议: {recommendation.get('buy_recommendation', '未知')}")
        
        print(f"\n🎯 具体操作建议")
        print(f"{'─'*40}")
        print(f"买入价格区间: ¥{recommendation.get('buy_price_range', '未知')}")
        print(f"卖出目标价位: ¥{recommendation.get('sell_price_targets', '未知')}")
        print(f"止损价位: ¥{recommendation.get('stop_loss_price', 0):.2f}")
        print(f"建议持有周期: {recommendation.get('holding_period', '未知')}")
        
        print(f"\n⚡ 买入触发条件:")
        for trigger in recommendation.get('buy_triggers', []):
            print(f"  • {trigger}")
        
        if not recommendation.get('buy_triggers'):
            print(f"  • 暂无明确买入触发条件")
        
        print(f"\n🚨 卖出触发条件:")
        for trigger in recommendation.get('sell_triggers', []):
            print(f"  • {trigger}")
        
        if not recommendation.get('sell_triggers'):
            print(f"  • 暂无明确卖出触发条件")
        
        print(f"\n🛑 止损触发条件:")
        for trigger in recommendation.get('stop_triggers', []):
            print(f"  • {trigger}")
        
        print(f"\n🔄 需要重新评估的情况:")
        for condition in recommendation.get('re_evaluate_conditions', []):
            print(f"  • {condition}")
        
        print(f"\n📅 下次评估时间: {recommendation.get('next_review_date', '未知')}")
        
        print(f"\n{'═'*80}")
        print("📋 最终决策")
        print(f"{'═'*80}")
        
        rating = recommendation.get('investment_rating', '')
        buy_rec = recommendation.get('buy_recommendation', '')
        
        if "强烈买入" in rating or "强烈推荐" in buy_rec:
            print("✅ 决策: 立即买入")
            print("   理由: 综合评分高，技术面、基本面、情绪面均支持买入")
        elif "买入" in rating or "推荐" in buy_rec:
            print("✅ 决策: 建议买入")
            print("   理由: 整体评估积极，适合分批建仓")
        elif "持有" in rating or "谨慎" in buy_rec:
            print("🟡 决策: 观望/持有")
            print("   理由: 无明显优势，建议等待更好时机")
        elif "卖出" in rating or "不推荐" in buy_rec:
            print("🔴 决策: 建议卖出/不买入")
            print("   理由: 存在明显风险或劣势")
        elif "强烈卖出" in rating or "强烈不推荐" in buy_rec:
            print("🔴 决策: 立即卖出/坚决不买入")
            print("   理由: 高风险，建议规避")
        else:
            print("❓ 决策: 无法确定")
            print("   理由: 数据不足或分析异常")
        
        print(f"\n💎 核心观点:")
        current_price = technical.get('current_price', 0)
        stop_loss = recommendation.get('stop_loss_price', 0)
        buy_range = recommendation.get('buy_price_range', '')
        
        if current_price > 0 and stop_loss > 0:
            risk_percent = (current_price - stop_loss) / current_price * 100
            print(f"   当前价: ¥{current_price:.2f}")
            print(f"   潜在风险: {risk_percent:.1f}% (到止损位)")
            
            if risk_percent < 5:
                print(f"   风险可控，适合操作")
            elif risk_percent < 10:
                print(f"   风险中等，需谨慎")
            else:
                print(f"   风险较高，建议轻仓")
        
        print(f"\n📈 后续跟踪:")
        print(f"   1. 监控价格是否进入买入区间: {buy_range}")
        print(f"   2. 关注新闻情绪变化")
        print(f"   3. 观察技术形态演变")
        print(f"   4. 在{recommendation.get('next_review_date', '3天后')}重新评估")
        
        print(f"\n{'='*80}")
        print("⚠️ 风险提示: 投资有风险，入市需谨慎。本分析仅供参考。")
        print(f"{'='*80}\n")


# 主函数
if __name__ == "__main__":
    # 测试分析系统
    system = StockAnalysisSystem()
    
    # 分析云天化
    system.run_complete_analysis("600096")
    
    # 获取分析历史
    print("\n📚 分析历史记录:")
    history = system.get_analysis_history("600096", limit=3)
    for record in history:
        print(f"  {record['analysis_date']}: {record['investment_rating']} (评分: {record['overall_score']:.1f})")
    
    # 绩效回顾
    system.review_performance()