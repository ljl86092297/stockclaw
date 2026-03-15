#!/usr/bin/env python3
"""
风险管理模块
集成到高胜率交易系统
"""

from typing import Dict, Tuple, Optional
import json
from datetime import datetime

class RiskManager:
    """风险管理器"""
    
    def __init__(self, account_size: float = 100000.0):
        """
        初始化风险管理器
        
        参数:
            account_size: 账户资金规模（默认10万）
        """
        self.account_size = account_size
        self.trade_records = []  # 交易记录
        self.risk_parameters = {
            "max_single_loss_pct": 2.0,    # 单笔最大亏损百分比
            "max_total_position": 0.30,    # 总仓位限制
            "max_drawdown_pct": 10.0,      # 最大回撤限制
            "min_win_rate": 60.0,          # 最低胜率要求
            "min_risk_reward": 2.0,        # 最低风险收益比
            "consecutive_loss_limit": 3,   # 连续亏损限制
        }
        
        # 当前状态
        self.current_position = 0.0
        self.current_profit = 0.0
        self.max_profit = 0.0
        self.consecutive_losses = 0
        
    def calculate_position(self, win_rate: float, risk_reward: float, 
                          risk_level: str = "中") -> Tuple[float, Dict]:
        """
        计算建议仓位
        
        参数:
            win_rate: 预估胜率（百分比）
            risk_reward: 风险收益比
            risk_level: 风险等级（低/中/高）
            
        返回:
            (position_pct, details)
        """
        # 1. 基础检查
        if win_rate < self.risk_parameters["min_win_rate"]:
            return 0.0, {"status": "REJECTED", "reason": f"胜率过低({win_rate:.1f}%<{self.risk_parameters['min_win_rate']}%)"}
        
        if risk_reward < self.risk_parameters["min_risk_reward"]:
            return 0.0, {"status": "REJECTED", "reason": f"风险收益比过低({risk_reward:.2f}<{self.risk_parameters['min_risk_reward']})"}
        
        # 2. 凯利公式计算理论仓位
        p = win_rate / 100  # 转换为小数
        b = risk_reward
        
        # 凯利公式：f = p - (1-p)/b
        kelly_position = p - (1 - p) / b
        
        # 3. 保守调整（使用半凯利）
        theoretical_position = kelly_position * 0.5
        
        # 4. 根据风险等级调整
        risk_adjustment = {
            "低": 1.0,
            "中": 0.8,
            "高": 0.6
        }
        adjusted_position = theoretical_position * risk_adjustment.get(risk_level, 0.8)
        
        # 5. 限制范围
        min_position = 0.05  # 最小仓位5%
        max_position = 0.25  # 最大仓位25%
        
        final_position = max(min_position, min(max_position, adjusted_position))
        
        # 6. 考虑连续亏损
        if self.consecutive_losses >= 2:
            final_position *= 0.5  # 连续亏损，仓位减半
        
        # 7. 考虑总仓位限制
        available_position = self.risk_parameters["max_total_position"] - self.current_position
        if final_position > available_position:
            final_position = available_position
        
        details = {
            "status": "APPROVED",
            "win_rate": win_rate,
            "risk_reward": risk_reward,
            "risk_level": risk_level,
            "kelly_position": kelly_position,
            "theoretical_position": theoretical_position,
            "adjusted_position": adjusted_position,
            "final_position": final_position,
            "position_amount": final_position * self.account_size,
            "max_single_loss": final_position * self.account_size * (self.risk_parameters["max_single_loss_pct"] / 100)
        }
        
        return final_position, details
    
    def calculate_stop_loss(self, buy_price: float, technical_stop: float, 
                           max_loss_pct: float = 6.0) -> Tuple[float, Dict]:
        """
        计算止损价
        
        参数:
            buy_price: 买入价
            technical_stop: 技术止损位
            max_loss_pct: 最大亏损百分比
            
        返回:
            (stop_price, details)
        """
        # 1. 百分比止损
        pct_stop = buy_price * (1 - max_loss_pct / 100)
        
        # 2. 取较严格者（价格较低者）
        stop_price = min(technical_stop, pct_stop)
        
        # 3. 计算实际亏损百分比
        actual_loss_pct = (buy_price - stop_price) / buy_price * 100
        
        # 4. 确保不超过单笔最大亏损
        max_allowed_loss = self.risk_parameters["max_single_loss_pct"]
        if actual_loss_pct > max_allowed_loss:
            stop_price = buy_price * (1 - max_allowed_loss / 100)
            actual_loss_pct = max_allowed_loss
        
        details = {
            "stop_price": stop_price,
            "technical_stop": technical_stop,
            "pct_stop": pct_stop,
            "actual_loss_pct": actual_loss_pct,
            "max_allowed_loss": max_allowed_loss,
            "stop_type": "技术止损" if stop_price == technical_stop else "百分比止损"
        }
        
        return stop_price, details
    
    def calculate_take_profit(self, buy_price: float, stop_price: float, 
                             risk_reward: float, target_return: Optional[float] = None) -> Tuple[float, Dict]:
        """
        计算止盈价
        
        参数:
            buy_price: 买入价
            stop_price: 止损价
            risk_reward: 风险收益比
            target_return: 目标收益率（可选）
            
        返回:
            (target_price, details)
        """
        # 1. 计算亏损金额
        loss_amount = buy_price - stop_price
        
        # 2. 计算目标盈利金额
        if target_return:
            # 使用指定的目标收益率
            target_profit = buy_price * (target_return / 100)
        else:
            # 基于风险收益比计算
            target_profit = loss_amount * risk_reward
        
        # 3. 计算目标价
        target_price = buy_price + target_profit
        
        # 4. 计算实际收益率和风险收益比
        actual_return = target_profit / buy_price * 100
        actual_risk_reward = target_profit / loss_amount if loss_amount > 0 else 0
        
        details = {
            "target_price": target_price,
            "buy_price": buy_price,
            "stop_price": stop_price,
            "loss_amount": loss_amount,
            "target_profit": target_profit,
            "actual_return": actual_return,
            "actual_risk_reward": actual_risk_reward,
            "method": "指定收益率" if target_return else "风险收益比"
        }
        
        return target_price, details
    
    def calculate_moving_stop(self, current_price: float, original_stop: float, 
                             profit_pct: float) -> Tuple[float, Dict]:
        """
        计算移动止损
        
        参数:
            current_price: 当前价格
            original_stop: 原始止损价
            profit_pct: 当前盈利百分比
            
        返回:
            (new_stop, details)
        """
        # 移动止损规则
        if profit_pct >= 20:
            # 盈利20%以上，止损提高到盈亏平衡点
            new_stop = original_stop * 1.20  # 至少保本
            stop_type = "保本止损"
        elif profit_pct >= 15:
            # 盈利15-20%，止损提高到盈利10%处
            new_stop = original_stop * 1.10
            stop_type = "盈利保护止损"
        elif profit_pct >= 10:
            # 盈利10-15%，止损提高到盈利5%处
            new_stop = original_stop * 1.05
            stop_type = "部分盈利保护"
        else:
            # 盈利不足10%，保持原始止损
            new_stop = original_stop
            stop_type = "原始止损"
        
        # 确保新止损不低于原始止损
        new_stop = max(new_stop, original_stop)
        
        details = {
            "new_stop": new_stop,
            "original_stop": original_stop,
            "current_price": current_price,
            "profit_pct": profit_pct,
            "stop_type": stop_type,
            "stop_raised_pct": (new_stop - original_stop) / original_stop * 100
        }
        
        return new_stop, details
    
    def record_trade(self, trade_data: Dict):
        """
        记录交易
        
        参数:
            trade_data: 交易数据字典
        """
        trade_data["record_time"] = datetime.now().isoformat()
        self.trade_records.append(trade_data)
        
        # 更新连续亏损计数
        if trade_data.get("result") == "亏损":
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # 更新仓位和盈利
        if trade_data.get("position_pct"):
            self.current_position += trade_data["position_pct"]
        
        if trade_data.get("profit_pct"):
            profit_amount = trade_data.get("profit_amount", 0)
            self.current_profit += profit_amount
            self.max_profit = max(self.max_profit, self.current_profit)
    
    def check_risk_limits(self) -> Dict:
        """
        检查风险限制
        
        返回:
            风险状态字典
        """
        # 计算当前回撤
        current_drawdown = 0
        if self.max_profit > 0:
            current_drawdown = (self.max_profit - self.current_profit) / self.account_size * 100
        
        warnings = []
        
        # 检查连续亏损
        if self.consecutive_losses >= self.risk_parameters["consecutive_loss_limit"]:
            warnings.append(f"连续亏损{self.consecutive_losses}次，建议暂停交易")
        
        # 检查回撤
        if current_drawdown >= self.risk_parameters["max_drawdown_pct"]:
            warnings.append(f"回撤达到{current_drawdown:.1f}%，超过限制{self.risk_parameters['max_drawdown_pct']}%")
        
        # 检查仓位
        if self.current_position > self.risk_parameters["max_total_position"]:
            warnings.append(f"总仓位{self.current_position*100:.1f}%，超过限制{self.risk_parameters['max_total_position']*100}%")
        
        status = {
            "current_position": self.current_position,
            "current_profit": self.current_profit,
            "max_profit": self.max_profit,
            "current_drawdown": current_drawdown,
            "consecutive_losses": self.consecutive_losses,
            "warnings": warnings,
            "risk_status": "正常" if not warnings else "警告"
        }
        
        return status
    
    def generate_trade_plan(self, analysis_result: Dict) -> Dict:
        """
        生成完整的交易计划
        
        参数:
            analysis_result: 分析结果
            
        返回:
            完整的交易计划
        """
        # 提取分析数据
        win_rate = analysis_result.get("win_rate_estimate", 60)
        risk_reward = analysis_result.get("risk_reward", 2.0)
        risk_level = analysis_result.get("risk_level", "中")
        current_price = analysis_result.get("current_price", 0)
        technical_stop = analysis_result.get("technical_stop", 0)
        
        # 1. 计算仓位
        position_pct, position_details = self.calculate_position(win_rate, risk_reward, risk_level)
        
        if position_details["status"] == "REJECTED":
            return {
                "status": "REJECTED",
                "reason": position_details["reason"],
                "recommendation": "不交易"
            }
        
        # 2. 计算止损
        max_loss_pct = 6 if risk_level == "中" else (5 if risk_level == "低" else 8)
        stop_price, stop_details = self.calculate_stop_loss(current_price, technical_stop, max_loss_pct)
        
        # 3. 计算止盈
        target_price, target_details = self.calculate_take_profit(current_price, stop_price, risk_reward)
        
        # 4. 生成交易计划
        trade_plan = {
            "status": "APPROVED",
            "position_pct": position_pct,
            "position_amount": position_pct * self.account_size,
            "buy_price": current_price * 0.995,  # 允许0.5%回调
            "stop_price": stop_price,
            "target_price": target_price,
            "expected_return": target_details["actual_return"],
            "expected_risk": stop_details["actual_loss_pct"],
            "risk_reward": target_details["actual_risk_reward"],
            "holding_days": 5 if risk_level == "中" else (7 if risk_level == "低" else 3),
            "position_details": position_details,
            "stop_details": stop_details,
            "target_details": target_details,
            "risk_level": risk_level,
            "win_rate": win_rate
        }
        
        return trade_plan

