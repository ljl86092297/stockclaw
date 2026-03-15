#!/usr/bin/env python3
"""
诊断微信操作问题
找出为什么消息发送失败
"""

import subprocess
import time

def run_cmd(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def mouse_cmd(cmd_json):
    """执行鼠标命令"""
    success, stdout, stderr = run_cmd(f"python3 openclaw_mouse_control.py '{cmd_json}'")
    return success, stdout

def test_wechat_shortcuts():
    """测试微信快捷键"""
    print("=== 测试微信快捷键 ===")
    
    shortcuts = [
        ("Ctrl+F", "搜索联系人", "^f"),
        ("Ctrl+Alt+W", "微信截图", "^%w"),
        ("Ctrl+Alt+S", "微信收藏", "^%s"),
        ("F2", "微信文件助手", "F2"),
    ]
    
    for name, description, keys in shortcuts:
        print(f"\n测试: {name} ({description})")
        print(f"发送按键: {keys}")
        
        # 发送按键
        success, output = mouse_cmd(f'{{"action": "key", "key": "{keys}"}}')
        if success:
            print("  ✓ 命令执行成功")
            print(f"  输出: {output[:100]}")
        else:
            print("  ✗ 命令执行失败")
        
        time.sleep(1)
    
    return True

def test_search_function():
    """测试搜索功能"""
    print("\n=== 测试微信搜索功能 ===")
    
    print("1. 尝试打开搜索（多种方式）")
    
    # 方式1: Ctrl+F
    print("  方式1: Ctrl+F")
    mouse_cmd('{"action": "key", "key": "Control_L+f"}')
    time.sleep(2)
    
    # 方式2: 点击搜索图标位置
    print("  方式2: 点击搜索图标（假设位置）")
    mouse_cmd('{"action": "move", "x": 100, "y": 100}')
    mouse_cmd('{"action": "click"}')
    time.sleep(2)
    
    # 方式3: 按Tab导航
    print("  方式3: Tab导航到搜索框")
    for i in range(10):
        mouse_cmd('{"action": "key", "key": "Tab"}')
        time.sleep(0.3)
    
    return True

def test_message_sending():
    """测试消息发送"""
    print("\n=== 测试消息发送 ===")
    
    print("1. 测试输入框焦点")
    print("  点击屏幕底部中间（输入框位置）")
    mouse_cmd('{"action": "move", "x": 960, "y": 1000}')
    mouse_cmd('{"action": "click"}')
    time.sleep(1)
    
    print("2. 输入测试文本")
    mouse_cmd('{"action": "type", "text": "[测试输入]"}')
    time.sleep(1)
    
    print("3. 测试发送方式")
    
    # 方式1: 回车
    print("  方式1: 回车键")
    mouse_cmd('{"action": "key", "key": "Return"}')
    time.sleep(1)
    
    # 方式2: Ctrl+Enter
    print("  方式2: Ctrl+Enter")
    mouse_cmd('{"action": "key", "key": "Control_L+Return"}')
    time.sleep(1)
    
    # 方式3: 点击发送按钮
    print("  方式3: 点击发送按钮位置")
    mouse_cmd('{"action": "move", "x": 1800, "y": 1000}')
    mouse_cmd('{"action": "click"}')
    time.sleep(1)
    
    return True

def create_verification_plan():
    """创建验证计划"""
    print("\n=== 微信操作验证计划 ===")
    
    plan = [
        {
            "步骤": "1. 确认微信窗口状态",
            "验证方法": "用户视觉确认",
            "问题": "窗口是否真正在前台？标题栏是否高亮？",
            "解决方案": "请用户描述窗口状态"
        },
        {
            "步骤": "2. 验证搜索功能",
            "验证方法": "逐步测试 + 用户确认",
            "问题": "Ctrl+F是否打开搜索框？搜索框是否出现？",
            "解决方案": "测试多种搜索方式，用户确认搜索框出现"
        },
        {
            "步骤": "3. 验证联系人选择",
            "验证方法": "用户确认搜索结果",
            "问题": "是否搜索到'宝宝'？是否进入聊天窗口？",
            "解决方案": "用户确认聊天窗口打开"
        },
        {
            "步骤": "4. 验证消息发送",
            "验证方法": "用户确认消息出现",
            "问题": "消息是否出现在聊天窗口？发送状态如何？",
            "解决方案": "用户截图或描述消息状态"
        }
    ]
    
    for item in plan:
        print(f"\n{item['步骤']}")
        print(f"验证方法: {item['验证方法']}")
        print(f"可能问题: {item['问题']}")
        print(f"解决方案: {item['解决方案']}")
    
    return plan

def main():
    """主函数"""
    print("微信操作问题诊断")
    print("=" * 60)
    print("时间:", time.strftime("%H:%M:%S"))
    print()
    
    print("⚠️ 重要发现: 我的判断方式错误")
    print("我只检查了xdotool命令是否执行成功")
    print("但没有验证微信界面是否真的发生变化")
    print()
    
    # 测试快捷键
    test_wechat_shortcuts()
    
    # 测试搜索功能
    test_search_function()
    
    # 测试消息发送
    test_message_sending()
    
    # 创建验证计划
    create_verification_plan()
    
    print("\n" + "=" * 60)
    print("🎯 新的工作流程:")
    print("1. 执行一个操作")
    print("2. 请您确认界面变化")
    print("3. 根据您的反馈继续或调整")
    print("4. 重复直到成功")
    print()
    print("❓ 请回答:")
    print("1. 当我按Ctrl+F时，微信界面有什么变化？")
    print("2. 搜索框出现了吗？在哪里？")
    print("3. 当前微信窗口显示什么内容？")

if __name__ == "__main__":
    main()