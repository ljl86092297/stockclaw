        elif rsi > 70:
            risk["rsi_risk_level"] = "高"
            risk["rsi_risk_desc"] = f"RSI={rsi:.1f}，超买状态"
        elif rsi < 30:
            risk["rsi_risk_level"] = "低"
            risk["rsi_risk_desc"] = f"RSI={rsi:.1f}，超卖状态"
        else:
            risk["rsi_risk_level"] = "中"
            risk["rsi_risk_desc"] = f"RSI={rsi:.1f}，正常范围"
        
        # 4. 成交量风险
        volume_ratio = technical.get("volume_ratio", 1.0)
        
        if volume_ratio > 2.5:
            risk["volume_risk_level"] = "高"
            risk["volume_risk_desc"] = f"量比{volume_ratio:.2f}，异常放量，需警惕"
        elif volume_ratio > 1.5:
            risk["volume_risk_level"] = "中"
            risk["volume_risk_desc"] = f"量比{volume_ratio:.2f}，放量明显"
        elif volume_ratio < 0.5:
            risk["volume_risk_level"] = "高"
            risk["volume_risk_desc"] = f"量比{volume_ratio:.2f}，严重缩量，流动性风险"
        else:
            risk["volume_risk_level"] = "低"
            risk["volume_risk_desc"] = f"量比{volume_ratio:.2f}，成交量正常"
        
        # 5. 综合风险评估
        risk_levels = {
            "position_risk_level": risk.get("position_risk_level", "中"),
            "short_term_risk_level": risk.get("short_term_risk_level", "中"),
            "rsi_risk_level": risk.get("rsi_risk_level", "中"),
            "volume_risk_level": risk.get("volume_risk_level", "中")
        }
        
        # 风险等级映射为数值
        level_map = {"极高": 4, "高": 3, "中": 2, "低": 1, "极低": 0}
        risk_scores = [level_map.get(level, 2) for level in risk_levels.values()]
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 2
        
        if avg_risk_score >= 3.5:
            risk["overall_risk_level"] = "极高"
            risk["overall_risk_desc"] = "综合风险极高，建议规避"
        elif avg_risk_score >= 2.5:
            risk["overall_risk_level"] = "高"
            risk["overall_risk_desc"] = "综合风险较高，谨慎操作"
        elif avg_risk_score >= 1.5:
            risk["overall_risk_level"] = "中"
            risk["overall_risk_desc"] = "综合风险适中，可适度参与"
        else:
            risk["overall_risk_level"] = "低"
            risk["overall_risk_desc"] = "综合风险较低，相对安全"
        
        risk["risk_score"] = avg_risk_score
        risk["max_risk_score"] = 4
        
        return risk
    
    def _comprehensive_assessment(self, fundamental: Dict, technical: Dict, 
                                 capital: Dict, risk: Dict) -> Dict:
        """综合评估"""
        print("  🎯 综合评估...")
        
        assessment = {}
        
        # 各维度评分
        fund_score = fundamental.get("score", 0)
        tech_score = technical.get("score", 0)
        cap_score = capital.get("score", 0)
        risk_score = risk.get("risk_score", 2)
        
        # 综合评分（考虑风险调整）
        total_score = fund_score + tech_score + cap_score
        max_total = fundamental.get("max_score", 10) + technical.get("max_score", 8) + capital.get("max_score", 5)
        
        # 风险调整：高风险降低评分
        risk_adjustment = 0
        if risk_score >= 3.5:  # 极高风险
            risk_adjustment = -0.4
        elif risk_score >= 2.5:  # 高风险
            risk_adjustment = -0.2
        elif risk_score <= 1.5:  # 低风险
            risk_adjustment = 0.1
        
        adjusted_score = total_score * (1 + risk_adjustment)
        score_percentage = adjusted_score / max_total * 100 if max_total > 0 else 0
        
        assessment["fundamental_score"] = fund_score
        assessment["technical_score"] = tech_score
        assessment["capital_score"] = cap_score
        assessment["risk_score"] = risk_score
        assessment["total_score"] = total_score
        assessment["adjusted_score"] = adjusted_score
        assessment["score_percentage"] = score_percentage
        
        # 投资建议
        if score_percentage >= 70:
            assessment["recommendation"] = "强烈买入"
            assessment["confidence"] = "高"
            assessment["suggested_position"] = 0.20
            assessment["holding_period"] = "3-7天"
        elif score_percentage >= 60:
            assessment["recommendation"] = "买入"
            assessment["confidence"] = "中"
            assessment["suggested_position"] = 0.15
            assessment["holding_period"] = "5-10天"
        elif score_percentage >= 50:
            assessment["recommendation"] = "持有观望"
            assessment["confidence"] = "低"
            assessment["suggested_position"] = 0.10
            assessment["holding_period"] = "等待时机"
        elif score_percentage >= 40:
            assessment["recommendation"] = "减持"
            assessment["confidence"] = "中"
            assessment["suggested_position"] = 0.05
            assessment["holding_period"] = "逐步退出"
        else:
            assessment["recommendation"] = "卖出"
            assessment["confidence"] = "高"
            assessment["suggested_position"] = 0
            assessment["holding_period"] = "立即"
        
        # 关键风险提示
        risk_level = risk.get("overall_risk_level", "中")
        if risk_level in ["极高", "高"]:
            assessment["risk_warning"] = f"⚠️ 高风险警告：{risk.get('overall_risk_desc', '')}"
        else:
            assessment["risk_warning"] = "风险可控"
        
        # 操作建议
        assessment["operation_suggestion"] = self._generate_operation_suggestion(
            fundamental, technical, capital, risk, assessment
        )
        
        return assessment
    
    def _generate_operation_suggestion(self, fundamental: Dict, technical: Dict, 
                                      capital: Dict, risk: Dict, assessment: Dict) -> str:
        """生成具体操作建议"""
        suggestions = []
        
        # 基本面建议
        if fundamental.get("profit_growth", 0) < 0:
            suggestions.append("基本面：业绩下滑，需谨慎")
        
        if fundamental.get("pe_ratio", 0) > 30:
            suggestions.append("估值：市盈率偏高")
        
        # 技术面建议
        if technical.get("price_position", 50) > 70:
            suggestions.append("技术面：价格处于高位，回调风险大")
        
        if technical.get("change_5d", 0) > 15:
            suggestions.append("短期：涨幅过大，不宜追高")
        
        if technical.get("rsi", 50) > 70:
            suggestions.append("指标：RSI超买，等待回调")
        
        # 资金面建议
        if capital.get("price_volume_relation", "") == "价升量缩（谨慎）":
            suggestions.append("资金面：量价背离，需警惕")
        
        # 风险面建议
        if risk.get("overall_risk_level", "中") in ["极高", "高"]:
            suggestions.append(f"风险：{risk.get('overall_risk_desc', '高风险')}")
        
        # 综合建议
        if assessment["recommendation"] in ["强烈买入", "买入"]:
            if suggestions:
                suggestions.append("建议：如要买入，应分批建仓，严格止损")
            else:
                suggestions.append("建议：可考虑买入，控制仓位")
        elif assessment["recommendation"] in ["减持", "卖出"]:
            suggestions.append("建议：规避或减仓")
        
        return "；".join(suggestions) if suggestions else "无明显操作建议"
    
    def print_comprehensive_report(self, name: str, code: str):
        """打印全面分析报告"""
        print(f"\n{'='*80}")
        print(f"📊 {name} ({code}) 全面分析报告")
        print(f"{'='*80}")
        
        result = self.analyze_stock_comprehensive(name, code)
        if not result:
            print("❌ 分析失败")
            return
        
        fundamental = result["fundamental"]
        technical = result["technical"]
        capital = result["capital"]
        risk = result["risk"]
        assessment = result["assessment"]
        
        # 基本信息
        print(f"\n📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"📈 当前价格: ¥{technical.get('current_price', 0):.2f}")
        
        # 基本面
        print(f"\n📊 基本面分析:")
        print(f"   市盈率(PE): {fundamental.get('pe_ratio', 0):.1f} - {fundamental.get('valuation_comment', '')}")
        print(f"   净资产收益率(ROE): {fundamental.get('roe', 0):.1f}% - {fundamental.get('profitability_comment', '')}")
        print(f"   利润增长率: {fundamental.get('profit_growth', 0):.1f}% - {fundamental.get('growth_comment', '')}")
        print(f"   负债率: {fundamental.get('debt_ratio', 0):.1f}% - {fundamental.get('health_comment', '')}")
        print(f"   评分: {fundamental.get('score', 0)}/{fundamental.get('max_score', 10)}")
        
        # 技术面
        print(f"\n📈 技术面分析:")
        print(f"   趋势: {technical.get('trend_type', '')} ({technical.get('trend_strength', '')})")
        print(f"   均线: MA5=¥{technical.get('ma5', 0):.2f}, MA20=¥{technical.get('ma20', 0):.2f}")
        print(f"   价格位置: {technical.get('price_position', 0):.1f}% - {technical.get('position_risk', '')}")
        print(f"   短期涨幅: 5日{technical.get('change_5d', 0):.1f}%, 20日{technical.get('change_20d', 0):.1f}%")
        print(f"   成交量: 量比{technical.get('volume_ratio', 0):.2f} ({technical.get('volume_status', '')})")
        print(f"   RSI: {technical.get('rsi', 0):.1f}")
        print(f"   评分: {technical.get('score', 0)}/{technical.get('max_score', 8)}")
        
        # 资金面
        print(f"\n💰 资金面分析:")
        print(f"   量价关系: {capital.get('price_volume_relation', '')}")
        print(f"   机构参与: {capital.get('institutional_participation', '')}")
        print(f"   评分: {capital.get('score', 0)}/{capital.get('max_score', 5)}")
        
        # 风险分析
        print(f"\n⚠️ 风险分析:")
        print(f"   位置风险: {risk.get('position_risk_level', '')} - {risk.get('position_risk_desc', '')}")
        print(f"   短期风险: {risk.get('short_term_risk_level', '')} - {risk.get('short_term_risk_desc', '')}")
        print(f"   RSI风险: {risk.get('rsi_risk_level', '')} - {risk.get('rsi_risk_desc', '')}")
        print(f"   成交量风险: {risk.get('volume_risk_level', '')} - {risk.get('volume_risk_desc', '')}")
        print(f"   综合风险: {risk.get('overall_risk_level', '')} - {risk.get('overall_risk_desc', '')}")
        print(f"   风险评分: {risk.get('risk_score', 0):.1f}/{risk.get('max_risk_score', 4)}")
        
        # 综合评估
        print(f"\n🎯 综合评估:")
        print(f"   基本面评分: {assessment.get('fundamental_score', 0)}")
        print(f"   技术面评分: {assessment.get('technical_score', 0)}")
        print(f"   资金面评分: {assessment.get('capital_score', 0)}")
        print(f"   风险评分: {assessment.get('risk_score', 0):.1f}")
        print(f"   总评分: {assessment.get('total_score', 0)} → 调整后: {assessment.get('adjusted_score', 0):.1f}")
        print(f"   评分百分比: {assessment.get('score_percentage', 0):.1f}%")
        
        print(f"\n📝 投资建议:")
        print(f"   评级: {assessment.get('recommendation', '')} ({assessment.get('confidence', '')}置信度)")
        print(f"   建议仓位: {assessment.get('suggested_position', 0)*100:.0f}%")
        print(f"   建议持有: {assessment.get('holding_period', '')}")
        
        if assessment.get('risk_warning'):
            print(f"   {assessment.get('risk_warning')}")
        
        print(f"\n💡 操作建议:")
        print(f"   {assessment.get('operation_suggestion', '')}")
        
        # 关键结论
        print(f"\n{'='*80}")
        print("🎯 关键结论:")
        
        if assessment["recommendation"] in ["强烈买入", "买入"]:
            print("   1. 虽有上涨潜力，但需注意风险控制")
            print("   2. 建议分批买入，严格止损")
            print("   3. 关注成交量变化和RSI指标")
        elif assessment["recommendation"] in ["持有观望"]:
            print("   1. 无明显优势，建议等待更好时机")
            print("   2. 如已持有，可继续观察")
            print("   3. 关注基本面改善信号")
        else:
            print("   1. 风险较高，建议规避")
            print("   2. 如已持有，考虑减仓")
            print("   3. 等待风险释放后再考虑")
        
        print(f"\n📅 下次评估: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*80}")

# 主函数
if __name__ == "__main__":
    analyzer = ComprehensiveAnalyzer()
    
    # 分析三只股票
    stocks = [
        ("华胜天成", "600410"),
        ("拓维信息", "002261"),
        ("航锦科技", "000818")
    ]
    
    print("🚀 全面股票分析系统")
    print("="*80)
    print("📚 包含：基本面 + 技术面 + 资金面 + 风险分析")
    print("="*80)
    
    for name, code in stocks:
        analyzer.print_comprehensive_report(name, code)
    
    print("\n✅ 分析完成")
    print("💡 记住：投资有风险，决策需谨慎")
    print("📊 本分析基于多维度评估，但仍需结合市场环境和个人风险承受能力")