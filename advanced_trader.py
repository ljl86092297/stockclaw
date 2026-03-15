            conn.commit()
            conn.close()
            
            print(f"  ✅ 分析记录已保存 (ID: {analysis_id})")
            return analysis_id
            
        except Exception as e:
            print(f"  ❌ 保存失败: {e}")
            return None
    
    def print_advanced_report(self, stock_code: str):
        """打印高级分析报告"""
        print(f"\n{'='*80}")
        print(f"🎯 {stock_code} 高级分析报告（集成ADX）")
        print(f"{'='*80}")
        
        # 运行分析
        result = self.analyze_with_adx(stock_code)
        
        if not result:
            print("❌ 分析失败")
            return
        
        base = result["base_indicators"]
        adx = result["adx_analysis"]
        scores = result["scores"]
        suggestion = result["suggestion"]
        
        print(f"\n📅 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"📊 股票代码: {stock_code}")
        
        print(f"\n📈 基础技术指标:")
        print(f"   当前价格: ¥{base.get('current_price', 0):.2f}")
        print(f"   MA5: ¥{base.get('ma5', 0):.2f}")
        print(f"   MA10: ¥{base.get('ma10', 0):.2f}")
        print(f"   MA20: ¥{base.get('ma20', 0):.2f} (关键支撑)")
        print(f"   量比: {base.get('volume_ratio', 0):.2f}")
        print(f"   5日涨幅: {base.get('change_5d', 0):.1f}%")
        print(f"   价格位置: {base.get('price_position', 0):.1f}%")
        
        print(f"\n📊 ADX趋势分析:")
        print(f"   ADX值: {adx.get('adx_value', 0):.2f}")
        print(f"   +DI: {adx.get('plus_di', 0):.2f}")
        print(f"   -DI: {adx.get('minus_di', 0):.2f}")
        print(f"   趋势强度: {adx.get('trend_strength', '未知')}")
        print(f"   趋势方向: {adx.get('trend_direction', '未知')}")
        print(f"   ADX解读: {adx.get('adx_interpretation', '未知')}")
        if adx.get('adx_reason'):
            print(f"   理由: {adx.get('adx_reason')}")
        
        print(f"\n🏆 综合评分:")
        print(f"   技术面: {scores.get('technical_score', 0)}/4")
        print(f"   趋势面: {scores.get('trend_score', 0)}/4")
        print(f"   成交量: {scores.get('volume_score', 0)}/2")
        print(f"   总评分: {scores.get('total_score', 0)}/9")
        
        print(f"\n📝 交易建议:")
        print(f"   评级: {suggestion.get('recommendation', '未知')}")
        print(f"   置信度: {suggestion.get('confidence', '未知')}")
        
        if suggestion.get("recommendation") in ["强烈买入", "买入"]:
            print(f"\n🎯 具体操作:")
            print(f"   建议买入价: ¥{suggestion.get('buy_price', 0):.2f}")
            print(f"   目标价位: ¥{suggestion.get('target_price', 0):.2f} (+{suggestion.get('expected_return', 0)}%)")
            print(f"   止损价位: ¥{suggestion.get('stop_loss_price', 0):.2f} (-{suggestion.get('expected_risk', 0)}%)")
            print(f"   建议持有: {suggestion.get('holding_days', 0)} 天")
            print(f"   建议仓位: {suggestion.get('position_size', 0)*100:.0f}%")
            print(f"   风险收益比: {suggestion.get('risk_reward_ratio', 0):.2f}")
            
            print(f"\n⚡ 买入理由:")
            print(f"   {suggestion.get('reasoning', '')}")
            
            if suggestion.get('adx_suggestion'):
                print(f"\n📊 ADX建议:")
                print(f"   {suggestion.get('adx_suggestion')}")
        
        elif suggestion.get("recommendation") == "持有":
            print(f"\n🟡 操作建议:")
            print(f"   等待价格: ¥{suggestion.get('buy_price', 0):.2f} 以下")
            print(f"   如已持有，止损位: ¥{suggestion.get('stop_loss_price', 0):.2f}")
            print(f"   {suggestion.get('reasoning', '')}")
        
        elif suggestion.get("recommendation") == "卖出":
            print(f"\n🔴 操作建议:")
            print(f"   建议卖出或不买入")
            print(f"   {suggestion.get('reasoning', '')}")
        
        print(f"\n💡 系统进步:")
        print("   1. ✅ 集成ADX趋势分析")
        print("   2. ✅ 综合评分系统（技术+趋势+成交量）")
        print("   3. ✅ 详细的买入/卖出理由")
        print("   4. ✅ 数据库记录完整分析")
        
        print(f"\n📋 记录信息:")
        print(f"   分析ID: {result.get('suggestion', {}).get('analysis_id', 'N/A')}")
        print(f"   数据库: {self.db_path}")
        print(f"   明天可查询具体表现")
        
        print(f"\n{'='*80}")
        print("🎯 短线核心: ADX过滤震荡市，只交易明显趋势")
        print(f"{'='*80}\n")

# 主函数
if __name__ == "__main__":
    trader = AdvancedTrader()
    
    print("🚀 高级短线交易系统（集成ADX）")
    print("="*50)
    
    # 分析云天化
    trader.print_advanced_report("600096")
    
    print("✅ 系统功能:")
    print("   1. ADX趋势分析 - 过滤震荡市")
    print("   2. 综合评分系统 - 技术+趋势+成交量")
    print("   3. 详细操作建议 - 具体价格和时间")
    print("   4. 数据库记录 - 完整分析历史")
    print("   5. 绩效追踪 - 可查询具体盈亏")
    
    print(f"\n📅 明天收盘后查询:")
    print("   '今天云天化的ADX趋势如何？'")
    print("   '具体盈亏是多少？'")
    print("   '为什么会有这个结果？'")
    print("   '基于ADX有什么优化建议？'")