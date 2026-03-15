#!/usr/bin/env python3
"""
最直接的微信打开方法：模拟用户鼠标操作
"""

import subprocess
import time
import os

def mouse_command(cmd_json):
    """执行鼠标命令"""
    try:
        result = subprocess.run(
            ['python3', 'openclaw_mouse_control.py', cmd_json],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip()
    except:
        return None

def press_key(key_combination):
    """按下按键组合"""
    keys = key_combination.split('+')
    for key in keys:
        mouse_command(f'{{"action": "key", "key": "{key}"}}')
        time.sleep(0.1)
    time.sleep(0.5)

def click_at(x, y):
    """在指定位置点击"""
    mouse_command(f'{{"action": "move", "x": {x}, "y": {y}}}')
    time.sleep(0.3)
    mouse_command('{"action": "click"}')
    time.sleep(0.5)

def type_text(text):
    """输入文本"""
    mouse_command(f'{{"action": "type", "text": "{text}"}}')
    time.sleep(1)

def get_screen_size():
    """获取屏幕尺寸"""
    # 默认值
    return {'width': 1920, 'height': 1080}

def method1_open_start_menu():
    """方法1：通过开始菜单打开"""
    print("方法1: 通过开始菜单打开微信")
    
    screen = get_screen_size()
    
    # 1. 按Win键打开开始菜单
    print("  按Win键打开开始菜单")
    press_key('Super_L')
    time.sleep(1)
    
    # 2. 输入"wechat"
    print("  搜索'wechat'")
    type_text('wechat')
    time.sleep(2)
    
    # 3. 按回车启动
    print("  按回车启动")
    press_key('Return')
    time.sleep(3)
    
    return True

def method2_desktop_shortcut():
    """方法2：点击桌面快捷方式"""
    print("方法2: 点击桌面快捷方式")
    
    screen = get_screen_size()
    
    # 假设微信快捷方式在桌面左上角区域
    print("  点击桌面空白处显示桌面")
    press_key('Super_L+d')  # Win+D显示桌面
    time.sleep(1)
    
    # 尝试点击常见位置
    shortcut_positions = [
        (100, 100),   # 左上角
        (200, 100),   # 稍右
        (100, 200),   # 稍下
        (150, 150),   # 中间
    ]
    
    for x, y in shortcut_positions:
        print(f"  尝试位置 ({x}, {y})")
        click_at(x, y)
        time.sleep(1)
        
        # 双击
        mouse_command('{"action": "click", "count": 2}')
        time.sleep(2)
    
    # 返回原窗口
    press_key('Super_L+d')
    time.sleep(1)
    
    return True

def method3_taskbar():
    """方法3：任务栏固定图标"""
    print("方法3: 任务栏固定图标")
    
    screen = get_screen_size()
    
    # 任务栏通常在底部
    taskbar_y = screen['height'] - 10
    
    # 从左到右扫描任务栏
    for x in range(100, screen['width'] - 100, 100):
        print(f"  扫描任务栏位置 x={x}")
        click_at(x, taskbar_y)
        time.sleep(0.5)
    
    return True

def method4_system_tray():
    """方法4：系统托盘（如果已运行）"""
    print("方法4: 系统托盘图标")
    
    screen = get_screen_size()
    
    # 系统托盘在右下角
    tray_x = screen['width'] - 50
    tray_y = screen['height'] - 50
    
    print(f"  点击系统托盘 ({tray_x}, {tray_y})")
    click_at(tray_x, tray_y)
    time.sleep(1)
    
    # 如果微信在托盘，可能在弹出菜单中
    # 尝试向上移动点击
    for y_offset in range(0, 200, 50):
        click_at(tray_x, tray_y - y_offset)
        time.sleep(0.5)
    
    return True

def method5_alt_tab():
    """方法5：Alt+Tab切换（如果已在后台）"""
    print("方法5: Alt+Tab切换")
    
    # 按Alt+Tab
    press_key('Alt_L+Tab')
    time.sleep(1)
    
    # 多次按Tab切换
    for _ in range(5):
        press_key('Tab')
        time.sleep(0.5)
    
    # 按回车选择
    press_key('Return')
    time.sleep(2)
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("微信直接启动 - 鼠标模拟操作")
    print("=" * 60)
    print(f"屏幕: {get_screen_size()['width']}x{get_screen_size()['height']}")
    print(f"DISPLAY: {os.environ.get('DISPLAY', ':0')}")
    print()
    
    print("⚠️ 注意：此操作将控制您的鼠标和键盘")
    print("请确保：")
    print("1. 不要移动鼠标")
    print("2. 不要操作键盘")
    print("3. 观察屏幕变化")
    print()
    
    input("按回车键开始（或Ctrl+C取消）...")
    
    methods = [
        ("开始菜单搜索", method1_open_start_menu),
        ("桌面快捷方式", method2_desktop_shortcut),
        ("任务栏图标", method3_taskbar),
        ("系统托盘", method4_system_tray),
        ("窗口切换", method5_alt_tab),
    ]
    
    print("\n" + "=" * 60)
    print("开始尝试各种方法...")
    
    for method_name, method_func in methods:
        print(f"\n▶ 尝试: {method_name}")
        print("-" * 40)
        
        try:
            if method_func():
                print(f"  ✓ {method_name} 执行完成")
            else:
                print(f"  ✗ {method_name} 可能未成功")
        except Exception as e:
            print(f"  ✗ {method_name} 出错: {e}")
        
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print("所有方法尝试完成！")
    print()
    print("请检查：")
    print("1. 微信窗口是否出现？")
    print("2. 任务栏是否有微信图标？")
    print("3. 系统托盘是否有微信？")
    print()
    print("如果微信已打开，我可以继续帮您：")
    print("1. 操作登录界面")
    print("2. 自动填写信息")
    print("3. 执行其他操作")
    print()
    print("如果未打开，请告诉我：")
    print("1. 您平时如何打开微信？")
    print("2. 微信图标在哪里？")
    print("3. 有什么错误信息？")

if __name__ == "__main__":
    main()