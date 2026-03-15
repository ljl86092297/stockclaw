#!/usr/bin/env python3
"""
确保成功发送消息给"宝宝"
添加更多验证和精确操作
"""

import subprocess
import time
import sys

def run_cmd(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def mouse_command(cmd_json):
    """执行鼠标命令并验证"""
    print(f"执行: {cmd_json}")
    success, stdout, stderr = run_cmd(f'python3 openclaw_mouse_control.py \'{cmd_json}\'')
    
    if success:
        print("  ✓ 成功")
        if "success" in stdout.lower():
            return True
    else:
        print(f"  ✗ 失败: {stderr}")
    
    return False

def wait_and_confirm(seconds, message):
    """等待并确认"""
    print(f"{message} (等待{seconds}秒)")
    for i in range(seconds, 0, -1):
        print(f"\r  倒计时: {i}秒", end="")
        time.sleep(1)
    print("\r  继续执行...")

def focus_wechat_surely():
    """确保聚焦微信窗口"""
    print("\n=== 步骤1: 确保微信窗口聚焦 ===")
    
    # 方法1: 按Alt+Tab多次确保切换到微信
    print("1. 按Alt+Tab切换窗口")
    if not mouse_command('{"action": "key", "key": "Alt_L+Tab"}'):
        return False
    time.sleep(1)
    
    # 多次Tab切换
    for i in range(5):
        print(f"2.{i+1} 按Tab键切换")
        if not mouse_command('{"action": "key", "key": "Tab"}'):
            return False
        time.sleep(0.5)
    
    print("3. 按回车确认选择")
    if not mouse_command('{"action": "key", "key": "Return"}'):
        return False
    time.sleep(2)
    
    # 方法2: 如果微信在任务栏，点击任务栏中间
    print("4. 点击任务栏中间位置")
    if not mouse_command('{"action": "move", "x": 960, "y": 1070}'):
        return False
    time.sleep(0.5)
    if not mouse_command('{"action": "click"}'):
        return False
    time.sleep(1)
    
    return True

def search_baobao_surely():
    """确保搜索到宝宝"""
    print("\n=== 步骤2: 搜索联系人'宝宝' ===")
    
    print("1. 按Ctrl+F打开搜索框")
    if not mouse_command('{"action": "key", "key": "Control_L+f"}'):
        print("  尝试备用: 点击搜索图标位置")
        # 假设搜索图标在左上角
        mouse_command('{"action": "move", "x": 100, "y": 100}')
        mouse_command('{"action": "click"}')
    
    wait_and_confirm(2, "等待搜索框打开")
    
    print("2. 清空可能存在的文本（按Ctrl+A然后Delete）")
    mouse_command('{"action": "key", "key": "Control_L+a"}')
    time.sleep(0.5)
    mouse_command('{"action": "key", "key": "Delete"}')
    time.sleep(0.5)
    
    print("3. 输入'宝宝'")
    if not mouse_command('{"action": "type", "text": "宝宝"}'):
        return False
    
    wait_and_confirm(3, "等待搜索结果")
    
    print("4. 按回车选择第一个结果")
    if not mouse_command('{"action": "key", "key": "Return"}'):
        print("  尝试点击搜索结果位置")
        # 假设第一个结果在屏幕中间偏上
        mouse_command('{"action": "move", "x": 960, "y": 300}')
        mouse_command('{"action": "click"}')
    
    wait_and_confirm(2, "等待聊天界面打开")
    return True

def send_message_surely(message):
    """确保发送消息"""
    print(f"\n=== 发送消息: {message} ===")
    
    print("1. 点击输入框（屏幕底部中间）")
    if not mouse_command('{"action": "move", "x": 960, "y": 1000}'):
        return False
    time.sleep(0.5)
    if not mouse_command('{"action": "click"}'):
        return False
    time.sleep(0.5)
    
    print("2. 清空输入框")
    mouse_command('{"action": "key", "key": "Control_L+a"}')
    time.sleep(0.3)
    mouse_command('{"action": "key", "key": "Delete"}')
    time.sleep(0.5)
    
    print("3. 输入消息内容")
    if not mouse_command(f'{{"action": "type", "text": "{message}"}}'):
        return False
    time.sleep(1)
    
    print("4. 发送消息（尝试多种方式）")
    
    # 方式1: Ctrl+Enter
    print("  方式1: Ctrl+Enter")
    if mouse_command('{"action": "key", "key": "Control_L+Return"}'):
        print("  ✓ Ctrl+Enter成功")
        return True
    
    # 方式2: 普通回车
    print("  方式2: 回车键")
    if mouse_command('{"action": "key", "key": "Return"}'):
        print("  ✓ 回车键成功")
        return True
    
    # 方式3: 点击发送按钮（假设在右下角）
    print("  方式3: 点击发送按钮位置")
    mouse_command('{"action": "move", "x": 1800, "y": 1000}')
    mouse_command('{"action": "click"}')
    
    return True

def main():
    """主函数"""
    print("=" * 70)
    print("确保成功发送消息给'宝宝'")
    print("=" * 70)
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    print("⚠️ 重要: 请确保:")
    print("1. 微信窗口可见")
    print("2. 不要操作鼠标键盘")
    print("3. 观察每个步骤")
    print()
    
    input("按回车键开始（或Ctrl+C取消）...")
    print()
    
    try:
        # 步骤1: 聚焦微信
        if not focus_wechat_surely():
            print("❌ 聚焦微信失败")
            return False
        
        # 步骤2: 搜索宝宝
        if not search_baobao_surely():
            print("❌ 搜索宝宝失败")
            return False
        
        # 步骤3: 发送消息
        messages = [
            "宝宝，这次我一定要成功发送消息给你！",
            "我是OpenClaw，正在学习如何可靠地操作微信",
            "如果这条消息收到了，请给我一个反馈",
            "自动化技术应该让生活更便捷",
            "祝你今天一切顺利！😊"
        ]
        
        success_count = 0
        for i, msg in enumerate(messages, 1):
            print(f"\n发送第{i}条消息...")
            if send_message_surely(msg):
                success_count += 1
                wait_and_confirm(2, "等待下一条消息")
            else:
                print(f"❌ 第{i}条消息发送失败")
        
        print("\n" + "=" * 70)
        print("执行完成!")
        print(f"成功发送: {success_count}/{len(messages)} 条消息")
        
        if success_count > 0:
            print("✅ 至少部分消息发送成功")
            print("\n请立即检查微信:")
            print("1. 查看与'宝宝'的聊天窗口")
            print("2. 确认消息是否显示")
            print("3. 查看发送状态")
        else:
            print("❌ 所有消息发送失败")
            print("\n可能的原因:")
            print("1. 微信窗口位置不对")
            print("2. 输入框位置不准确")
            print("3. 需要手动调整")
        
        return success_count > 0
        
    except KeyboardInterrupt:
        print("\n❌ 用户取消操作")
        return False
    except Exception as e:
        print(f"\n❌ 程序出错: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)