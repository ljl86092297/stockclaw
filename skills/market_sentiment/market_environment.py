                'operating_strategy': self._determine_operating_strategy(score, risk_level)
            }
            
        except Exception as e:
            return {'error': f'环境评估错误: {str(e)}'}
    
    def _identify_positive_factors(self, trend, sector, sentiment):
        """识别积极因素"""
        positive_factors = []
        
        try:
            # 趋势积极因素
            if trend.get('market_state') == 'bull':
                positive_factors.append('市场处于牛市状态')
            elif trend.get('market_state') == 'recovery':
                positive_factors.append('市场处于反弹状态')
            
            if trend.get('ma_trend') == '上升':
                positive_factors.append('均线呈多头排列')
            
            if trend.get('price_change_20d', 0) > 0:
                positive_factors.append('近期价格呈上涨趋势')
            
            # 板块积极因素
            strong_sectors = sector.get('strong_sectors', [])
            if len(strong_sectors) >= 2:
                sector_names = [s['sector_name'] for s in strong_sectors[:2]]
                positive_factors.append(f'多个板块走强: {", ".join(sector_names)}')
            
            # 情绪积极因素
            if sentiment.get('sentiment_score', 50) > 60:
                positive_factors.append('市场情绪偏乐观')
            
            if sentiment.get('confidence_level') == '高':
                positive_factors.append('情绪指标置信度高')
            
        except Exception as e:
            positive_factors.append(f'识别积极因素时出错: {str(e)}')
        
        return positive_factors if positive_factors else ['暂无显著积极因素']
    
    def _identify_key_risks(self, trend, sector, sentiment):
        """识别关键风险"""
        key_risks = []
        
        try:
            # 趋势风险
            if trend.get('market_state') == 'bear':
                key_risks.append('市场处于熊市状态')
            elif trend.get('market_state') == 'correction':
                key_risks.append('市场处于调整状态')
            
            if trend.get('ma_trend') == '下降':
                key_risks.append('均线呈空头排列')
            
            if trend.get('price_change_20d', 0) < -5:
                key_risks.append('近期跌幅较大')
            
            if trend.get('volatility', 0) > 3:
                key_risks.append('市场波动率较高')
            
            # 板块风险
            weak_sectors = sector.get('weak_sectors', [])
            if len(weak_sectors) >= 2:
                sector_names = [s['sector_name'] for s in weak_sectors[:2]]
                key_risks.append(f'多个板块走弱: {", ".join(sector_names)}')
            
            if sector.get('rotation_strength', 0) < -2:
                key_risks.append('板块轮动呈现弱势')
            
            # 情绪风险
            if sentiment.get('sentiment_score', 50) < 40:
                key_risks.append('市场情绪偏悲观')
            
            if sentiment.get('trend_alignment') == '背离':
                key_risks.append('情绪与趋势出现背离')
            
        except Exception as e:
            key_risks.append(f'识别风险时出错: {str(e)}')
        
        return key_risks if key_risks else ['暂无显著风险']
    
    def _determine_operating_strategy(self, composite_score, risk_level):
        """确定操作策略"""
        if composite_score >= 70:
            if risk_level in ['低', '中低']:
                return {
                    'strategy': '积极进攻',
                    'suggested_position': '70-90%',
                    'focus': '强势板块龙头股',
                    'risk_control': '设好止损，关注趋势变化'
                }
            else:
                return {
                    'strategy': '稳健参与',
                    'suggested_position': '50-70%',
                    'focus': '基本面良好的成长股',
                    'risk_control': '严格控制仓位，分散投资'
                }
        
        elif composite_score >= 60:
            return {
                'strategy': '适度参与',
                'suggested_position': '30-50%',
                'focus': '估值合理的价值股',
                'risk_control': '分批建仓，设好止损'
            }
        
        elif composite_score >= 40:
            return {
                'strategy': '谨慎操作',
                'suggested_position': '10-30%',
                'focus': '防御性板块',
                'risk_control': '小仓位试盘，快进快出'
            }
        
        else:
            return {
                'strategy': '观望为主',
                'suggested_position': '0-10%',
                'focus': '现金或货币基金',
                'risk_control': '保持现金，等待机会'
            }
    
    def _generate_recommendations(self, overall_assessment):
        """生成操作建议"""
        recommendations = []
        
        try:
            env_rating = overall_assessment.get('environment_rating', '中性')
            composite_score = overall_assessment.get('composite_score', 50)
            strategy = overall_assessment.get('operating_strategy', {})
            
            # 基础建议
            recommendations.append(f"市场环境评级: {env_rating}")
            recommendations.append(f"综合评分: {composite_score}/100")
            
            # 策略建议
            if strategy:
                recommendations.append(f"操作策略: {strategy.get('strategy', '未知')}")
                recommendations.append(f"建议仓位: {strategy.get('suggested_position', '未知')}")
                recommendations.append(f"关注方向: {strategy.get('focus', '未知')}")
                recommendations.append(f"风控要点: {strategy.get('risk_control', '未知')}")
            
            # 积极因素
            positive_factors = overall_assessment.get('key_positive_factors', [])
            if positive_factors and positive_factors[0] != '暂无显著积极因素':
                recommendations.append("积极因素:")
                for factor in positive_factors[:3]:  # 只显示前3个
                    recommendations.append(f"  • {factor}")
            
            # 风险提示
            key_risks = overall_assessment.get('key_risks', [])
            if key_risks and key_risks[0] != '暂无显著风险':
                recommendations.append("风险提示:")
                for risk in key_risks[:3]:  # 只显示前3个
                    recommendations.append(f"  ⚠️ {risk}")
            
            # 特别提醒
            if composite_score < 40:
                recommendations.append("特别提醒: 市场环境较差，建议保持谨慎，多看少动")
            elif composite_score > 70:
                recommendations.append("特别提醒: 市场环境良好，可积极把握机会，但勿忘风险控制")
            
        except Exception as e:
            recommendations.append(f"生成建议时出错: {str(e)}")
        
        return recommendations


