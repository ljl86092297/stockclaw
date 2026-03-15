            suggestion_id,))
            suggestion = cursor.fetchone()
            
            if not suggestion:
                print("❌ 未找到对应建议")
                return
            
            stock_code = suggestion[1]
            
            # 计算盈亏
            profit_loss_amount = (sell_price - buy_price) * position_size
            profit_loss_percent = (sell_price - buy_price) / buy_price * 100
            
            # 判断交易结果
            if profit_loss_percent > 1:
                trade_result = "profit"
                profit_reason = self._analyze_profit_reason(suggestion, buy_price, sell_price)
                loss_reason = ""
            elif profit_loss_percent < -1:
                trade_result = "loss"
                profit_reason = ""
                loss_reason = self._analyze_loss_reason(suggestion, buy_price, sell_price)
            else:
                trade_result = "breakeven"
                profit_reason = loss_reason = ""
            
            # 计算持有天数（简化）
            buy_time = datetime.now() - timedelta(days=3)  # 假设3天前买入
            sell_time = datetime.now()
            holding_days = (sell_time - buy_time).days
            
            # 记录交易
            cursor.execute('''
            INSERT INTO actual_trades (
                suggestion_id, stock_code, buy_time, buy_price,
                sell_time, sell_price, position_size, actual_return,
                actual_holding_days, trade_result, profit_loss_amount,
                profit_loss_percent, profit_reason, loss_reason, lessons_learned
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                suggestion_id,
                stock_code,
                buy_time.strftime('%Y-%m-%d %H:%M:%S'),
                buy_price,
                sell_time.strftime('%Y-%m-%d %H:%M:%S'),
                sell_price,
                position_size,
                profit_loss_percent,
                holding_days,
                trade_result,
                profit_loss_amount,
                profit_loss_percent,
                profit_reason,
                loss_reason,
                self._generate_lessons_learned(suggestion, profit_loss_percent)
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ 实际交易记录已保存")
            print(f"   盈亏: {profit_loss_percent:.2f}% ({profit_loss_amount:.2f}元)")
            print(f"   结果: {trade_result}")
            
        except Exception as e:
            print(f"❌ 记录交易失败: {e}")
    
    def _analyze_profit_reason(self, suggestion: tuple, buy_price: float, sell_price: float) -> str:
        """分析盈利原因"""
        reasons = []
        
        # 从suggestion中提取数据
        expected_return = suggestion[24] if len(suggestion) > 24 else 0
        actual_return = (sell_price - buy_price) / buy_price * 100
        
        if actual_return > expected_return:
            reasons.append("实际收益超过预期")
        
        # 技术面原因
        volume_ratio = suggestion[7] if len(suggestion) > 7 else 0
        if volume_ratio > 1.5:
            reasons.append("成交量配合良好")
        
        change_5d = suggestion[8] if len(suggestion) > 8 else 0
        if change_5d > 5:
            reasons.append("短期趋势强劲")
        
        return "; ".join(reasons) if reasons else "技术面与基本面配合良好"
    
    def _analyze_loss_reason(self, suggestion: tuple, buy_price: float, sell_price: float) -> str:
        """分析亏损原因"""
        reasons = []
        
        # 止损执行
        stop_loss_price = suggestion[19] if len(suggestion) > 19 else 0
        if sell_price <= stop_loss_price:
            reasons.append("触发止损")
        
        # 技术面原因
        volume_ratio = suggestion[7] if len(suggestion) > 7 else 0
        if volume_ratio < 0.8:
            reasons.append("成交量不足")
        
        change_5d = suggestion[8] if len(suggestion) > 8 else 0
        if change_5d < 0:
            reasons.append("短期趋势转弱")
        
        return "; ".join(reasons) if reasons else "市场环境变化或技术判断失误"
    
    def _generate_lessons_learned(self, suggestion: tuple, actual_return: float) -> str:
        """生成经验教训"""
        expected_return = suggestion[24] if len(suggestion) > 24 else 0
        
        lessons = []
        
        if actual_return > expected_return:
            lessons.append("低估了该股的上涨潜力")
        elif actual_return < expected_return:
            lessons.append("高估了该股的上涨空间")
        
        risk_reward = suggestion[26] if len(suggestion) > 26 else 0
        if risk_reward < 1.5:
            lessons.append("风险收益比不够理想")
        
        return "; ".join(lessons) if lessons else "需要更多数据积累经验"
    
    def optimize_strategy(self):
        """策略优化（基于历史数据）"""
        print("\n🔄 开始策略优化...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 分析历史表现
            cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN trade_result = 'profit' THEN 1 ELSE 0 END) as profitable_trades,
                AVG(profit_loss_percent) as avg_return,
                AVG(actual_holding_days) as avg_holding_days
            FROM actual_trades
            ''')
            
            stats = cursor.fetchone()
            
            if stats and stats[0] > 0:
                total_trades = stats[0]
                profitable_trades = stats[1]
                win_rate = profitable_trades / total_trades * 100
                avg_return = stats[2] or 0
                avg_holding_days = stats[3] or 0
                
                print(f"📊 历史表现统计:")
                print(f"   总交易次数: {total_trades}")
                print(f"   盈利次数: {profitable_trades}")
                print(f"   胜率: {win_rate:.1f}%")
                print(f"   平均收益: {avg_return:.2f}%")
                print(f"   平均持有天数: {avg_holding_days:.1f}")
                
                # 根据表现调整策略
                changes = []
                
                if win_rate < 50:
                    changes.append("提高买入标准，减少交易频率")
                
                if avg_return < 5:
                    changes.append("调整目标收益，优化止损设置")
                
                if avg_holding_days > 7:
                    changes.append("缩短目标持有时间，追求更快周转")
                
                # 记录优化
                if changes:
                    cursor.execute('''
                    INSERT INTO strategy_optimization (
                        optimization_date, parameter_changes, 
                        performance_improvement, optimization_reason
                    ) VALUES (?, ?, ?, ?)
                    ''', (
                        datetime.now().strftime('%Y-%m-%d'),
                        json.dumps(changes),
                        0.1,  # 假设改进10%
                        "基于历史表现自动优化"
                    ))
                    
                    conn.commit()
                    print(f"✅ 策略优化建议: {', '.join(changes)}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 策略优化失败: {e}")
    
    def get_trade_summary(self, days: int = 7) -> Dict:
        """获取交易总结"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN trade_result = 'profit' THEN profit_loss_amount ELSE 0 END) as total_profit,
                SUM(CASE WHEN trade_result = 'loss' THEN profit_loss_amount ELSE 0 END) as total_loss,
                AVG(profit_loss_percent) as avg_return,
                MIN(profit_loss_percent) as worst_trade,
                MAX(profit_loss_percent) as best_trade
            FROM actual_trades
            WHERE sell_time >= ?
            ''', (start_date,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "total_trades": result[0] or 0,
                    "total_profit": result[1] or 0,
                    "total_loss": result[2] or 0,
                    "net_profit": (result[1] or 0) + (result[2] or 0),
                    "avg_return": result[3] or 0,
                    "worst_trade": result[4] or 0,
                    "best_trade": result[5] or 0
                }
            
        except Exception as e:
            print(f"❌ 获取交易总结失败: {e}")
        
        return {}
    
    def print_analysis_report(self, stock_code: str):
        """打印分析报告"""
        result = self.analyze_stock(stock_code)
        
        if "error" in result:
            print(f"❌ {result['error']}")
            return
        
        indicators = result["indicators"]
        suggestion = result["suggestion"]
        
        print(f"\n{'='*80}")
        print(f"🎯 {stock_code} 短线分析报告")
        print(f"{'='*80}")
        
        print(f"\n📊 短线指标:")
        print(f"   当前价: ¥{indicators.get('current_price', 0):.2f}")
        print(f"   MA5: ¥{indicators.get('ma5', 0):.2f}")
        print(f"   MA10: ¥{indicators.get('ma10', 0):.2f}")
        print(f"   量比: {indicators.get('volume_ratio', 0):.2f}")
        print(f"   5日涨幅: {indicators.get('change_5d', 0):.1f}%")
        print(f"   是否涨停: {'是' if indicators.get('is_limit_up', 0) == 1 else '否'}")
        print(f"   KDJ-K: {indicators.get('kdj_k', 0):.1f}")
        print(f"   RSI: {indicators.get('rsi', 0):.1f}")
        
        print(f"\n📝 交易建议:")
        rec_map = {
            "strong_buy": "强烈买入",
            "buy": "买入",
            "hold": "持有",
            "sell": "卖出"
        }
        recommendation = rec_map.get(suggestion.get("recommendation", ""), "未知")
        print(f"   评级: {recommendation} (评分: {suggestion.get('score', 0)}/12)")
        
        if suggestion.get("recommendation") in ["strong_buy", "buy"]:
            print(f"   建议买入价: ¥{suggestion.get('buy_price', 0):.2f}")
            print(f"   目标价: ¥{suggestion.get('target_price', 0):.2f} (+{suggestion.get('expected_return', 0):.1f}%)")
            print(f"   止损价: ¥{suggestion.get('stop_loss_price', 0):.2f} (-{suggestion.get('expected_risk', 0):.1f}%)")
            print(f"   建议持有: {suggestion.get('holding_days', 0)} 天")
            print(f"   建议仓位: {suggestion.get('position_size', 0)*100:.0f}%")
            print(f"   风险收益比: {suggestion.get('risk_reward_ratio', 0):.2f}")
            
            print(f"\n⚡ 买入触发条件:")
            for trigger in suggestion.get("buy_triggers", []):
                print(f"   • {trigger}")
        
        print(f"\n🚨 卖出条件:")
        for trigger in suggestion.get("sell_triggers", []):
            print(f"   • {trigger}")
        
        print(f"\n🛑 止损条件:")
        for trigger in suggestion.get("stop_triggers", []):
            print(f"   • {trigger}")
        
        print(f"\n{'='*80}")
        print("💡 短线操作要点: 快进快出，严格止损，追求5-15%收益")
        print(f"{'='*80}\n")


# 主函数
if __name__ == "__main__":
    # 创建分析器
    analyzer = ShortTermAnalyzer()
    
    # 测试多股分析
    test_stocks = ["600096", "000001", "000002", "600036"]
    
    print("🚀 短线交易分析器启动")
    print("="*50)
    
    # 1. 分析单股
    analyzer.print_analysis_report("600096")
    
    # 2. 多股分析并找出最优
    print("\n🔍 多股对比分析...")
    best = analyzer.find_best_stock(test_stocks)
    
    if "error" not in best:
        print(f"\n🏆 推荐关注: {best['stock_code']}")
        print(f"   理由: 短线评分最高，预期收益{best['suggestion'].get('expected_return', 0):.1f}%")
        print(f"         风险收益比{best['suggestion'].get('risk_reward_ratio', 0):.2f}")
        print(f"         建议持有{best['suggestion'].get('holding_days', 0)}天")
    
    # 3. 策略优化（模拟）
    analyzer.optimize_strategy()
    
    print(f"\n✅ 系统已就绪")
    print(f"   数据库: short_term_trades.db")
    print(f"   功能: 短线分析、多股对比、绩效追踪、策略优化")
    print(f"   目标: 1-14天持有，5-20%收益，严格止损")