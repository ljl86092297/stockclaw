#!/usr/bin/env python3
import subprocess
import time
import sys

def test_mouse_control():
    print("测试鼠标控制功能...")
    
    # 方法1：尝试使用xdotool（如果可用）
    try:
        # 获取当前鼠标位置
        result = subprocess.run(['xdotool', 'getmouselocation'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"xdotool可用，鼠标位置: {result.stdout}")
            return "xdotool"
    except FileNotFoundError:
        print("xdotool未安装")
    
    # 方法2：尝试使用xte（如果可用）
    try:
        result = subprocess.run(['xte'], capture_output=True, text=True)
        if result.returncode != 127:  # 127表示命令未找到
            print("xte可用")
            return "xte"
    except FileNotFoundError:
        print("xte未安装")
    
    # 方法3：尝试使用Python的pyautogui
    try:
        import pyautogui
        print("pyautogui可用")
        # 获取屏幕尺寸
        screen_width, screen_height = pyautogui.size()
        print(f"屏幕尺寸: {screen_width}x{screen_height}")
        
        # 获取当前鼠标位置
        current_x, current_y = pyautogui.position()
        print(f"当前鼠标位置: ({current_x}, {current_y})")
        
        return "pyautogui"
    except ImportError:
        print("pyautogui未安装")
    
    # 方法4：检查其他可能的工具
    tools = ['xinput', 'xset', 'xrandr']
    for tool in tools:
        try:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{tool}可用: {result.stdout.strip()}")
        except:
            pass
    
    return None

if __name__ == "__main__":
    available_tool = test_mouse_control()
    if available_tool:
        print(f"\n可用的鼠标控制工具: {available_tool}")
        print("建议安装的包:")
        print("1. xdotool - 功能强大的X11自动化工具")
        print("2. python3-pyautogui - Python鼠标/键盘控制库")
        print("3. x11-apps - X11相关工具集")
    else:
        print("\n未找到可用的鼠标控制工具")
        print("需要安装相关工具包")