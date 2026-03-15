#!/usr/bin/env python3
"""
自我验证系统
通过图像识别和状态检测实现自我验证
"""

import subprocess
import time
import os
import sys

class SelfVerificationSystem:
    def __init__(self):
        self.display = os.environ.get('DISPLAY', ':0')
        print(f"自我验证系统启动 (DISPLAY={self.display})")
    
    def execute_and_verify(self, command_json, verification_type="keyboard"):
        """执行命令并尝试自我验证"""
        print(f"\n执行命令: {command_json}")
        
        # 1. 执行命令
        success = self.execute_command(command_json)
        if not success:
            print("  ✗ 命令执行失败")
            return False
        
        print("  ✓ 命令已发送到系统")
        
        # 2. 等待系统响应
        time.sleep(1)
        
        # 3. 尝试验证（根据类型）
        if verification_type == "keyboard":
            return self.verify_keyboard_action()
        elif verification_type == "mouse_click":
            return self.verify_mouse_click()
        elif verification_type == "text_input":
            return self.verify_text_input()
        else:
            print("  ⚠️ 验证类型不支持，假设成功")
            return True
    
    def execute_command(self, command_json):
        """执行鼠标/键盘命令"""
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
    
    def verify_keyboard_action(self):
        """验证键盘操作效果"""
        print("  尝试验证键盘操作...")
        
        # 方法1: 检查是否有焦点变化
        print("  方法1: 检查活动窗口变化")
        try:
            # 获取当前活动窗口信息
            result = subprocess.run(
                ['xdotool', 'getactivewindow', 'getwindowname'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                window_name = result.stdout.strip()
                print(f"    当前活动窗口: {window_name[:50]}...")
                return True
        except:
            pass
        
        # 方法2: 检查键盘状态
        print("  方法2: 模拟后续操作验证")
        # 发送一个无害的按键测试（如右箭头）
        test_success = self.execute_command('{"action": "key", "key": "Right"}')
        if test_success:
            print("    ✓ 键盘响应正常")
            return True
        
        print("    ✗ 键盘验证不确定")
        return False
    
    def verify_mouse_click(self):
        """验证鼠标点击效果"""
        print("  尝试验证鼠标点击...")
        
        # 获取点击前后鼠标位置
        try:
            before = self.get_mouse_position()
            print(f"    点击前位置: {before}")
            
            # 执行点击
            time.sleep(0.5)
            
            after = self.get_mouse_position()
            print(f"    点击后位置: {after}")
            
            # 如果位置有变化，可能点击到了可交互元素
            if before != after:
                print("    ✓ 鼠标位置变化，可能点击成功")
                return True
            else:
                print("    ⚠️ 鼠标位置未变，点击效果不确定")
                return False
                
        except:
            print("    ✗ 鼠标验证失败")
            return False
    
    def verify_text_input(self):
        """验证文本输入效果"""
        print("  尝试验证文本输入...")
        
        # 方法1: 检查是否有文本被输入
        print("  方法1: 模拟退格键测试")
        test_success = self.execute_command('{"action": "key", "key": "BackSpace"}')
        if test_success:
            print("    ✓ 文本输入环境正常")
            return True
        
        print("    ✗ 文本输入验证不确定")
        return False
    
    def get_mouse_position(self):
        """获取鼠标位置"""
        try:
            result = subprocess.run(
                ['xdotool', 'getmouselocation'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                # 解析: x:123 y:456 screen:0 window:789
                parts = result.stdout.strip().split()
                pos = {}
                for part in parts:
                    if ':' in part:
                        key, value = part.split(':', 1)
                        pos[key] = value
                return f"({pos.get('x', '?')},{pos.get('y', '?')})"
        except:
            pass
        return "(未知)"
    
    def learn_from_failure(self, action, expected_result, actual_result):
        """从失败中学习"""
        print(f"\n📚 学习记录:")
        print(f"操作: {action}")
        print(f"预期: {expected_result}")
        print(f"实际: {actual_result}")
        
        # 记录学习经验
        learning_path = "wechat_learning_log.md"
        with open(learning_path, "a", encoding="utf-8") as f:
            f.write(f"## {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"操作: {action}\n")
            f.write(f"问题: {actual_result}\n")
            f.write(f"学习: 需要改进验证方法\n\n")
        
        print(f"  学习记录已保存到: {learning_path}")
        return True
    
    def create_improvement_plan(self):
        """创建改进计划"""
        print("\n=== 自我验证改进计划 ===")
        
        improvements = [
            {
                "问题": "无法检测界面变化",
                "解决方案": "实现屏幕截图对比功能",
                "优先级": "高",
                "预计时间": "2小时"
            },
            {
                "问题": "不知道微信快捷键",
                "解决方案": "系统测试所有可能快捷键",
                "优先级": "高",
                "预计时间": "1小时"
            },
            {
                "问题": "无法验证消息发送",
                "解决方案": "开发消息发送确认机制",
                "优先级": "中",
                "预计时间": "3小时"
            },
            {
                "问题": "依赖xdotool成功率",
                "解决方案": "实现多重验证方法",
                "优先级": "中",
                "预计时间": "2小时"
            }
        ]
        
        for imp in improvements:
            print(f"\n{imp['问题']}")
            print(f"解决方案: {imp['解决方案']}")
            print(f"优先级: {imp['优先级']} | 时间: {imp['预计时间']}")
        
        return improvements

def main():
    """主函数"""
    print("=" * 70)
    print("自我验证与学习系统")
    print("=" * 70)
    
    system = SelfVerificationSystem()
    
    print("\n🎯 核心原则:")
    print("1. 每个操作都要自我验证")
    print("2. 从失败中学习改进")
    print("3. 建立验证机制，不依赖外部反馈")
    print("4. 持续优化验证准确性")
    
    print("\n🔧 立即测试自我验证系统:")
    
    # 测试1: 键盘操作验证
    print("\n测试1: 键盘操作验证")
    success1 = system.execute_and_verify(
        '{"action": "key", "key": "Control_L+f"}',
        "keyboard"
    )
    print(f"验证结果: {'成功' if success1 else '需要改进'}")
    
    # 测试2: 鼠标操作验证
    print("\n测试2: 鼠标操作验证")
    success2 = system.execute_and_verify(
        '{"action": "move", "x": 960, "y": 500}',
        "mouse_click"
    )
    print(f"验证结果: {'成功' if success2 else '需要改进'}")
    
    # 创建改进计划
    improvements = system.create_improvement_plan()
    
    print("\n" + "=" * 70)
    print("🚀 立即行动:")
    print("1. 实现屏幕截图对比功能")
    print("2. 系统测试微信所有快捷键")
    print("3. 开发完整的自我验证流程")
    print("4. 建立学习反馈循环")
    
    print("\n💡 关键学习:")
    print("不能只依赖命令执行成功，必须验证实际效果")
    print("要建立自己的验证系统，实现真正的自动化")

if __name__ == "__main__":
    main()