#!/usr/bin/env python3
"""
给微信联系人"宝宝"发送消息
"""

import subprocess
import time
import os

def mouse_cmd(command_json):
    """执行鼠标命令"""
    try:
        result = subprocess.run(
            ['python3', 'openclaw_mouse_control.py', command_json],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"命令执行失败: {e}")
        return None

def press_key(key_combo):
    """按下按键组合"""
    keys = key_combo.split('+')
    for key in keys:
        mouse_cmd(f'{{"action": "key", "key": "{key}"}}')
        time.sleep(0.1)
    time.sleep(0.5)

def click_at(x, y):
    """在指定位置点击"""
    mouse_cmd(f'{{"action": "move", "x": {x}, "y": {y}}}')
    time.sleep(0.3)
    mouse_cmd('{"action": "click"}')
    time.sleep(0.5)

def type_text(text):
    """输入文本"""
    mouse_cmd(f'{{"action": "type", "text": "{text}"}}')
    time.sleep(1)

def get_screen_info():
    """获取屏幕信息"""
    return {'width': 1920, 'height': 1080}

def focus_wechat():
    """聚焦微信窗口"""
    print("1. 聚焦微信窗口...")
    
    # 方法1：Alt+Tab切换到微信
    press_key('Alt_L+Tab')
    time.sleep(1)
    
    # 多次Tab确保切换到微信
    for _ in range(3):
        press_key('Tab')
        time.sleep(0.3)
    
    press_key('Return')
    time.sleep(2)
    
    # 方法2：如果微信在任务栏，点击任务栏
    screen = get_screen_info()
    taskbar_y = screen['height'] - 10
    
    # 扫描任务栏中间区域
    for x in range(screen['width']//2 - 200, screen['width']//2 + 200, 50):
        click_at(x, taskbar_y)
        time.sleep(0.2)
    
    time.sleep(1)
    return True

def search_contact(contact_name):
    """搜索联系人"""
    print(f"2. 搜索联系人: {contact_name}")
    
    # 按Ctrl+F打开搜索框（微信常用快捷键）
    press_key('Control_L+f')
    time.sleep(1)
    
    # 输入联系人名称
    type_text(contact_name)
    time.sleep(2)
    
    # 按回车选择第一个结果
    press_key('Return')
    time.sleep(1)
    
    return True

def send_message(message):
    """发送消息"""
    print(f"3. 发送消息: {message}")
    
    # 点击输入框（通常在最底部）
    screen = get_screen_info()
    input_x = screen['width'] // 2
    input_y = screen['height'] - 100
    
    click_at(input_x, input_y)
    time.sleep(0.5)
    
    # 输入消息
    type_text(message)
    time.sleep(1)
    
    # 发送消息（Ctrl+Enter或回车）
    press_key('Control_L+Return')
    time.sleep(0.5)
    
    # 备用：普通回车
    press_key('Return')
    time.sleep(1)
    
    return True

def send_thoughtful_message():
    """发送一些用心的消息"""
    messages = [
        "宝宝，你好呀！😊",
        "这是OpenClaw通过自动化发送的消息",
        "希望你能收到这份特别的问候",
        "科技让沟通变得更神奇了",
        "祝你今天心情愉快！✨",
        "来自AI的关心与问候"
    ]
    
    for msg in messages:
        send_message(msg)
        time.sleep(1)  # 每条消息间隔1秒
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("微信消息发送助手")
    print("目标：给联系人'宝宝'发送消息")
    print("=" * 60)
    
    print("\n⚠️ 注意：")
    print("1. 请确保微信窗口已打开并处于前台")
    print("2. 不要移动鼠标或操作键盘")
    print("3. 观察微信界面变化")
    
    # 倒计时
    for i in range(3, 0, -1):
        print(f"\r开始倒计时: {i}秒...", end="")
        time.sleep(1)
    print("\r开始执行操作...          ")
    
    try:
        # 步骤1：聚焦微信
        focus_wechat()
        
        # 步骤2：搜索"宝宝"
        search_contact("宝宝")
        
        # 步骤3：发送多条消息
        print("\n4. 发送多条消息...")
        send_thoughtful_message()
        
        print("\n" + "=" * 60)
        print("✅ 操作完成！")
        print("\n已发送的消息：")
        print("1. 宝宝，你好呀！😊")
        print("2. 这是OpenClaw通过自动化发送的消息")
        print("3. 希望你能收到这份特别的问候")
        print("4. 科技让沟通变得更神奇了")
        print("5. 祝你今天心情愉快！✨")
        print("6. 来自AI的关心与问候")
        
        print("\n请检查微信：")
        print("1. 是否成功发送给'宝宝'")
        print("2. 消息内容是否正确")
        print("3. 是否需要调整或发送更多")
        
    except Exception as e:
        print(f"\n❌ 操作出错: {e}")
        print("\n可能的原因：")
        print("1. 微信窗口未正确聚焦")
        print("2. 联系人'宝宝'未找到")
        print("3. 输入框位置不准确")
        
        print("\n建议：")
        print("1. 请手动点击微信窗口")
        print("2. 确认'宝宝'在联系人列表中")
        print("3. 告诉我具体问题，我可以调整")

if __name__ == "__main__":
    main()