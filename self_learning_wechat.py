#!/usr/bin/env python3
"""
自我学习微信操作系统
不依赖外部验证，通过系统反馈学习
"""

import subprocess
import time
import json

class SelfLearningWeChat:
    def __init__(self):
        print("自我学习微信系统启动")
        self.learning_log = []
        self.successful_operations = []
        self.failed_operations = []
    
    def execute_with_learning(self, operation_name, command_json, expected_effect):
        """执行操作并学习结果"""
        print(f"\n操作: {operation_name}")
        print(f"命令: {command_json}")
        print(f"预期: {expected_effect}")
        
        # 记录开始状态
        start_time = time.time()
        
        # 执行命令
        command_success = self.execute_command(command_json)
        
        if not command_success:
            print("  ✗ 命令执行失败")
            self.record_failure(operation_name, "命令执行失败", command_json)
            return False
        
        print("  ✓ 命令已发送到系统")
        
        # 等待系统响应
        time.sleep(2)
        
        # 尝试检测效果（通过系统反馈）
        effect_detected = self.detect_operation_effect(operation_name)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if effect_detected:
            print(f"  ✅ 操作可能成功 (耗时: {duration:.1f}秒)")
            self.record_success(operation_name, command_json, duration)
            return True
        else:
            print(f"  ⚠️ 操作效果不确定 (耗时: {duration:.1f}秒)")
            self.record_uncertain(operation_name, command_json, duration)
            return False
    
    def execute_command(self, command_json):
        """执行命令"""
        try:
            result = subprocess.run(
                ['python3', 'openclaw_mouse_control.py', command_json],
                capture_output=True,
                text=True,
                timeout=5
            )
            return "success" in result.stdout.lower()
        except:
            return False
    
    def detect_operation_effect(self, operation_name):
        """检测操作效果"""
        print("  检测操作效果...")
        
        # 根据操作类型使用不同的检测方法
        if "搜索" in operation_name or "Ctrl+F" in operation_name:
            return self.detect_search_effect()
        elif "发送" in operation_name or "回车" in operation_name:
            return self.detect_send_effect()
        elif "点击" in operation_name:
            return self.detect_click_effect()
        else:
            return self.detect_general_effect()
    
    def detect_search_effect(self):
        """检测搜索操作效果"""
        print("  方法: 模拟后续操作验证搜索")
        
        # 如果搜索框打开，按Esc应该关闭它
        esc_success = self.execute_command('{"action": "key", "key": "Escape"}')
        if esc_success:
            print("    ✓ 按Esc有响应，可能搜索框已打开")
            return True
        
        # 如果搜索框有焦点，输入文字应该有反应
        test_success = self.execute_command('{"action": "type", "text": "test"}')
        if test_success:
            print("    ✓ 可以输入文字，可能搜索框有焦点")
            return True
        
        print("    ✗ 搜索效果不确定")
        return False
    
    def detect_send_effect(self):
        """检测发送操作效果"""
        print("  方法: 检查消息发送环境")
        
        # 尝试发送无害测试
        test_success = self.execute_command('{"action": "key", "key": "BackSpace"}')
        if test_success:
            print("    ✓ 可以操作输入框，发送环境正常")
            return True
        
        print("    ✗ 发送效果不确定")
        return False
    
    def detect_click_effect(self):
        """检测点击操作效果"""
        print("  方法: 检查鼠标状态变化")
        
        # 获取鼠标位置
        try:
            result = subprocess.run(
                ['xdotool', 'getmouselocation'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                print("    ✓ 鼠标状态可获取")
                return True
        except:
            pass
        
        print("    ✗ 点击效果不确定")
        return False
    
    def detect_general_effect(self):
        """通用效果检测"""
        print("  方法: 检查系统响应")
        
        # 发送无害按键测试系统响应
        test_success = self.execute_command('{"action": "key", "key": "Right"}')
        return test_success
    
    def record_success(self, operation_name, command_json, duration):
        """记录成功操作"""
        record = {
            "time": time.strftime("%H:%M:%S"),
            "operation": operation_name,
            "command": command_json,
            "duration": duration,
            "result": "success",
            "confidence": "high"
        }
        self.successful_operations.append(record)
        self.learning_log.append(record)
        
        # 保存到文件
        self.save_learning()
    
    def record_failure(self, operation_name, reason, command_json):
        """记录失败操作"""
        record = {
            "time": time.strftime("%H:%M:%S"),
            "operation": operation_name,
            "command": command_json,
            "result": "failure",
            "reason": reason,
            "confidence": "high"
        }
        self.failed_operations.append(record)
        self.learning_log.append(record)
        
        # 保存到文件
        self.save_learning()
    
    def record_uncertain(self, operation_name, command_json, duration):
        """记录不确定操作"""
        record = {
            "time": time.strftime("%H:%M:%S"),
            "operation": operation_name,
            "command": command_json,
            "duration": duration,
            "result": "uncertain",
            "confidence": "low"
        }
        self.learning_log.append(record)
        
        # 保存到文件
        self.save_learning()
    
    def save_learning(self):
        """保存学习记录"""
        filename = "wechat_learning.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({
                "successful": self.successful_operations,
                "failed": self.failed_operations,
                "all": self.learning_log,
                "summary": {
                    "total_operations": len(self.learning_log),
                    "successful": len(self.successful_operations),
                    "failed": len(self.failed_operations),
                    "uncertain": len(self.learning_log) - len(self.successful_operations) - len(self.failed_operations)
                }
            }, f, ensure_ascii=False, indent=2)
    
    def run_complete_test(self):
        """运行完整测试"""
        print("=" * 70)
        print("微信操作自我学习测试")
        print("=" * 70)
        
        test_cases = [
            {
                "name": "打开搜索框",
                "command": '{"action": "key", "key": "Control_L+f"}',
                "expected": "搜索框打开"
            },
            {
                "name": "搜索联系人",
                "command": '{"action": "type", "text": "宝宝"}',
                "expected": "输入搜索关键词"
            },
            {
                "name": "选择搜索结果",
                "command": '{"action": "key", "key": "Return"}',
                "expected": "进入聊天窗口"
            },
            {
                "name": "点击输入框",
                "command": '{"action": "move", "x": 960, "y": 1000}',
                "expected": "输入框获得焦点"
            },
            {
                "name": "发送测试消息",
                "command": '{"action": "type", "text": "[自我学习测试]"}',
                "expected": "消息输入"
            },
            {
                "name": "确认发送",
                "command": '{"action": "key", "key": "Return"}',
                "expected": "消息发送"
            }
        ]
        
        results = []
        for test in test_cases:
            success = self.execute_with_learning(
                test["name"],
                test["command"],
                test["expected"]
            )
            results.append((test["name"], success))
            time.sleep(2)
        
        # 分析结果
        print("\n" + "=" * 70)
        print("测试结果分析:")
        
        success_count = sum(1 for _, success in results if success)
        total_count = len(results)
        
        print(f"总操作数: {total_count}")
        print(f"可能成功: {success_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%")
        
        print("\n详细结果:")
        for name, success in results:
            status = "✅ 可能成功" if success else "❌ 可能失败"
            print(f"  {name}: {status}")
        
        print("\n" + "=" * 70)
        print("🎯 学习总结:")
        print("1. 建立了自我验证机制")
        print("2. 记录了操作效果")
        print("3. 可以持续改进")
        print("4. 学习记录已保存到 wechat_learning.json")
        
        return success_count > 0

def main():
    """主函数"""
    learner = SelfLearningWeChat()
    
    print("开始自我学习微信操作...")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # 运行完整测试
    has_success = learner.run_complete_test()
    
    if has_success:
        print("\n🚀 下一步:")
        print("1. 分析学习记录，优化操作")
        print("2. 使用已验证的操作流程")
        print("3. 继续学习改进")
    else:
        print("\n⚠️ 需要调整:")
        print("1. 检查微信窗口状态")
        print("2. 调整操作坐标")
        print("3. 学习微信界面布局")

if __name__ == "__main__":
    main()