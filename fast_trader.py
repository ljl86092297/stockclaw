#!/usr/bin/env python3
"""
快速短线交易系统
持有1-14天，目标5-20%收益
支持：多股分析、最优选择、绩效追踪、策略优化
"""

import sys
import os
import sqlite3
import json
from datetime import datetime, timedelta
import pandas as pd

sys.path.append('/home/openclaw/.openclaw/workspace')
from utils.data_source_manager import get_data_source_manager

class FastTrader:
    def __init__(self):
        self.manager = get_data_source_manager()
        self.db = "fast_trades.db"
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        
        # 建议表
        c.execute('''
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY,
            code TEXT,
            date TEXT,
            price REAL,
            ma5 REAL,
            volume_ratio REAL,
            change_5d REAL,
            rec TEXT,
            buy_price REAL,
            target REAL,
            stop REAL,
            days INTEGER,
            position REAL,
            exp_return REAL,
            risk_reward REAL
        )
        ''')
        
        # 交易表
        c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY,
            sug_id INTEGER,
            code TEXT,
            buy_date TEXT,
            buy_price REAL,
            sell_date TEXT,
            sell_price REAL,
            profit REAL,
            profit_pct REAL,
            result TEXT,
            reason TEXT,
            lesson TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ 数据库: {self.db}")
    
    def analyze(self, code):
        """分析股票"""
        print(f"分析 {code}...")
        
        # 获取数据
        end = datetime.now().strftime('%Y-%m-%d')
        start = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        df = self.manager.get_stock_data(code, start, end)
        if df is None or df.empty:
            return None
        
        # 计算指标
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        price = df['close'].iloc[-1]
        ma5 = df['close'].rolling(5).mean().iloc[-1]
        
        # 成交量
        avg_vol = df['volume'].mean()
        latest_vol = df['volume'].iloc[-1]
        vol_ratio = latest_vol / avg_vol if avg_vol > 0 else 0
        
        # 5日涨幅
        if len(df) >= 5:
            change_5d = (price - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100
        else:
            change_5d = 0
        
        # 评分
        score = 0
        if price > ma5: score += 1
        if change_5d > 5: score += 1
        if vol_ratio > 1.5: score += 2
        elif vol_ratio > 1.0: score += 1
        
        # 空间
        resistance = df['high'].max() * 0.98
        space = (resistance - price) / price * 100
        if space > 10: score += 2
        elif space > 5: score += 1
        
        # 建议
        if score >= 8:
            rec = "强烈买入"
            buy = price * 0.995
            target_pct = 15
            stop_pct = 5
            days = 3
            pos = 0.25
        elif score >= 6:
            rec = "买入"
            buy = price * 0.99
            target_pct = 10
            stop_pct = 6
            days = 5
            pos = 0.15
        elif score >= 4:
            rec = "持有"
            buy = ma5 * 0.98
            target_pct = 8
            stop_pct = 7
            days = 7
            pos = 0.10
        else:
            rec = "卖出"
            buy = target_pct = stop_pct = days = pos = 0
        
        # 计算价格
        target = price * (1 + target_pct / 100)
        stop = price * (1 - stop_pct / 100)
        rr = target_pct / stop_pct if stop_pct > 0 else 0
        
        # 保存
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        
        c.execute('''
        INSERT INTO suggestions (code, date, price, ma5, volume_ratio, change_5d, 
                               rec, buy_price, target, stop, days, position, exp_return, risk_reward)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (code, datetime.now().strftime('%Y-%m-%d'), price, ma5, vol_ratio, change_5d,
              rec, buy, target, stop, days, pos, target_pct, rr))
        
        sug_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "code": code,
            "price": price,
            "ma5": ma5,
            "vol_ratio": vol_ratio,
            "change_5d": change_5d,
            "score": score,
            "rec": rec,
            "buy": buy,
            "target": target,
            "stop": stop,
            "days": days,
            "pos": pos,
            "exp_return": target_pct,
            "risk_reward": rr,
            "sug_id": sug_id
        }
    
    def analyze_multi(self, codes):
        """分析多股"""
        results = []
        for code in codes:
            res = self.analyze(code)
            if res:
                results.append(res)
        
        # 按预期收益排序
        results.sort(key=lambda x: x.get("exp_return", 0), reverse=True)
        return results
    
    def find_best(self, codes):
        """找最优"""
        results = self.analyze_multi(codes)
        if not results:
            return None
        
        best = results[0]
        
        print(f"\n🏆 最优: {best['code']}")
        print(f"   建议: {best['rec']}")
        print(f"   评分: {best['score']}/10")
        print(f"   预期收益: {best['exp_return']}%")
        print(f"   风险收益比: {best['risk_reward']:.2f}")
        print(f"   持有: {best['days']}天")
        
        return best
    
    def record_trade(self, sug_id, buy_price, sell_price, position):
        """记录交易"""
        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            
            # 获取建议
            c.execute('SELECT * FROM suggestions WHERE id = ?', (sug_id,))
            sug = c.fetchone()
            
            if not sug:
                print("❌ 无建议记录")
                return
            
            code = sug[1]
            
            # 计算盈亏
            profit = (sell_price - buy_price) * position
            profit_pct = (sell_price - buy_price) / buy_price * 100
            
            # 结果
            if profit_pct > 1:
                result = "盈利"
                reason = "技术面良好"
            elif profit_pct < -1:
                result = "亏损"
                reason = "市场变化"
            else:
                result = "持平"
                reason = "波动小"
            
            # 教训
            exp_return = sug[13]
            if profit_pct > exp_return:
                lesson = "表现超预期"
            elif profit_pct < exp_return:
                lesson = "表现不及预期"
            else:
                lesson = "符合预期"
            
            # 记录
            c.execute('''
            INSERT INTO trades (sug_id, code, buy_date, buy_price, sell_date, sell_price,
                              profit, profit_pct, result, reason, lesson)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (sug_id, code, datetime.now().strftime('%Y-%m-%d'), buy_price,
                  datetime.now().strftime('%Y-%m-%d'), sell_price,
                  profit, profit_pct, result, reason, lesson))
            
            conn.commit()
            conn.close()
            
            print(f"✅ 交易记录: {profit_pct:.2f}% ({profit:.2f}元)")
            
        except Exception as e:
            print(f"❌ 记录失败: {e}")
    
    def get_summary(self, days=7):
        """获取总结"""
        try:
            conn = sqlite3.connect(self.db)
            c = conn.cursor()
            
            start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            c.execute('''
            SELECT 
                COUNT(*),
                SUM(CASE WHEN result = '盈利' THEN 1 ELSE 0 END),
                SUM(profit),
                AVG(profit_pct)
            FROM trades
            WHERE sell_date >= ?
            ''', (start,))
            
            r = c.fetchone()
            conn.close()
            
            if r and r[0] > 0:
                total = r[0]
                wins = r[1]
                total_profit = r[2] or 0
                avg_return = r[3] or 0
                win_rate = wins / total * 100
                
                return {
                    "交易次数": total,
                    "盈利次数": wins,
                    "胜率": f"{win_rate:.1f}%",
                    "总盈亏": f"{total_profit:.2f}元",
                    "平均收益": f"{avg_return:.2f}%"
                }
            
        except Exception as e:
            print(f"❌ 总结失败: {e}")
        
        return {}
    
    def optimize(self):
        """优化策略"""
        print("\n🔄 策略优化...")
        
        summary = self.get_summary(30)
        if summary:
            print("📊 近期表现:")
            for k, v in summary.items():
                print(f"   {k}: {v}")
            
            # 简单优化
            win_rate = float(summary.get("胜率", "0%").replace("%", ""))
            if win_rate < 60:
                print("💡 建议: 提高买入标准")
            else:
                print("💡 建议: 保持当前策略")
        
        print("✅ 优化完成")

# 主函数
if __name__ == "__main__":
    trader = FastTrader()
    
    print("🚀 快速短线交易系统")
    print("="*40)
    
    # 测试
    stocks = ["600096", "000001", "600036"]
    
    print(f"\n📊 分析 {len(stocks)} 只股票:")
    for code in stocks:
        res = trader.analyze(code)
        if res:
            print(f"  {code}: {res['rec']} (预期{res['exp_return']}%)")
    
    # 最优
    best = trader.find_best(stocks)
    if best:
        print(f"\n🎯 推荐操作:")
        print(f"  股票: {best['code']}")
        print(f"  买入价: ¥{best['buy']:.2f}")
        print(f"  目标价: ¥{best['target']:.2f}")
        print(f"  止损价: ¥{best['stop']:.2f}")
        print(f"  仓位: {best['pos']*100:.0f}%")
        print(f"  持有: {best['days']}天")
    
    # 优化
    trader.optimize()
    
    print(f"\n✅ 系统就绪")
    print(f"数据库: {trader.db}")
    print("明天可查询:")
    print("1. 具体盈亏")
    print("2. 原因分析")
    print("3. 优化建议")