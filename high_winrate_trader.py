        target_price = current_price * (1 + target_return / 100)
        stop_loss_price = current_price * (1 - stop_loss / 100)
        risk_reward = target_return / stop_loss if stop_loss > 0 else 0
        
        # 买入条件
        buy_conditions = []
        if technical_data.get("price_position", 50) < 60:
            buy_conditions.append("价格位置适中(<60%)")
        if technical_data.get("rsi", 50) < 70:
            buy_conditions.append("RSI未超买(<70)")
        if 1.0 < technical_data.get("volume_ratio", 1.0) < 1.8:
            buy_conditions.append("成交量温和放大")
        
        # 止损条件
        stop_conditions = [
            f"价格跌破¥{stop_loss_price:.2f} (止损{stop_loss}%)",
            "RSI>80 (严重超买)",
            "成交量持续萎缩(量比<0.7)",
            f"持有超过{holding_days+3}天未达目标"
        ]
        
        return {
            "buy_price": buy_price,
            "target_price": target_price,
            "stop_loss_price": stop_loss_price,
            "position_size": position,
            "holding_days": holding_days,
            "expected_return": target_return,
            "expected_risk": stop_loss,
            "risk_reward_ratio": risk_reward,
            "buy_conditions": buy_conditions,
            "stop_conditions": stop_conditions,
            "risk_level": risk_level
        }
    
    def _estimate_win_rate(self, fundamental: Dict, technical: Dict, risk: Dict) -> float:
        """估计胜率"""
        fund_score = fundamental.get("score", 0)
        tech_score = technical.get("score", 0)
        risk_level = risk.get("risk_data", {}).get("risk_level", "中")
        
        # 基础胜率
        base_win_rate = 50.0
        
        # 基本面加分
        if fund_score >= 7:
            base_win_rate += 10
        elif fund_score >= 5:
            base_win_rate += 5
        
        # 技术面加分
        if tech_score >= 7:
            base_win_rate += 15
        elif tech_score >= 5:
            base_win_rate += 8
        
        # 风险等级调整
        risk_adjustment = {
            "低": 5,
            "中": 0,
            "中高": -5,
            "高": -10
        }
        base_win_rate += risk_adjustment.get(risk_level, 0)
        
        # 限制范围
        win_rate = max(40, min(85, base_win_rate))
        
        return win_rate
    
    def print_analysis_report(self, name: str, code: str):
        """打印分析报告"""
        print(f"\n{'='*80}")
        print(f"🎯 {name} ({code}) - 高胜率策略分析")
        print(f"{'='*80}")
        
        result = self.analyze_stock(name, code)
        if not result:
            print("❌ 分析失败")
            return
        
        print(f"\n📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        if result["status"] == "REJECTED":
            print(f"\n🔴 分析结果: 不通过")
            print(f"   原因: {result.get('reason', '未知原因')}")
            print(f"   建议: {result.get('recommendation', '不买入')}")
            print(f"   置信度: {result.get('confidence', '高')}")
        else:
            print(f"\n✅ 分析结果: 通过")
            
            fundamental = result["fundamental_analysis"]
            technical = result["technical_analysis"]
            risk = result["risk_analysis"]
            trade_plan = result["trade_plan"]
            
            print(f"\n📊 基本面评分: {fundamental.get('score', 0)}/10")
            print(f"📈 技术面评分: {technical.get('score', 0)}/10")
            print(f"⚠️ 风险等级: {risk.get('risk_data', {}).get('risk_level', '中')}")
            print(f"🎯 预估胜率: {result.get('win_rate_estimate', 0):.1f}%")
            
            print(f"\n📝 交易计划:")
            print(f"   建议买入价: ¥{trade_plan.get('buy_price', 0):.2f}")
            print(f"   目标价位: ¥{trade_plan.get('target_price', 0):.2f} (+{trade_plan.get('expected_return', 0)}%)")
            print(f"   止损价位: ¥{trade_plan.get('stop_loss_price', 0):.2f} (-{trade_plan.get('expected_risk', 0)}%)")
            print(f"   风险收益比: {trade_plan.get('risk_reward_ratio', 0):.2f}")
            print(f"   建议仓位: {trade_plan.get('position_size', 0)*100:.0f}%")
            print(f"   建议持有: {trade_plan.get('holding_days', 0)}天")
            
            print(f"\n✅ 买入条件:")
            for condition in trade_plan.get("buy_conditions", []):
                print(f"   • {condition}")
            
            print(f"\n🚨 止损条件:")
            for condition in trade_plan.get("stop_conditions", []):
                print(f"   • {condition}")
            
            print(f"\n💡 策略说明:")
            print("   1. 追求高胜率(>60%)，宁可错过不做错")
            print("   2. 严格风险控制，单笔最大亏损<2%")
            print("   3. 多重筛选，只做高概率交易")
            print("   4. 明确的买入、持有、卖出条件")
        
        print(f"\n{'='*80}")
        print("🎯 核心策略: 追求高胜率，严格风险控制")
        print("           只做高概率交易，宁可错过不做错")
        print(f"{'='*80}")

# 主函数
def main():
    """测试高胜率交易系统"""
    trader = HighWinrateTrader()
    
    print("🚀 高胜率短线交易系统")
    print("="*80)
    print("📚 追求高胜率，严格风险控制")
    print("="*80)
    
    stocks = [
        ("华胜天成", "600410"),
        ("拓维信息", "002261"),
        ("航锦科技", "000818")
    ]
    
    for name, code in stocks:
        trader.print_analysis_report(name, code)
    
    print("\n✅ 系统特点:")
    print("   1. 三重筛选: 基本面 + 技术面 + 风险面")
    print("   2. 严格标准: 宁可错过，不可做错")
    print("   3. 明确计划: 具体的买入、持有、卖出条件")
    print("   4. 风险控制: 单笔最大亏损<2%，仓位管理")
    print("   5. 胜率优先: 追求>60%的胜率")
    
    print("\n📊 下一步:")
    print("   1. 连接真实财务数据源")
    print("   2. 进行历史回测验证胜率")
    print("   3. 优化筛选标准和参数")
    print("   4. 开发更多高胜率策略")

if __name__ == "__main__":
    main()