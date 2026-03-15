#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
福斯特（603806）专业分析 - 使用akshare数据
全方位分析：技术面、基本面、市场情绪、风险控制
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

print("="*70)
print("🎯 福斯特（603806）全方位专业分析报告")
print("="*70)
print("分析时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print()

class FosterProfessionalAnalyzer:
    """福斯特专业分析器"""
    
    def __init__(self, code="603806"):
        self.code = code
        self.data = {}
        self.analysis = {}
    
    def fetch_all_data(self):
        """获取所有需要的数据"""
        print("📥 正在获取福斯特数据...")
        
        try:
            # 1. 获取日线数据（最近1年）
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            print("  获取日线数据...")
            daily_df = ak.stock_zh_a_hist(
                symbol=self.code, 
                period="daily", 
                start_date=start_date, 
                end_date=end_date, 
                adjust=""
            )
            
            if not daily_df.empty:
                # 重命名列以统一格式
                daily_df = daily_df.rename(columns={
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close', 
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '涨跌幅': 'pct_change',
                    '涨跌额': 'change',
                    '换手率': 'turnover_rate'
                })
                daily_df['date'] = pd.to_datetime(daily_df['date'])
                daily_df = daily_df.sort_values('date').reset_index(drop=True)
                self.data['daily'] = daily_df
                print(f"  ✅ 获取日线数据 {len(daily_df)} 条")
            else:
                print("  ❌ 日线数据为空")
                return False
            
            # 2. 获取股票基本信息
            print("  获取股票基本信息...")
            try:
                stock_info = ak.stock_individual_info_em(symbol=self.code)
                if not stock_info.empty:
                    self.data['info'] = stock_info
                    print(f"  ✅ 获取股票信息")
            except:
                print("  ⚠️  股票信息获取失败，使用默认信息")
                self.data['info'] = pd.DataFrame({
                    'item': ['股票名称', '上市日期', '总市值', '流通市值'],
                    'value': ['福斯特', '2014-12-05', '待获取', '待获取']
                })
            
            # 3. 获取实时行情
            print("  获取实时行情...")
            try:
                spot_df = ak.stock_zh_a_spot_em()
                if not spot_df.empty:
                    foster_spot = spot_df[spot_df['代码'] == self.code]
                    if not foster_spot.empty:
                        self.data['spot'] = foster_spot.iloc[0]
                        print(f"  ✅ 获取实时行情")
            except:
                print("  ⚠️  实时行情获取失败")
            
            # 4. 获取资金流向
            print("  获取资金流向...")
            try:
                money_flow = ak.stock_individual_fund_flow(stock=self.code, market="sh")
                if not money_flow.empty:
                    self.data['money_flow'] = money_flow
                    print(f"  ✅ 获取资金流向数据")
            except:
                print("  ⚠️  资金流向获取失败")
            
            return True
            
        except Exception as e:
            print(f"  ❌ 数据获取失败: {e}")
            return False
    
    def calculate_technical_indicators(self):
        """计算技术指标（应用刚学习的指标）"""
        if 'daily' not in self.data:
            return
        
        print("\n📊 计算技术指标...")
        df = self.data['daily'].copy()
        
        # 1. 基础移动平均线
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        # 2. RSI（相对强弱指数）
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 3. MACD（指数平滑移动平均线）
        df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']
        
        # 4. ATR（平均真实波幅）- 刚学习的指标
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = tr.rolling(window=14).mean()
        
        # 5. ADX（平均趋向指数）- 刚学习的指标（简化版）
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
        
        atr = df['ATR'].replace(0, np.nan)
        plus_di = 100 * plus_dm.rolling(window=14).mean() / atr
        minus_di = 100 * minus_dm.rolling(window=14).mean() / atr
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
        df['ADX'] = dx.rolling(window=14).mean()
        df['plus_DI'] = plus_di
        df['minus_DI'] = minus_di
        
        # 6. CCI（商品通道指数）- 刚学习的指标
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma = typical_price.rolling(window=20).mean()
        mean_deviation = abs(typical_price - sma).rolling(window=20).mean()
        df['CCI'] = (typical_price - sma) / (0.015 * mean_deviation.replace(0, np.nan))
        
        # 7. 布林带
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        df['BB_std'] = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * 2)
        df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * 2)
        
        self.data['daily_with_indicators'] = df
        print("✅ 技术指标计算完成")
    
    def analyze_technical(self):
        """技术分析"""
        if 'daily_with_indicators' not in self.data:
            return
        
        df = self.data['daily_with_indicators']
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        analysis = {}
        
        # 价格分析
        current_price = latest['close']
        prev_price = prev['close']
        price_change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
        
        analysis['price'] = {
            'current': round(current_price, 2),
            'change': round(price_change_pct, 2),
            'direction': '上涨' if price_change_pct > 0 else '下跌',
            'volume': int(latest['volume']),
            'turnover_rate': round(latest.get('turnover_rate', 0), 2)
        }
        
        # 趋势分析
        if pd.notna(latest.get('MA5')) and pd.notna(latest.get('MA20')):
            ma5 = latest['MA5']
            ma20 = latest['MA20']
            analysis['trend'] = {
                'ma_trend': '上涨趋势' if ma5 > ma20 else '下跌趋势',
                'ma_position': '均线上方' if current_price > ma20 else '均线下方',
                'ma5': round(ma5, 2),
                'ma20': round(ma20, 2)
            }
        
        # 技术指标状态
        indicators = {}
        
        # RSI
        if pd.notna(latest.get('RSI')):
            rsi = latest['RSI']
            indicators['rsi'] = {
                'value': round(rsi, 1),
                'status': '超买' if rsi > 70 else '超卖' if rsi < 30 else '正常',
                'signal': '卖出' if rsi > 70 else '买入' if rsi < 30 else '持有'
            }
        
        # MACD
        if pd.notna(latest.get('MACD')) and pd.notna(latest.get('MACD_signal')):
            macd = latest['MACD']
            signal = latest['MACD_signal']
            indicators['macd'] = {
                'value': round(macd, 3),
                'signal': round(signal, 3),
                'status': '金叉' if macd > signal else '死叉',
                'direction': '买入' if macd > signal else '卖出'
            }
        
        # ATR（刚学习的指标）
        if pd.notna(latest.get('ATR')):
            atr = latest['ATR']
            indicators['atr'] = {
                'value': round(atr, 3),
                'volatility': round(atr / current_price * 100, 2),
                'suggested_stop_loss': round(atr * 2, 2)
            }
        
        # ADX（刚学习的指标）
        if pd.notna(latest.get('ADX')):
            adx = latest['ADX']
            indicators['adx'] = {
                'value': round(adx, 1),
                'strength': '强趋势' if adx > 25 else '弱趋势' if adx < 20 else '中等趋势',
                'direction': '上升' if latest.get('plus_DI', 0) > latest.get('minus_DI', 0) else '下降'
            }
        
        # CCI（刚学习的指标）
        if pd.notna(latest.get('CCI')):
            cci = latest['CCI']
            indicators['cci'] = {
                'value': round(cci, 1),
                'status': '超买' if cci > 100 else '超卖' if cci < -100 else '正常',
                'signal': '卖出' if cci > 100 else '买入' if cci < -100 else '持有'
            }
        
        analysis['indicators'] = indicators
        
        # 关键价位
        support = df['low'].tail(20).min()
        resistance = df['high'].tail(20).max()
        analysis['key_levels'] = {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'current_vs_support': '支撑上方' if current_price > support else '支撑下方'
        }
        
        self.analysis['technical'] = analysis
    
    def analyze_fundamental(self):
        """基本面分析"""
        analysis = {}
        
        # 从股票信息中提取
        if 'info' in self.data:
            info_df = self.data['info']
            if not info_df.empty:
                fundamentals = {}
                for _, row in info_df.iterrows():
                    item = row['item']
                    value = row['value']
                    fundamentals[item] = value
                analysis['info'] = fundamentals
        
        # 实时行情信息
        if 'spot' in self.data:
            spot = self.data['spot']
            if not spot.empty:
                analysis['spot'] = {
                    '最新价': spot.get('最新价', 'N/A'),
                    '涨跌幅': spot.get('涨跌幅', 'N/A'),
                    '成交量': spot.get('成交量', 'N/A'),
                    '成交额': spot.get('成交额', 'N/A')
                }
        
        self.analysis['fundamental'] = analysis
    
    def analyze_market_sentiment(self):
        """市场情绪分析"""
        analysis = {}
        
        # 资金流向分析
        if 'money_flow' in self.data:
            money_flow = self.data['money_flow']
            if not money_flow.empty:
                analysis['money_flow'] = {
                    '主力净流入': money_flow.get('主力净流入', 'N/A'),
                    '散户净流入': money_flow.get('散户净流入', 'N/A'),
                    '资金状态': '净流入' if money_flow.get('主力净流入', 0) > 0 else '净流出'
                }
        
        # 基于价格变化的情绪
        if 'daily' in self.data:
            df = self.data['daily']
            if len(df) >= 5:
                recent_change = (df['close'].iloc[-1] - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100
                if recent_change > 5:
                    analysis['price_sentiment'] = '乐观'
                elif recent_change < -5:
                    analysis['price_sentiment'] = '悲观'
                else:
                    analysis['price_sentiment'] = '中性'
        
        self.analysis['sentiment'] = analysis
    
    def generate_investment_advice(self):
        """生成投资建议"""
        advice = {
            'technical_signals': [],
            'risk_warnings': [],
            'trading_suggestions': [],
            'short_term_outlook': {}
        }
        
        # 技术信号
        if 'technical' in self.analysis:
            tech = self.analysis['technical']
            
            # 趋势信号
            if 'trend' in tech:
                trend = tech['trend']
                if '上涨' in trend['ma_trend']:
                    advice['technical_signals'].append('上涨趋势中，适合趋势跟踪')
                else:
                    advice['technical_signals'].append('下跌趋势中，建议谨慎操作')
            
            # 指标信号
            if 'indicators' in tech:
                indicators = tech['indicators']
                
                if 'rsi' in indicators:
                    rsi_status = indicators['rsi']['status']
                    if rsi_status == '超买':
                        advice['technical_signals'].append('RSI超买，警惕回调')
                    elif rsi_status == '超卖':
                        advice['technical_signals'].append('RSI超卖，关注机会')
                
                if 'macd' in indicators:
                    macd_status = indicators['macd']['status']
                    if macd_status == '金叉':
                        advice['technical_signals'].append('MACD金叉，上涨信号')
                    elif macd_status == '死叉':
                        advice['technical_signals'].append('MACD死叉，下跌信号')
                
                if 'cci' in indicators:
                    cci_status = indicators['cci']['status']
                    if cci_status == '超买':
                        advice['technical_signals'].append('CCI超买，考虑减仓')
                    elif cci_status == '超卖':
                        advice['technical_signals'].append('CCI超卖，考虑加仓')
                
                if 'atr' in indicators:
                    atr_info = indicators['atr']
                    advice['technical_signals'].append(f"波动率{atr_info['volatility']}%，建议止损±{atr_info['suggested_stop_loss']}")
        
        # 风险警告
        advice['risk_warnings'].extend([
            '股市有风险，投资需谨慎',
            '以上分析仅供参考，不构成投资建议',
            '请结合自身风险承受能力决策',
            '建议设置止损位控制风险'
        ])
        
        # 交易建议
        if 'technical' in self.analysis and 'price' in self.analysis['technical']:
            price_info = self.analysis['technical']['price']
            
            if price_info['direction'] == '上涨':
                advice['trading_suggestions'].append('可考虑逢低布局')
            else:
                advice['trading_suggestions'].append('建议观望或谨慎操作')
            
            if 'key_levels' in self.analysis['technical']:
                levels = self.analysis['technical']['key_levels']
                advice['trading_suggestions'].append(f"支撑位:{levels['support']}，阻力位:{levels['resistance']}")
        
        # 短期展望
        if 'daily' in self.data:
            df = self.data