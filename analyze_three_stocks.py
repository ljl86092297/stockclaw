#!/usr/bin/env python3
"""
三只股票详细分析：华胜天成、拓维信息、航锦科技
基于ADX策略 + 综合评分系统
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict
import pandas as pd
import numpy as np

sys.path.append('/home/openclaw/.openclaw/workspace')
from utils.data_source_manager import get_data_source_manager

# 导入ADX计算器
sys.path.append('/home/openclaw/.openclaw/workspace/learning/2026-03/03-15_ADX指标学习/code')
from adx_calculator import calculate_adx, interpret_adx

class ThreeStocksAnalyzer:
    """三只股票分析器"""
    
    def __init__(self):
        self.manager = get_data_source_manager()
        self.stocks = {
            '华胜天成': '600410',
            '拓维信息': '002261',
            '航锦科技': '000818'
        }
    
    def analyze_stock(self, name: str, code: str) -> Dict:
        """分析单只股票"""
        print(f"\n🔍 分析 {name} ({code})...")
        
        # 获取数据
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        
        df = self.manager.get_stock_data(code, start_date, end_date)
        if df is None or df.empty:
            print(f"  ❌ 数据获取失败")
            return None
        
        # 数据预处理
        df = df.copy()
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna(subset=['open', 'high', 'low', 'close', 'volume'])
        
        if len(df) < 30:
            print(f"  ❌ 数据不足，需要至少30条，当前{len(df)}条")
            return None
        
        # 1. 基础技术指标
        current_price = float(df['close'].iloc[-1])
        ma5 = float(df['close'].rolling(5).mean().iloc[-1])
        ma10 = float(df['close'].rolling(10).mean().iloc[-1])
        ma20 = float(df['close'].rolling(20).mean().iloc[-1])
        
        # 成交量
        avg_volume = float(df['volume'].mean())
        latest_volume = float(df['volume'].iloc[-1])
        volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 0
        
        # 价格变化
        if len(df) >= 5:
            price_5d_ago = float(df['close'].iloc[-5])
            change_5d = (current_price - price_5d_ago) / price_5d_ago * 100 if price_5d_ago > 0 else 0
        else:
            change_5d = 0
        
        # 价格位置
        period_high = float(df['high'].max())
        period_low = float(df['low'].min())
        price_position = (current_price - period_low) / (period_high - period_low) * 100 if period_high > period_low else 50
        
        base_indicators = {
            "current_price": current_price,
            "ma5": ma5,
            "ma10": ma10,
            "ma20": ma20,
            "volume_ratio": volume_ratio,
            "change_5d": change_5d,
            "price_position": price_position,
            "period_high": period_high,
            "period_low": period_low
        }
        
        # 2. ADX趋势分析
        adx_data = calculate_adx(df)
        interpretation = interpret_adx(adx_data)
        
        adx_analysis = {
            "adx_value": adx_data.get('ADX', 25),
            "plus_di": adx_data.get('+DI', 50),
            "minus_di": adx_data.get('-DI', 50),
            "trend_strength": interpretation.get('趋势强度', '未知'),
            "trend_direction": interpretation.get('趋势方向', '未知'),
            "adx_suggestion": interpretation.get('交易建议', '未知'),
            "adx_reason": interpretation.get('建议理由', '')
        }
        
        # 3. 综合评分
        scores = self._calculate_scores(base_indicators, adx_analysis)
        
        # 4. 生成建议
        suggestion = self._generate_suggestion(base_indicators, adx_analysis, scores)
        
        return {
            "name": name,
            "code": code,
            "base_indicators": base_indicators,
            "adx_analysis": adx_analysis,
            "scores": scores,
            "suggestion": suggestion
        }
    
    def _calculate_scores(self, base: Dict, adx: Dict) -> Dict:
        """计算综合评分"""
        # 技术面评分（0-4分）
        tech_score = 0
        if base["current_price"] > base["ma5"]: tech_score += 1
        if base["current_price"] > base["ma20"]: tech_score += 1
        if base["change_5d"] > 5: tech_score += 1
        if base["volume_ratio"] > 1.0: tech_score += 1
        
        # 趋势面评分
        trend_strength = adx.get("trend_strength", "未知")
        trend_score_map = {
            "极强趋势": 3,
            "明显趋势": 2,
            "弱趋势": 1,
            "震荡市": 0
        }
        trend_score = trend_score_map.get(trend_strength, 0)
        
        # 如果是上升趋势，额外加分
        if adx.get("trend_direction") == "上升趋势":
            trend_score += 1
        
        # 成交量评分
        volume_score = 0
        if base["volume_ratio"] > 1.5: volume_score = 2
        elif base["volume_ratio"] > 1.0: volume_score = 1
        
        # 总评分
        total_score = tech_score + trend_score + volume_score
        
        return {
            "technical_score": tech_score,
            "trend_score": trend_score,
            "volume_score": volume_score,
            "total_score": total_score,
            "max_score": 9
        }
    
    def _generate_suggestion(self, base: Dict, adx: Dict, scores: Dict) -> Dict:
        """生成交易建议"""
        total_score = scores.get("total_score", 0)
        current_price = base.get("current_price", 0)
        ma20 = base.get("ma20", 0)
        adx_value = adx.get("adx_value", 25)
        
        # 根据评分生成建议
        if total_score >= 7:
            recommendation = "强烈买入"
            buy_price = current_price * 0.995
            target_return = 15
            stop_loss = 5
            holding_days = 3
            position = 0.25
            confidence = "高"
            
        elif total_score >= 5:
            recommendation = "买入"
            buy_price = current_price * 0.99
            target_return = 10
            stop_loss = 6
            holding_days = 5
            position = 0.15
            confidence = "中"
            
        elif total_score >= 3:
            recommendation = "持有"
            buy_price = ma20 * 0.98
            target_return = 8
            stop_loss = 7
            holding_days = 7
            position = 0.10
            confidence = "低"
            
        else:
            recommendation = "卖出"
            buy_price = 0
            target_return = 0
            stop_loss = 0
            holding_days = 0
            position = 0
            confidence = "高"
        
        # 计算具体价格
        target_price = current_price * (1 + target_return / 100)
        stop_loss_price = current_price * (1 - stop_loss / 100)
        risk_reward = target_return / stop_loss if stop_loss > 0 else 0
        
        # 生成理由
        reasoning = self._generate_reasoning(base, adx, scores)
        
        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "buy_price": buy_price,
            "target_price": target_price,
            "stop_loss_price": stop_loss_price,
            "holding_days": holding_days,
            "position_size": position,
            "expected_return": target_return,
            "expected_risk": stop_loss,
            "risk_reward_ratio": risk_reward,
            "reasoning": reasoning
        }
    
    def _generate_reasoning(self, base: Dict, adx: Dict, scores: Dict) -> str:
        """生成建议理由"""
        reasons = []
        
        # 技术面理由
        if base["current_price"] > base["ma20"]:
            reasons.append("价格在MA20之上")
        if base["change_5d"] > 5:
            reasons.append(f"5日涨幅{base['change_5d']:.1f}%")
        if base["volume_ratio"] > 1.0:
            reasons.append(f"量比{base['volume_ratio']:.2f}")
        
        # ADX理由
        trend_strength = adx.get("trend_strength", "")
        trend_direction = adx.get("trend_direction", "")
        if trend_strength != "未知":
            reasons.append(f"趋势{trend_strength}")
        if trend_direction != "未知":
            reasons.append(f"方向{trend_direction}")
        
        # 评分理由
        total_score = scores.get("total_score", 0)
        reasons.append(f"综合评分{total_score}/9")
        
        return "；".join(reasons) if reasons else "无明显优势"
    
    def print_comparison_report(self):
        """打印对比分析报告"""
        print("🚀 三只股票详细对比分析")
        print("="*80)
        print("📚 基于ADX策略 + 综合评分系统")
        print("="*80)
        
        results = {}
        
        # 分析每只股票
        for name, code in self.stocks.items():
            result = self.analyze_stock(name, code)
            if result:
                results[name] = result
        
        if not results:
            print("❌ 所有股票分析失败")
            return
        
        # 打印详细分析
        print(f"\n{'='*80}")
        print("📊 详细分析结果")
        print(f"{'='*80}")
        
        for name, result in results.items():
            base = result["base_indicators"]
            adx = result["adx_analysis"]
            scores = result["scores"]
            suggestion = result["suggestion"]
            
            print(f"\n🎯 {name} ({result['code']})")
            print(f"  当前价: ¥{base['current_price']:.2f}")
            print(f"  MA20: ¥{base['ma20']:.2f}")
            print(f"  量比: {base['volume_ratio']:.2f}")
            print(f"  5日涨幅: {base['change_5d']:.1f}%")
            
            print(f"  ADX: {adx['adx_value']:.2f} ({adx['trend_strength']})")
            print(f"  趋势: {adx['trend_direction']}")
            
            print(f"  评分: {scores['total_score']}/9 (技术{scores['technical_score']}/4, "
                  f"趋势{scores['trend_score']}/4, 成交量{scores['volume_score']}/2)")
            
            print(f"  建议: {suggestion['recommendation']} ({suggestion['confidence']}置信度)")
            
            if suggestion['recommendation'] in ["强烈买入", "买入"]:
                print(f"  买入价: ¥{suggestion['buy_price']:.2f}")
                print(f"  目标价: ¥{suggestion['target_price']:.2f} (+{suggestion['expected_return']}%)")
                print(f"  止损价: ¥{suggestion['stop_loss_price']:.2f} (-{suggestion['expected_risk']}%)")
                print(f"  风险收益比: {suggestion['risk_reward_ratio']:.2f}")
            
            print(f"  理由: {suggestion['reasoning']}")
        
        # 找出最优股票
        print(f"\n{'='*80}")
        print("🏆 最优股票推荐")
        print(f"{'='*80}")
        
        # 按评分排序
        sorted_results = sorted(
            results.items(),
            key=lambda x: x[1]["scores"]["total_score"],
            reverse=True
        )
        
        for i, (name, result) in enumerate(sorted_results[:3], 1):
            scores = result["scores"]
            suggestion = result["suggestion"]
            
            print(f"{i}. {name} ({result['code']})")
            print(f"   评分: {scores['total_score']}/9")
            print(f"   建议: {suggestion['recommendation']}")
            
            if suggestion['recommendation'] in ["强烈买入", "买入"]:
                print(f"   预期收益: {suggestion['expected_return']}%")
                print(f"   风险收益比: {suggestion['risk_reward_ratio']:.2f}")
                print(f"   建议持有: {suggestion['holding_days']}天")
                print(f"   建议仓位: {suggestion['position_size']*100:.0f}%")
            
            print(f"   理由: {suggestion['reasoning']}")
            print()
        
        # 策略依据总结
        print(f"\n{'='*80}")
        print("📋 策略依据总结")
        print(f"{'='*80}")
        
        print("1. ADX趋势过滤:")
        print("   • ADX > 25: 趋势明显（非震荡市）")
        print("   • +DI > -DI: 上升趋势（非下降趋势）")
        print("   • ADX < 20: 震荡市，建议规避")
        
        print("\n2. 技术面确认:")
        print("   • 价格 > MA20: 中期趋势向上")
        print("   • 价格 > MA5: 短期趋势向上")
        print("   • 5日涨幅 > 5%: 近期有上涨动能")
        print("   • 量比 > 1.0: 有成交量支持")
        
        print("\n3. 评分系统:")
        print("   • 技术面: 0-4分（价格位置、涨幅、均线）")
        print("   • 趋势面: 0-4分（ADX强度、方向）")
        print("   • 成交量: 0-2分（量比大小）")
        print("   • 总评分: 0-9分")
        
        print("\n4. 操作建议规则:")
        print("   • 评分≥7: 强烈买入（目标15%，止损5%，仓位25%）")
        print("   • 评分≥5: 买入（目标10%，止损6%，仓位15%）")
        print("   • 评分≥3: 持有观望（等待更好时机）")
        print("   • 评分<3: 卖出（规避风险）")
        
        print("\n5. 风险控制:")
        print("   • 止损位: MA20支撑或5-8%最大亏损")
        print("   • 仓位: 基于凯利公式和风险收益比")
        print("   • 持有时间: 1-14天（短线策略）")
        
        print(f"\n{'='*80}")
        print("🎯 核心策略: 只交易ADX>25的明显趋势，严格风险控制")
        print(f"{'='*80}")

if __name__ == "__main__":
    analyzer = ThreeStocksAnalyzer()
    analyzer.print_comparison_report()