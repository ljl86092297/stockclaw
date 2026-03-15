        if not advice:
            advice.append('建议结合基本面和其他因素综合判断')
        
        report['investment_advice']['suggestions'] = advice
        
        # 短期走势预测（1周）
        recent_trend = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100 if len(df) >= 5 else 0
        if recent_trend > 3:
            short_term = '继续上涨'
            short_target = df['close'].iloc[-1] * 1.03
        elif recent_trend < -3:
            short_term = '继续调整'
            short_target = df['close'].iloc[-1] * 0.97
        else:
            short_term = '震荡整理'
            short_target = df['close'].iloc[-1]
        
        report['investment_advice']['short_term_forecast'] = {
            'period': '1周',
            'direction': short_term,
            'target_price': round(short_target, 2),
            'probability': '中等'
        }
        
        # 关键价位
        support = df['low'].tail(20).min()
        resistance = df['high'].tail(20).max()
        
        report['investment_advice']['key_levels'] = {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'current_position': '支撑上方' if df['close'].iloc[-1] > support else '支撑下方'
        }
        
        return report
    
    def save_report(self, report, filename=None):
        """保存报告"""
        if filename is None:
            filename = f"福斯特_分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join('/home/openclaw/.openclaw/workspace', filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
            return None
    
    def print_report_summary(self, report):
        """打印报告摘要"""
        print("\n" + "="*60)
        print("📊 福斯特（603806）专业分析报告")
        print("="*60)
        
        # 股票信息
        info = report['stock_info']
        print(f"\n📋 股票信息:")
        print(f"   代码: {info['code']} - {info['name']}")
        print(f"   交易所: {info['exchange']}")
        print(f"   分析时间: {info['analysis_time']}")
        print(f"   数据期间: {info['data_period']}")
        print(f"   数据点数: {info['data_points']}")
        
        # 当前状态
        status = report['current_status']['price_analysis']
        print(f"\n💰 当前状态:")
        print(f"   当前价格: {status['current_price']}")
        print(f"   涨跌幅: {status['price_change']}% ({status['direction']})")
        print(f"   成交量: {status['volume']:,}")
        print(f"   换手率: {status['turnover_rate']}%")
        
        # 技术分析
        if report['technical_summary']['points']:
            print(f"\n📈 技术分析:")
            for point in report['technical_summary']['points']:
                print(f"   • {point}")
        
        # 投资建议
        advice = report['investment_advice']
        print(f"\n💡 投资建议:")
        for suggestion in advice['suggestions']:
            print(f"   • {suggestion}")
        
        # 短期预测
        if 'short_term_forecast' in advice:
            forecast = advice['short_term_forecast']
            print(f"\n📅 短期预测({forecast['period']}):")
            print(f"   方向: {forecast['direction']}")
            print(f"   目标价位: {forecast['target_price']}")
            print(f"   概率: {forecast['probability']}")
        
        # 关键价位
        if 'key_levels' in advice:
            levels = advice['key_levels']
            print(f"\n🎯 关键价位:")
            print(f"   支撑位: {levels['support']}")
            print(f"   阻力位: {levels['resistance']}")
            print(f"   当前位置: {levels['current_position']}")
        
        # 风险提示
        print(f"\n⚠️ 风险提示:")
        for warning in report['risk_warnings'][:3]:
            print(f"   • {warning}")
        
        print("\n" + "="*60)
        print("✅ 分析完成！建议结合自身情况谨慎决策。")
        print("="*60)

def main():
    """主函数"""
    print("\n🚀 开始福斯特（603806）专业分析...")
    
    # 创建分析器
    analyzer = FosterAnalyzer()
    
    if not analyzer.connected:
        print("❌ 无法连接Baostock，退出分析")
        return
    
    try:
        # 1. 获取K线数据
        print("\n📥 获取福斯特K线数据...")
        df = analyzer.get_kline_data()
        
        if df.empty:
            print("❌ 无法获取数据，退出分析")
            analyzer.logout()
            return
        
        # 2. 计算技术指标
        df = analyzer.calculate_technical_indicators(df)
        
        # 3. 分析当前状态
        print("\n🔍 分析当前状态...")
        analysis = analyzer.analyze_current_status(df)
        
        # 4. 生成综合报告
        print("\n📋 生成综合报告...")
        report = analyzer.generate_comprehensive_report(df, analysis)
        
        # 5. 保存报告
        saved_file = analyzer.save_report(report)
        if saved_file:
            print(f"✅ 报告已保存: {saved_file}")
        
        # 6. 打印报告摘要
        analyzer.print_report_summary(report)
        
        # 7. 显示最新指标值
        print("\n📊 最新技术指标值:")
        latest = df.iloc[-1]
        
        indicators = [
            ('RSI', latest.get('RSI'), '超买>70,超卖<30'),
            ('MACD', latest.get('MACD'), '金叉买入,死叉卖出'),
            ('ATR', latest.get('ATR'), '波动率指标'),
            ('ADX', latest.get('ADX'), '趋势强度>25强趋势'),
            ('CCI', latest.get('CCI'), '超买>100,超卖<-100')
        ]
        
        for name, value, desc in indicators:
            if pd.notna(value):
                print(f"   {name}: {round(value, 2)} - {desc}")
        
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 退出Baostock
        analyzer.logout()
    
    print("\n🎯 分析流程完成！")

if __name__ == "__main__":
    main()