# 测试函数
def test_risk_manager():
    """测试风险管理器"""
    print("🧪 测试风险管理器...")
    
    rm = RiskManager(account_size=100000)
    
    # 测试1：仓位计算
    print("\n1. 仓位计算测试:")
    position, details = rm.calculate_position(win_rate=65, risk_reward=3.0, risk_level="中")
    print(f"   胜率65%，风险收益比3.0，风险等级中")
    print(f"   建议仓位: {position*100:.1f}% (¥{details['position_amount']:.0f})")
    print(f"   最大单笔亏损: ¥{details['max_single_loss']:.0f}")
    
    # 测试2：止损计算
    print("\n2. 止损计算测试:")
    stop_price, stop_details = rm.calculate_stop_loss(
        buy_price=100, 
        technical_stop=92, 
        max_loss_pct=6
    )
    print(f"   买入价: ¥100，技术止损: ¥92，最大亏损6%")
    print(f"   最终止损: ¥{stop_price:.2f} ({stop_details['actual_loss_pct']:.1f}%)")
    print(f"   止损类型: {stop_details['stop_type']}")
    
    # 测试3：止盈计算
    print("\n3. 止盈计算测试:")
    target_price, target_details = rm.calculate_take_profit(
        buy_price=100,
        stop_price=stop_price,
        risk_reward=3.0
    )
    print(f"   买入价: ¥100，止损价: ¥{stop_price:.2f}，风险收益比3.0")
    print(f"   目标价: ¥{target_price:.2f} (+{target_details['actual_return']:.1f}%)")
    print(f"   实际风险收益比: {target_details['actual_risk_reward']:.2f}")
    
    # 测试4：移动止损
    print("\n4. 移动止损测试:")
    new_stop, move_details = rm.calculate_moving_stop(
        current_price=115,
        original_stop=stop_price,
        profit_pct=15
    )
    print(f"   当前价: ¥115，原始止损: ¥{stop_price:.2f}，盈利15%")
    print(f"   新止损: ¥{new_stop:.2f} ({move_details['stop_type']})")
    
    # 测试5：生成交易计划
    print("\n5. 交易计划生成测试:")
    analysis_result = {
        "win_rate_estimate": 68,
        "risk_reward": 3.2,
        "risk_level": "中",
        "current_price": 100,
        "technical_stop": 92
    }
    trade_plan = rm.generate_trade_plan(analysis_result)
    
    if trade_plan["status"] == "APPROVED":
        print(f"   状态: 通过")
        print(f"   建议仓位: {trade_plan['position_pct']*100:.1f}%")
        print(f"   买入价: ¥{trade_plan['buy_price']:.2f}")
        print(f"   止损价: ¥{trade_plan['stop_price']:.2f} (-{trade_plan['expected_risk']:.1f}%)")
        print(f"   目标价: ¥{trade_plan['target_price']:.2f} (+{trade_plan['expected_return']:.1f}%)")
        print(f"   风险收益比: {trade_plan['risk_reward']:.2f}")
        print(f"   建议持有: {trade_plan['holding_days']}天")
    else:
        print(f"   状态: 拒绝 - {trade_plan.get('reason', '未知原因')}")
    
    print("\n✅ 风险管理器测试完成")

if __name__ == "__main__":
    test_risk_manager()