# 使用示例
if __name__ == "__main__":
    analyzer = MarketEnvironmentAnalyzer()
    
    print("="*60)
    print("市场环境分析示例")
    print("="*60)
    
    # 1. 大盘趋势分析
    print("\n1. 大盘趋势分析:")
    trend_result = analyzer.analyze_market_trend()
    for key, value in trend_result.items():
        print(f"  {key}: {value}")
    
    # 2. 板块轮动分析
    print("\n2. 板块轮动分析:")
    sector_result = analyzer.analyze_sector_rotation()
    print(f"  强势板块: {[s['sector_name'] for s in sector_result.get('strong_sectors', [])[:2]]}")
    print(f"  弱势板块: {[s['sector_name'] for s in sector_result.get('weak_sectors', [])[:2]]}")
    print(f"  市场特征: {sector_result.get('market_character', '未知')}")
    
    # 3. 市场情绪分析
    print("\n3. 市场情绪分析:")
    sentiment_result = analyzer.analyze_market_sentiment()
    print(f"  情绪分数: {sentiment_result.get('sentiment_score', 'N/A')}")
    print(f"  情绪状态: {sentiment_result.get('sentiment_state', '未知')}")
    print(f"  置信程度: {sentiment_result.get('confidence_level', '未知')}")
    
    # 4. 综合分析
    print("\n4. 综合市场环境分析:")
    comprehensive_result = analyzer.comprehensive_market_analysis()
    
    if 'overall_assessment' in comprehensive_result:
        assessment = comprehensive_result['overall_assessment']
        print(f"  综合评分: {assessment.get('composite_score', 'N/A')}")
        print(f"  环境评级: {assessment.get('environment_rating', '未知')}")
        print(f"  环境描述: {assessment.get('environment_description', '未知')}")
    
    # 5. 操作建议
    print("\n5. 操作建议:")
    if 'recommendations' in comprehensive_result:
        for rec in comprehensive_result['recommendations']:
            print(f"  {rec}")
    
    print("="*60)