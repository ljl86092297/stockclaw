#!/usr/bin/env python3
"""
短线交易系统 - 持有1-14天，追求5-20%收益
功能：多股分析、最优选择、绩效追踪、策略优化
"""

import sys
import os
import sqlite3
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

sys.path.append('/home/openclaw/.openclaw/workspace')
from utils.data_source_manager import get_data_source_manager

class ShortTermTrader:
    """短线交易系统"""
    
    def __init__(self):
        self.manager = get_data_source_manager()
        self.db_path = "short_term_trades.db"
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 交易建议表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_code TEXT,
            analysis_date DATE,
            current_price REAL,
            ma5 REAL, ma10 REAL,
            volume_ratio REAL,
            change_5d REAL,
            is_limit_up INTEGER,
            recommendation TEXT,
            buy_price REAL,
            target_price REAL,
            stop_loss REAL,
            holding_days INTEGER,
            position_size REAL,
            expected_return REAL,
            expected_risk REAL,
            risk_reward REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 实际交易表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS actual_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suggestion_id INTEGER,
            stock_code TEXT,
            buy_date DATE,
            buy_price REAL,
            sell_date DATE,
            sell_price REAL,
            position_size REAL,
            profit_loss REAL,
            profit_loss_pct REAL,
            trade_result TEXT,
            profit_reason TEXT,
            loss_reason TEXT,
            lessons TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ 短线交易数据库已创建: {self.db_path}")
    
    def analyze_stock(self, stock_code):
        """分析单只股票"""
        print(f"\n📊 分析 {stock_code}...")
        
        # 获取数据
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = self.manager.get_stock_data(stock_code, start_date, end_date)
        if df is None or df.empty:
            return None
        
        # 计算指标
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        current_price = df['close'].iloc[-1]
        ma5 = df['close'].rolling(5).mean().iloc[-1]
        ma10 = df['close'].rolling(10).mean().iloc[-1]
        
        # 成交量
        avg_volume = df['volume'].mean()
        latest_volume = df['volume'].iloc[-1]
        volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 0
        
        # 5日涨幅
        if len(df) >= 5:
            change_5d = (current_price - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100
        else:
            change_5d = 0
        
        # 是否涨停
        is_limit_up = 0
        if 'high' in df.columns and 'low' in df.columns:
            today_range = (df['high'].iloc[-1] - df['low'].iloc[-1]) / df['low'].iloc[-1]
            if today_range > 0.095:
                is_limit_up = 1
        
        # 短线评分
        score = 0
        if current_price > ma5: score += 1
        if current_price > ma10: score += 1
        if change_5d > 5: score += 1
        if volume_ratio > 1.5: score += 2
        elif volume_ratio > 1.0: score += 1
        if is_limit_up == 1: score += 2
        
        # 空间计算
        resistance = df['high'].max() * 0.98
        space = (resistance - current_price) / current_price * 100
        if space > 10: score += 2
        elif space > 5: score += 1
        
        # 生成建议
        if score >= 8:
            rec = "强烈买入"
            buy_price = current_price * 0.995
            target_return = 15
            stop_loss = 5
            holding_days = 3
            position = 0.25
        elif score >= 6:
            rec = "买入"
            buy_price = current_price * 0.99
            target_return = 10
            stop_loss = 6
            holding_days = 5
            position = 0.15
        elif score >= 4:
            rec = "持有"
            buy_price = ma10 * 0.98
            target_return = 8
            stop_loss = 7
            holding_days = 7
            position = 0.10
        else:
            rec = "卖出"
            buy_price = target_return = stop_loss = holding_days = position = 0
        
        # 计算价格
        target_price = current_price * (1 + target_return / 100)
        stop_loss_price = current_price * (1 - stop_loss / 100)
        risk_reward = target_return / stop_loss if stop_loss > 0 else 0
        
        # 保存到数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO trade_suggestions (
            stock_code, analysis_date, current_price, ma5, ma10,
            volume_ratio, change_5d, is_limit_up, recommendation,
            buy_price, target_price, stop_loss, holding_days, position_size,
            expected_return, expected_risk, risk_reward
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stock_code,
            datetime.now().strftime('%Y-%m-%d'),
            current_price, ma5, ma10, volume_ratio, change_5d, is_limit_up, rec,
            buy_price, target_price, stop_loss_price, holding_days, position,
            target_return, stop_loss, risk_reward
        ))
        
        suggestion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        result = {
            "stock_code": stock_code,
            "current_price": current_price,
            "ma5": ma5,
            "ma10": ma10,
            "volume_ratio": volume_ratio,
            "change_5d": change_5d,
            "is_limit_up": is_limit_up,
            "score": score,
            "recommendation": rec,
            "buy_price": buy_price,
            "target_price": target_price,
            "stop_loss": stop_loss_price,
            "holding_days": holding_days,
            "position": position,
            "expected_return": target_return,
            "expected_risk": stop_loss,
            "risk_reward": risk_reward,
            "suggestion_id": suggestion_id
        }
        
        return result
    
    def analyze_multiple(self, stock_list):
        """分析多只股票"""
        print(f"\n🔍 分析 {len(stock_list)} 只股票...")
        
        results = []
        for code in stock_list:
            result = self.analyze_stock(code)
            if result:
                results.append(result)
        
        # 按预期收益排序
        results.sort(key=lambda x: x.get("expected_return", 0), reverse=True)
        
        return results
    
    def find_best_stock(self, stock_list):
        """找出最优股票"""
        results = self.analyze_multiple(stock_list)
        
        if not results:
            return None
        
        best = results[0]
        
        print(f"\n🏆 最优股票: {best['stock_code']}")
        print(f"   评分: {best['score']}/12")
        print(f"   建议: {best['recommendation']}")
        print(f"   预期收益: {best['expected_return']}%")
        print(f"   风险收益比: {best['risk_reward']:.2f}")
        print(f"   持有天数: {best['holding_days']} 天")
        
        return best
    
    def record_trade(self, suggestion_id, buy_price, sell_price, position):
        """记录实际交易"""
        try:
            # 获取建议信息
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM trade_suggestions WHERE id = ?', (suggestion_id,))
            suggestion = cursor.fetchone()
            
            if not suggestion:
                print("❌ 未找到建议记录")
                return
            
            stock_code = suggestion[1]
            expected_return = suggestion[15]
            
            # 计算盈亏
            profit_loss = (sell_price - buy_price) * position
            profit_loss_pct = (sell_price - buy_price) / buy_price * 100
            
            # 判断结果
            if profit_loss_pct > 1:
                result = "盈利"
                profit_reason = self._analyze_profit(suggestion, profit_loss_pct)
                loss_reason = ""
            elif profit_loss_pct < -1:
                result = "亏损"
                profit_reason = ""
                loss_reason = self._analyze_loss(suggestion, profit_loss_pct)
            else:
                result = "持平"
                profit_reason = loss_reason = ""
            
            # 经验教训
            lessons = ""
            if profit_loss_pct > expected_return:
                lessons = "实际表现超过预期，可适当提高目标"
            elif profit_loss_pct < expected_return:
                lessons = "实际表现不及预期，需调整买入条件"
            
            # 记录交易
            cursor.execute('''
            INSERT INTO actual_trades (
                suggestion_id, stock_code, buy_date, buy_price,
                sell_date, sell_price, position_size, profit_loss,
                profit_loss_pct, trade_result, profit_reason, loss_reason, lessons
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                suggestion_id,
                stock_code,
                datetime.now().strftime('%Y-%m-%d'),
                buy_price,
                datetime.now().strftime('%Y-%m-%d'),
                sell_price,
                position,
                profit_loss,
                profit_loss_pct,
                result,
                profit_reason,
                loss_reason,
                lessons
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ 交易记录已保存")
            print(f"   盈亏: {profit_loss_pct:.2f}% ({profit_loss:.2f}元)")
            print(f"   结果: {result}")
            
        except Exception as e:
            print(f"❌ 记录失败: {e}")
    
    def _analyze_profit(self, suggestion, actual_return):
        """分析盈利原因"""
        reasons = []
        
        volume_ratio = suggestion[6]
        if volume_ratio > 1.5:
            reasons.append("成交量配合")
        
        change_5d = suggestion[7]
        if change_5d > 5:
            reasons.append("趋势强劲")
        
        return "、".join(reasons) if reasons else "技术面良好"
    
    def _analyze_loss(self, suggestion, actual_return):
        """分析亏损原因"""
        reasons = []
        
        volume_ratio = suggestion[6]
        if volume_ratio < 0.8:
            reasons.append("量能不足")
        
        change_5d = suggestion[7]
        if change_5d < 0:
            reasons.append("趋势转弱")
        
        return "、".join(reasons) if reasons else "市场变化"
    
    def get_performance_summary(self, days=7):
        """获取绩效总结"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN trade_result = '盈利' THEN 1 ELSE 0 END) as wins,
                SUM(profit_loss) as total_profit,
                AVG(profit_loss_pct) as avg_return
            FROM actual_trades
            WHERE sell_date >= ?
            ''', (start_date,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] > 0:
                total = result[0]
                wins = result[1]
                total_profit = result[2] or 0
                avg_return = result[3] or 0
                win_rate = wins / total * 100
                
                return {
                    "总交易次数": total,
                    "盈利次数": wins,
                    "胜率": f"{win_rate:.1f}%",
                    "总盈亏": f"{total_profit:.2f}元",
                    "平均收益": f"{avg_return:.2f}%"
                }
            
        except Exception as e:
            print(f"❌ 获取绩效失败: {e}")
        
        return {}
    
    def optimize_strategy(self):
        """策略优化"""
        print("\n🔄 策略优化分析...")
        
        summary = self.get_performance_summary(30)
        
        if summary:
            print(f"📊 近期表现:")
            for key, value in summary.items():
                print(f"   {key}: {value}")
            
            # 优化建议
            win_rate = float(summary.get("胜率", "0%").replace("%", ""))
            avg_return = float(summary.get("平均收益", "0%").replace("%", ""))
            
            suggestions = []
            
            if win_rate < 60:
                suggestions.append("提高买入标准，减少交易频率")
            
            if avg_return < 5:
                suggestions.append("调整止盈目标，优化风险收益比")
            
            if suggestions:
                print(f"\n💡 优化建议:")
                for suggestion in suggestions:
                    print(f"   • {suggestion}")
        
        print("✅ 策略优化完成")
    
    def print_report(self, stock_code):
        """打印分析报告"""
        result = self.analyze_stock(stock_code)
        
        if not result:
            print(f"❌ 分析失败")
            return
        
        print(f"\n{'='*80}")
        print(f"🎯 {stock_code} 短线交易分析")
        print(f"{'='*80}")
        
        print(f"\n📊 数据指标:")
        print(f"   当前价: ¥{result['current_price']:.2f}")
        print(f"   MA5: ¥{result['ma5']:.2f}")
        print(f"   MA10: ¥{result['ma10']:.2f}")
        print(f"   量比: {result['volume_ratio']:.2f}")
        print(f"   5日涨幅: {result['change_5d']:.1f}%")
        print(f"   是否涨停: {'是' if result['is_limit_up'] == 1 else '否'}")
        print(f"   评分: {result['score']}/12")
        
        print(f"\n📝 交易建议:")
        print(f"   评级: {result['recommendation']}")
        
        if result['recommendation'] in ["强烈买入", "买入"]:
            print(f"   建议买入价: ¥{result['buy_price']:.2f}")
            print(f"   目标价: ¥{result['target_price']:.2f} (+{result['expected_return']}%)")
            print(f"   止损价: ¥{result['stop_loss']:.2f} (-{result['expected_risk']}%)")
            print(f"   持有天数: {result['holding_days']} 天")
            print(f"   建议仓位: {result['position']*100:.0f}%")
            print(f"   风险收益比: {result['risk_reward']:.2f}")
            
            print(f"\n⚡ 操作要点:")
            print(f"   • 价格在{result['buy_price']:.2f}以下考虑买入")
            if result['volume_ratio'] > 1.5:
                print(f"   • 成交量持续放大是积极信号")
            if result['change_5d'] > 5:
                print(f"   • 短期趋势强劲，可适当追涨")
        
        print(f"\n🚨 风险提示:")
        print(f"   • 跌破{result['stop_loss']:.2f}立即止损")
        print(f"   • 持有不超过{result['holding_days']}天")
        print(f"   • 单股仓位不超过{result['position']*100:.0f}%")
        
        print(f"\n{'='*80}")
        print("💡 短线核心: 快进快出，严格止损，追求5-15%收益")
        print(f"{'='*80}\n")


# 测试函数
def test_system():
    trader = ShortTermTrader()
    
    print("🚀 测试短线交易系统")
    print("="*50)
    
    # 测试股票列表
    test_stocks = ["600096", "000001", "000002", "600036"]
    
    print("\n1. 📊 分析单只股票（云天化）")
    print("-"*40)
    result = trader.analyze_stock("600096")
    if result:
        print(f"   股票: {result['stock_code']}")
        print(f"   当前价: ¥{result['current_price']:.2f}")