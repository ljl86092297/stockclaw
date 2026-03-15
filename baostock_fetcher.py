            # 显示最新指标
            latest = daily_df.iloc[-1]
            print(f"   RSI(14): {latest['RSI']:.1f}" if pd.notna(latest.get('RSI')) else "   RSI: 无数据")
            print(f"   MACD: {latest['MACD']:.3f}" if pd.notna(latest.get('MACD')) else "   MACD: 无数据")
            print(f"   ATR: {latest['ATR']:.3f}" if pd.notna(latest.get('ATR')) else "   ATR: 无数据")
            print(f"   ADX: {latest['ADX']:.1f}" if pd.notna(latest.get('ADX')) else "   ADX: 无数据")
            print(f"   CCI: {latest['CCI']:.1f}" if pd.notna(latest.get('CCI')) else "   CCI: 无数据")
            
            # 4. 生成分析报告
            print("\n📋 生成分析报告...")
            report = fetcher.generate_analysis_report("603806", daily_df)
            
            # 5. 显示报告摘要
            print("\n" + "="*60)
            print("📊 福斯特（603806）分析报告摘要")
            print("="*60)
            
            print(f"\n📅 数据期间: {report['数据期间']}")
            print(f"💰 当前价格: {report['当前价格']}")
            print(f"📈 数据点数: {report['数据点数']}")
            
            if '技术分析' in report:
                print("\n🔍 技术指标:")
                for indicator, data in report['技术分析'].items():
                    print(f"   {indicator}: {data.get('数值', 'N/A')} ({data.get('状态', 'N/A')})")
            
            if '趋势判断' in report:
                print("\n📈 趋势判断:")
                for key, data in report['趋势判断'].items():
                    if isinstance(data, dict):
                        print(f"   {key}: {data.get('强度', data.get('排列', 'N/A'))}")
            
            if '风险指标' in report:
                print("\n⚠️ 风险指标:")
                for key, data in report['风险指标'].items():
                    print(f"   {key}: {data.get('数值', 'N/A')}")
            
            if '投资建议' in report and '操作建议' in report['投资建议']:
                print("\n💡 操作建议:")
                for i, suggestion in enumerate(report['投资建议']['操作建议'], 1):
                    print(f"   {i}. {suggestion}")
            
            # 6. 保存报告
            print("\n💾 保存报告...")
            saved_file = fetcher.save_report(report)
            if saved_file:
                print(f"   报告已保存: {saved_file}")
            
            # 7. 显示完整报告路径
            print("\n" + "="*60)
            print("🎯 分析完成！")
            print("="*60)
            print(f"\n完整报告已生成，包含：")
            print("1. 技术指标分析（RSI, MACD, ATR, ADX, CCI）")
            print("2. 趋势判断")
            print("3. 风险指标")
            print("4. 投资建议")
            print("5. 风险提示")
            
        else:
            print("❌ 无法获取福斯特日线数据")
            
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 退出Baostock
        fetcher.logout()
    
    print("\n✅ 分析流程完成")

if __name__ == "__main__":
    # 检查是否安装了baostock
    try:
        import baostock
        print("✅ Baostock库已安装")
        main()
    except ImportError:
        print("❌ 未安装Baostock库")
        print("请执行: pip install baostock")
        sys.exit(1)